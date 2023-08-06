# --------------------- AVIRIS-NG
# python ${ISOFIT_BASE}/utils/surfmodel.py --ncomp 8 --normalize --wavelengths ${ISOFIT_BASE}/examples/20170328_Ivanpah/20170320_ang20170228_wavelength_fit.txt  ${ISOFIT_BASE}/data/reflectance/surface_model_ucsb ${ISOFIT_BASE}/data/reflectance/surface_model_normalized.mat 

#python ${ISOFIT_BASE}/utils/surfmodel.py --ncomp 2 --normalize --decorrelate --wavelengths ${ISOFIT_BASE}/examples/20170328_Ivanpah/20170320_ang20170228_wavelength_fit.txt  ${ISOFIT_BASE}/data/reflectance/surface_model_ucsb ${ISOFIT_BASE}/data/reflectance/surface_model_normalized_loose.mat 

python ${ISOFIT_BASE}/utils/surfmodel.py --ncomp 8 --normalize --regularizer 1e-7 --wavelengths ${ISOFIT_BASE}/examples/20170328_Ivanpah/20170320_ang20170228_wavelength_fit.txt  ${ISOFIT_BASE}/data/reflectance/surface_model_ucsb ${ISOFIT_BASE}/data/reflectance/surface_model_normalized_strict.mat 

python ${ISOFIT_BASE}/utils/surfmodel.py --ncomp 8 --normalize --regularizer 1e-5 --wavelengths ${ISOFIT_BASE}/examples/20170328_Ivanpah/20170320_ang20170228_wavelength_fit.txt  ${ISOFIT_BASE}/data/reflectance/surface_model_ucsb ${ISOFIT_BASE}/data/reflectance/surface_model_normalized_noisy.mat 

#---------------------- AVIRIS-C
#python ${ISOFIT_BASE}/utils/surfmodel.py --regularizer 5e-5 --ncomp 4 --normalize --wavelengths ${ISOFIT_BASE}/examples/20160617_Sherpa/f160617_wavelengths_233chn.txt ${ISOFIT_BASE}/data/reflectance/surface_model_ucsb ${ISOFIT_BASE}/data/reflectance/surface_model_avirisc_normalized_233.mat 

#python ${ISOFIT_BASE}/utils/surfmodel.py --ncomp 8 --regularizer 1e-7 --normalize --wavelengths ${ISOFIT_BASE}/examples/20160617_Sherpa/f160617_wavelengths_233chn.txt ${ISOFIT_BASE}/data/reflectance/surface_model_ucsb ${ISOFIT_BASE}/data/reflectance/surface_model_avirisc_normalized_233_strict.mat 

#python ${ISOFIT_BASE}/utils/surfmodel.py --regularizer 5e-5 --ncomp 1 --normalize --wavelengths ${ISOFIT_BASE}/examples/20160617_Sherpa/f160617_wavelengths_233chn.txt ${ISOFIT_BASE}/data/reflectance/surface_model_ucsb ${ISOFIT_BASE}/data/reflectance/surface_model_avirisc_normalized_233.mat 

#python ${ISOFIT_BASE}/utils/surfmodel.py --ncomp 2 --normalize --decorrelate --solar_reflected --wavelengths ${ISOFIT_BASE}/examples/20171207_Fires/f171207t01p00r17_rdn_subs_233.txt ${ISOFIT_BASE}/data/reflectance/surface_model_ucsb ${ISOFIT_BASE}/data/reflectance/surface_model_avirisc_normalized_solref_233.mat 

#---------------------- PRISM
#python ${ISOFIT_BASE}/utils/surfmodel.py --ncomp 5 --normalize --wavelengths ${ISOFIT_BASE}/examples/20151026_SantaMonica/remote/20140221_PRISM_wavelengths_truncated_clip.txt ${ISOFIT_BASE}/data/reflectance/ocean_spectra ${ISOFIT_BASE}/data/reflectance/surface_model_prism_normalized.mat

#python ${ISOFIT_BASE}/utils/surfmodel.py --ncomp 1 --decorrelate --normalize --wavelengths ${ISOFIT_BASE}/examples/20151026_SantaMonica/remote/20140221_PRISM_wavelengths_truncated_clip.txt ${ISOFIT_BASE}/data/reflectance/ocean_spectra ${ISOFIT_BASE}/data/reflectance/surface_model_prism_normalized_loose.mat

#python ${ISOFIT_BASE}/utils/surfmodel.py --ncomp 2 --normalize --wavelengths ${ISOFIT_BASE}/examples/20151026_SantaMonica/remote/20140221_PRISM_wavelengths_truncated.txt ${ISOFIT_BASE}/data/reflectance/ocean_spectra ${ISOFIT_BASE}/data/reflectance/surface_model_prism_normalized_246.mat
