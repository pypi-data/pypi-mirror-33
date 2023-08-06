#
#  Copyright 2018 California Institute of Technology
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
# ISOFIT: Imaging Spectrometer Optimal FITting 
# Author: David R Thompson, david.r.thompson@jpl.nasa.gov
#

import json, os, sys, re
import scipy as s
from spectral.io import envi
from scipy.io import loadmat, savemat
from common import json_load_ascii, combos, VectorInterpolator 
from common import recursive_replace
from copy import deepcopy
from scipy.linalg import block_diag, det, norm, pinv, sqrtm, inv
from scipy.signal import convolve, gaussian, medfilt
from scipy.interpolate import interp1d
from scipy.optimize import minimize_scalar as min1d
from scipy.stats import multivariate_normal as mvn
import pylab as plt
import subprocess
import tensorflow as tf
import pylab as plt
import time

eps = 1e-5 # used for finite difference derivative calculations



class TensorFlowRT:
  """A model of photon transport including the atmosphere."""



  def __init__(self, config, instrument, geometry):

    self.instrument     = instrument
    self.geometry       = geometry
    self.wl             = instrument.wl
    self.fwhm           = instrument.fwhm

    self.statevec       = config['statevector']['names']
    self.bounds         = s.array(config['statevector']['bounds'])
    self.scale          = s.array(config['statevector']['scale'])
    self.init_val       = s.array(config['statevector']['init'])
    self.n_state        = len(self.statevec)

    # Input to neural network, can include state vector and metadata
    # It is always followed by the surface reflectance (per channel)
    self.inputvec       = config['inputvector']
    self.n_inputs       = len(self.inputvec)

    # Variables not retrieved
    self.bvec = ['Skyview','H2O_ABSCO']
    self.bval = s.array([config['skyview_uncertainty'],
                         config['h2o_abscoef_uncertainty']])

    # Define the TF variables
    self.tf_file  = config['model_file']
    self.D        = loadmat(self.tf_file)
    wldiffs       = abs(self.D['wl']-self.wl)
    if (wldiffs > eps).any():
      raise ValueError('model wavelengths do not match instrument')
    self.irr      = self.D['irr'] / 10.0  # Convert to uW/nm/sr/cm2

    # Build the tensorflow model from monochromatic subnetworks
    self.sess     = tf.Session()
    self.X        = tf.get_variable('X', len(self.wl)+self.n_inputs)
    self.y_pred   = tf.get_variable('y_pred',len(self.wl))

    # Define network variable weights and biases from the .mat file
    self.wIns, self.bIns, self.wHids, self.bHids, self.wOuts, self.bOuts = \
          [],[],[],[],[],[]
    for i in range(len(self.wl)):
      wIn_name, bIn_name   = 'wIn_%i'%i,  'bIn_%i'%i
      wHid_name, bHid_name = 'wHid_%i'%i, 'bHid_%i'%i
      wOut_name, bOut_name = 'wOut_%i'%i, 'bOut_%i'%i
      self.wIns.append(tf.get_variable(wIn_name, dtype='float32', 
            initializer=self.D[wIn_name]))
      self.bIns.append(tf.get_variable(bIn_name, dtype='float32', 
            initializer=self.D[bIn_name]))
      self.wHids.append(tf.get_variable(wHid_name, dtype='float32', 
            initializer=self.D[wHid_name]))
      self.bHids.append(tf.get_variable(bHid_name, dtype='float32', 
            initializer=self.D[bHid_name]))
      self.wOuts.append(tf.get_variable(wOut_name, dtype='float32', 
            initializer=self.D[wOut_name]))
      self.bOuts.append(tf.get_variable(bOut_name, dtype='float32', 
            initializer=self.D[bOut_name]))
      
    # Build the model - based on tutorial template, but must this really be
    # an embedded function
    def model(x):
      lyr_x, lyr_inp, lyr_hid, lyr_out = [],[],[],[]
      for i in range(len(self.wl)):

        # monochromatic subnetwork uses all of the atmosphere and the i-th
        # reflectance channel
        els = range(self.n_inputs)+[i]
        lyr_x.append(tf.reshape(tf.gather(x,els),[1, self.n_inputs+1]))

        # ReLu feedforward layer
        lyr_inp.append(tf.nn.relu(\
              tf.add(tf.matmul(lyr_x[i], self.wIns[i]), self.bIns[i])))

        # Second ReLu feedforward layer
        lyr_hid.append(tf.nn.relu(\
              tf.add(tf.matmul(lyr_inp[i], self.wHids[i]), self.bHids[i])))

        # Output is a linear mapping
        lyr_out.append(\
              tf.add(tf.matmul(lyr_hid[i], self.wOuts[i]), self.bOuts[i]))

      y = tf.stack(lyr_out)
      return y
    
    self.init_op = tf.global_variables_initializer()
    self.sess.run(self.init_op)
    self.model_op = model(self.X)
    self.y_pred = self.model_op

    # convert output from TOA reflectance to radiance
    self.irr_factor = self.irr/(geometry.sundist()**2)*geometry.coszen()/s.pi



  def xa(self):
    '''Mean of prior distribution, calculated at state x. This is the
       Mean of our LUT grid (why not).'''
    return self.init_val.copy()



  def Sa(self):
    '''Covariance of prior distribution. Our state vector covariance 
       is diagonal with very loose constraints.'''
    std_factor = 10.0 
    return s.diagflat(pow(s.diff(self.bounds) * std_factor,2))




  def get_aerosol(self, val):
    asym = [0.65 for q in self.aerosol_wl]
    return deepcopy(self.aerosol_wl), absc, extc, asym




  def calc_rdn(self, x_RT, rfl, Ls=None, meta=None):
    '''Calculate radiance at aperature for a radiative transfer state vector.
       rfl is the reflectance at surface. 
       Ls is the  emissive radiance at surface.'''

    tf_inp = s.zeros(self.n_inputs+len(self.wl)) 
    for i,name in enumerate(self.inputvec):
      if name in self.statevec:
        tf_inp[i] = x_RT[self.statevec.index(name)]
      elif meta is not None:
        # Can only get this input from metadata
        metav = 0
        if name == 'phi':
          relaz = abs(meta[1]-meta[3])
          if relaz>180:
            relaz = 360-relaz
          metav = relaz/360.0*2.0*s.pi # relative az, radians
        elif name == 'umu':
          metav = s.cos(meta[2]/360.0*2.0*s.pi) # cosine of to-sensor zenith
        tf_inp[i] = metav
      else:
        raise ValueError('State vector does not match NN. Needs metadata?')
    tf_inp[self.n_inputs:] = rfl
    feed_dict = {self.X: tf_inp}
    rho = s.squeeze(self.sess.run(self.y_pred, feed_dict=feed_dict))
    rdn = rho * self.irr_factor
    return s.squeeze(rdn)



  def estimate_Ls(self, x_RT, rfl, rdn, meta=None):
    """Estimate the surface emission for a given state vector and 
       reflectance/radiance pair"""
    Ls = zeros(len(rfl))
    return Ls



  def heuristic_atmosphere(self, rdn, meta=None):
    '''From a given radiance, estimate atmospheric state using band ratio
    heuristics.  Used to initialize gradient descent inversions.'''
    x = self.init_val 
    #rfl_est = 0.1 * s.ones(len(rdn)) #self.invert_algebraic(x, rdn, meta=meta)
    rfl_est =self.invert_algebraic(x, rdn, meta=meta)
    return x, rfl_est



  def invert_algebraic(self, x, rdn, Ls = None, meta=None):
    '''Inverts radiance algebraically to get a reflectance.
       Ls is the surface emission, if present'''
    nwl = len(self.wl)
    rdn_0   = self.calc_rdn(x, s.zeros(nwl), meta=meta)
    rdn_1   = self.calc_rdn(x, s.ones(nwl), meta=meta)
    est_rfl = (rdn-rdn_0)/(rdn_1-rdn_0)
   #rdn_0p5 = self.calc_rdn(x, 0.5*s.ones(nwl), meta=meta)
   #est_rfl = s.zeros(nwl) 
   #for i,r in enumerate(rdn):
   #  p = s.polyfit([rdn_0[i],rdn_0p5[i],rdn_1[i]],[0,0.5,1.0],1)
   #  est_rfl[i] = max([1e-4, s.polyval(p,r)])
    return est_rfl 



  def K_RT(self, x_RT, x_surface, rfl, d_rfl_d_surface, Ls, d_Ls_d_surface, 
      meta=None):
    """Jacobian of radiance with respect to RT and surface state vectors"""

    # first the radiance at the current state vector
    rdn = self.calc_rdn(x_RT, rfl, Ls=Ls, meta=meta)

    # perturb each element of the RT state vector (finite difference)
    K_RT = [] 
    for i in range(len(x_RT)):
      x_RT_perturb = x_RT.copy()
      x_RT_perturb[i] = x_RT[i] + eps
      rdne = self.calc_rdn(x_RT_perturb, rfl, Ls=Ls, meta=meta)
      K_RT.append((rdne-rdn) / eps)
    K_RT =  s.array(K_RT).T

    # analytical jacobians for surface model state vector, via chain rule
    # KLUDGE WARNING - should generalize/refine this!!!
    rdne = self.calc_rdn(x_RT, rfl+eps, Ls=Ls, meta=meta)
    d_rdn_d_rfl = (rdne-rdn) / eps
    K_surface = s.dot(s.diag(d_rdn_d_rfl), d_rfl_d_surface)

    return K_RT, K_surface



  def Kb_RT(self, x_RT, rfl, Ls=None, meta=None):
    """Jacobian of radiance with respect to NOT RETRIEVED RT and surface 
       state.  Right now, this is just the sky view factor."""

    return s.zeros((len(rfl),len(self.bvec)))

