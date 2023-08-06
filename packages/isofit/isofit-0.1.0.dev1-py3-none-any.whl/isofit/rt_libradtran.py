#! /usr/bin/env python3
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

import json
import os
import re
import scipy as s
from common import json_load_ascii, combos, VectorInterpolator
from common import recursive_replace
from copy import deepcopy
from scipy.interpolate import interp1d
from rt_lut import TabularRT
from wl2flt import generateFiltFile

eps = 1e-5  # used for finite difference derivative calculations


class LibRadTranRT(TabularRT):
    """A model of photon transport including the atmosphere."""

    def __init__(self, config, instrument):

        TabularRT.__init__(self, config, instrument)

        self.libradtran_dir = config['libradtran_directory']
        self.libradtran_template = config['libradtran_template_file']
        self.solzen = config['solar_zenith_angle']
        self.wl2flt = config['gen_filter_exe']
        self.filtpath = config['filter_file']
        self.solarpath = config['solar_file']
        self.solar_source_path = config['solar_source_file']
        self.albs = [0, 0.5, 1.0]

        if 'aerosol_model_file' in config:
            self.aerosol_model_file = config['aerosol_model_file']
            self.aerosol_template = config['aerosol_template_file']
            self.build_aerosol_model()

        # Build the lookup table
        self.build_lut(instrument)

    def load_chn(self, infile, coszen):
        """Load a .chn output file and parse critical coefficient vectors.  
           These are:
             wl      - wavelength vector
             sol_irr - solar irradiance
             sphalb  - spherical sky albedo at surface
             transm  - diffuse and direct irradiance along the 
                          sun-ground-sensor path
             transup - transmission along the ground-sensor path only 
           We parse them one wavelength at a time."""

        with open(infile) as f:
            sols, transms, sphalbs, wls, rhoatms, transups = [], [], [], [], [], []
            lines = f.readlines()
            for i, line in enumerate(lines):
                if i < 5:
                    continue
                toks = line.strip().split(' ')
                toks = re.findall(r"[\S]+", line.strip())
                wl, wid = float(toks[0]), float(toks[8])  # nm
                solar_irr = float(toks[18]) * 1e6 * \
                    s.pi / wid / coszen  # uW/nm/sr/cm2
                rdnatm = float(toks[4]) * 1e6  # uW/nm/sr/cm2
                rhoatm = rdnatm * s.pi / (solar_irr * coszen)
                sphalb = float(toks[23])
                transm = float(toks[22]) + float(toks[21])
                transup = float(toks[24])
                sols.append(solar_irr)
                transms.append(transm)
                sphalbs.append(sphalb)
                rhoatms.append(rhoatm)
                transups.append(rhoatm)
                wls.append(wl)
        params = [s.array(i) for i in
                  [wls, sols, rhoatms, transms, sphalbs, transups]]
        return tuple(params)

    def get_aerosol(self, val):
        asym = [0.65 for q in self.aerosol_wl]
        return deepcopy(self.aerosol_wl), absc, extc, asym

    def modtran_driver(self, overrides):
        """Write a MODTRAN 6.0 input file"""

        param = deepcopy(json_load_ascii(self.modtran_template)['MODTRAN'])

        # Basic aerosol template
        if 'VIS' in overrides.keys() or 'AERTYPE' in overrides.keys():
            aerosol_template = deepcopy(json_load_ascii(self.aerosol_template))
            param[0]['MODTRANINPUT']['AEROSOLS'] = aerosol_template

        # Other overrides
        for key, val in overrides.items():
            recursive_replace(param, key, val)
            if key == 'AERTYPE':
                wl, absc, extc, asym = [list(q) for q in self.get_aerosol(val)]
                param[0]['MODTRANINPUT']['AEROSOLS']['IREGSPC'][0]['NARSPC'] = len(
                    wl)
                param[0]['MODTRANINPUT']['AEROSOLS']['IREGSPC'][0]['VARSPC'] = wl
                param[0]['MODTRANINPUT']['AEROSOLS']['IREGSPC'][0]['EXTC'] = extc
                param[0]['MODTRANINPUT']['AEROSOLS']['IREGSPC'][0]['ABSC'] = absc
                param[0]['MODTRANINPUT']['AEROSOLS']['IREGSPC'][0]['ASYM'] = asym
            if key == 'FILTNM':
                param[0]['MODTRANINPUT']['SPECTRAL']['FILTNM'] = val
            if key in ['ITYPE', 'H1ALT', 'IDAY', 'IPARM', 'PARM1', 'PARM2', 'GMTIME',
                       'TRUEAZ', 'OBSZEN']:
                param[0]['MODTRANINPUT']['GEOMETRY'][key] = val

        return json.dumps({"MODTRAN": param})

    def build_aerosol_model(self):
        aer_data = s.loadtxt(self.aerosol_model_file)
        self.aer_wl = aer_data[:, 0]
        aer_data = aer_data[:, 1:].T
        self.naer = len(aer_data)/2
        self.aer_grid = s.linspace(0, 1, self.naer)
        self.aer_asym = s.ones(len(self.aer_wl)) * 0.65  # heuristic
        aer_absc, aer_extc = [], []
        for i in range(self.naer):
            aer_extc.append(aer_data[i*2])
            aer_ssa = aer_data[i*2+1]
            aer_absc.append(aer_extc[-1] * (1.0 - aer_ssa))
        self.aer_absc = s.array(aer_absc)
        self.aer_extc = s.array(aer_extc)
        self.aer_absc_interp, self.aer_extc_interp = [], []
        for i in range(len(self.aer_wl)):
            self.aer_absc_interp.append(
                interp1d(self.aer_grid, self.aer_absc[:, i]))
            self.aer_extc_interp.append(
                interp1d(self.aer_grid, self.aer_extc[:, i]))

    def get_aerosol(self, val):
        """ Interpolation in lookup table """

        extc = s.array([p(val) for p in self.aer_extc_interp])
        absc = s.array([p(val) for p in self.aer_absc_interp])
        return self.aer_wl, absc, extc, self.aer_asym

    def build_lut(self, instrument, rebuild=False):
        """ Each LUT is associated with a source directory.  We build a 
            lookup table by: 
              (1) defining the LUT dimensions, state vector names, and the grid 
                  of values; 
              (2) running libradtran if needed, with each run defining one of 
                  three albedo values, used together to calculate the atmospheric
                  optical properties at each point in the LUT; and
                  different point in the LUT; and 
              (3) loading the LUTs, one per key atmospheric coefficient vector,
                  into memory as VectorInterpolator objects."""

        # Regenerate input filter file
        if not os.path.exists(self.filtpath):
            generateFiltFile(self, instrument.wavelength_file, self.filtpath)

        # Regenerate input solar file
        if not os.path.exists(self.solar_path):
            generateFiltFile(self, instrument.wavelength_file, self.solar_path)

        TabularRT.build_lut(self, instrument, rebuild)

    def rebuild_cmd(self, point, fn):

        vals = dict([(n, v) for n, v in zip(self.lut_names, point)])
        vals['DISALB'] = True
        vals['NAME'] = fn
        vals['FILTNM'] = self.filtpath
        modtran_config_str = self.modtran_driver(dict(vals))

        # Check rebuild conditions: LUT is missing or from a different config
        infilename = 'LUT_'+fn+'.json'
        infilepath = os.path.join(self.lut_dir, infilename)
        outchnname = fn+'.chn'
        outchnpath = os.path.join(self.lut_dir, outchnname)
        if not os.path.exists(infilepath) or\
           not os.path.exists(outchnpath):
            rebuild = True
        else:
            with open(infilepath, 'r') as f:
                current = f.read()
                rebuild = (modtran_config_str.strip() != current.strip())

        if not rebuild:
            raise ValueError('File exists')

        # write_config_file
        with open(infilepath, 'w') as f:
            f.write(modtran_config_str)

        cmd = self.modtran_dir+'/bin/macos/mod6c_cons '+infilename
        return cmd

    def load_rt(self, point, fn):
        for alb in self.albs:
            outfile = self.lut_dir+'/'+fn+'_albedo-%4.2f.out'
            X = s.loadtxt(outfile)
            wl, rdn, irr, sphalb = X.T
            rho = rdn / irr * s.pi

        solzen = self.load_output(outfile)
        coszen = s.cos(solzen * s.pi / 180.0)
        chnfile = self.lut_dir+'/'+fn+'.chn'
        wl, sol, rhoatm, transm, sphalb, transup = self.load_chn(
            chnfile, coszen)
        return wl, sol, solzen, rhoatm, transm, sphalb, transup
