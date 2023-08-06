ISOFIT Code and File Formats
============================

This section presents a high-level introduction to the main ISOFIT modules and utilities as well as a description of the file format used to run the examples.

isofit/
-------

The main ISOFIT codebase is located in the top-level "isofit/" directory.  In this directory you will find the following modules:

* isofit.py - Top level executable used to perform surface and atmosphere fitting on individual spectra or imaging spectroscopy data cubes.
* inverse.py - Inversion via Rodgers et al. optimal estimation.
* forward.py - Forward model that calculates radiance at sensor from a state vector.
* geometry.py - Geometry metadata for a single spectrum.
* instrument.py - Instrument model including noise models.
* rt_*.py - Different radiative transfer options.
* surf_*.py - Different surface model options suitable for water, land, and (potentially) burning emissive objects.

utils/
------

The scripts in this folder are standalone general purpose utilities outside of the "isofit" package.  They are very much "in development" and may require some extra care to use.

Config Files
------------

Each example spectrum requires a well-formatted JSON config file in order to run properly.  Several example config files have been provided in the "examples/20171108_Pasadena/configs".  Below is an explanation of the fields in each (field names are in bold):

* **ISOFIT_BASE**: *Path to the root directory of the isofit installation*
    * **input**:
        * **measured_radiance_file**:
        * **reference_reflectance_file**:
    * **output**:
        * **estimated_reflectance_file**:
        * **algebraic_inverse_file**:
        * **modeled_radiance_file**:
        * **data_dump_file**:
        * **posterior_errors_file**:
    * **forward_model**:
        * **instrument**:
            * **wavelength_file**:
            * **unknowns**:
                * **cal_uncertainty_systematic_file**:
                * **cal_uncertainty_flatfield**:
            * **integrations**:
            * **noise_file**:
        * **multicomponent_surface**:
            * **surface_file**:
        * **modtran_radiative_transfer**:
            * **lut_path**:
            * **aerosol_template_file**:
            * **aerosol_model_file**:
            * **wl2flt_exe**:
            * **modtran_template_file**:
            * **domain**:
                * **start**:
                * **end**:
                * **step**:
            * **statevector**:
            * **H2OSTR**:
                * **bounds**:
                * **scale**:
                * **init**:
            * **AOT550**:
                * **bounds**:
                * **scale**:
                * **init**:
            * **lut_grid**:
                * **H2OSTR**:
                * **AOT550**:
            * **unknowns**:
                * **H2O_ABSCO**:
    * **inversion**:
        * **windows**: