Release Notes (ver. 0.1.0)
==========================

*June 29, 2018*

We are very excited to share this release of ISOFIT with the community!

The routines and utilities in this codebase fit surface, atmosphere and instrument models to imaging spectrometer data using an Optimal Estimation (OE) approach.  This method can be used to perform atmospheric correction given a measured calibrated radiance file, either as a single spectra text file or as an imaging spectrometer data cube.

As this is still an early release of the code, please be aware of the following notes:

Included Examples
-----------------

For now, we have only included examples of individual radiance spectra in text format. These spectra were collected by JPL's Airborne Visible/Infrared Imaging Spectrometer Next Generation (AVIRIS-NG) instrument over Pasadena on 11/8/2017.  The measured radiance files can found in the "examples/20171108_Pasadena/remote" folder and the full config files for running the retrieval can be found in the "examples/20171108_Pasadena/configs" folder.

Supported Radiative Transfer Codes
----------------------------------

The ISOFIT code was built for flexibility and allows for different implementations of radiative transfer codes including open-source options like LibRadTran.  However, at the time of this release, only MODTRAN 6.0 is supported.

Roadmap
-------

Here are some of the things we currently have in mind for future releases:

* FEATURES
    * Implement LibRadTran for complete open-source solution
    * Apply neural network implementation to emulate radiative transfer
* ENHANCEMENTS
    * Optimize run time of code for improved performance
    * Remove dependency on "spectral" package
* TASKS
    * Implement unit tests
    * Augment documentation

Known Issues
------------

Issues to be added as discovered.  See the `issue tracker <https://github.com/davidraythompson/isofit/issues>`_ for more details.