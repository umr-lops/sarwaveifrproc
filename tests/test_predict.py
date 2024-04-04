import numpy as np
import pytest
import xarray as xr
import os
import logging
import sarwaveifrproc
# reference prediction is E01 (rmarquart January 2024), validated by L.Maillard
def get_hs_values(ff):
    ds=xr.open_dataset(ff,group='intraburst')
    return ds['hs_mean'].data
subswathSAR=[os.path.join(os.path.dirname(sarwaveifrproc.__file__),'reference_data',
                          's1a-iw2-slc-dv-20231128t035702-20231128t035727-051412-063451-e01.nc'),
                       ]
# L1B_SAR_vh = [os.path.join(os.path.dirname(sarwaveifrproc.__file__),'reference_data','s1a-iw2-slc-vh-20231128t035702-20231128t035727-051412-063451-002_L1B_xspec_IFR_3.7.6nospectra.nc')]
L1B_SAR_vv = [os.path.join(os.path.dirname(sarwaveifrproc.__file__),'reference_data',
            's1a-iw2-slc-vv-20231128t035702-20231128t035727-051412-063451-005_L1B_xspec_IFR_3.7.6nospectra.nc')]
hs_expected = []
for ii in subswathSAR:
    # hs_expected[ii] = get_hs_values(ff=ii)
    hs_expected.append(get_hs_values(ff=ii))

@pytest.mark.parametrize(
    "L1B_SAR_vv, hs_expected",
    [(L1B_SAR_vv[0],hs_expected[0])],
)
def test_hs_prediction(L1B_SAR_vv,hs_expected):
    from sarwaveifrproc.utils import  load_config,load_models
    ds = xr.open_dataset(L1B_SAR_vv) # no group in this light l1B without interburst and without xspectra
    conf = load_config()
    predicted_variables = conf['predicted_variables']
    paths = {
        'model_intraburst': conf['model_intraburst'],
        'model_interburst': conf['model_interburst'],
        'scaler_intraburst': conf['scaler_intraburst'],
        'scaler_interburst': conf['scaler_interburst'],
        'bins_intraburst': conf['bins_intraburst'],
        'bins_interburst': conf['bins_interburst'],
    }
    logging.info('Loading models...')
    (model_intraburst, model_interburst, scaler_intraburst, scaler_interburst,
     bins_intraburst, bins_interburst) = load_models(
        paths, predicted_variables)
    logging.info('Models loaded.')
    # kept_variables = ['corner_longitude', 'corner_latitude', 'land_flag', 'sigma0_filt', 'normalized_variance_filt',
    #                   'incidence', 'azimuth_cutoff', 'cwave_params']
    kept_variables = []
    dspredicted = sarwaveifrproc.l2_wave.generate_intermediate_product(ds,
                                                model_intraburst, scaler_intraburst,
                                                bins_intraburst,
                                                predicted_variables, kept_variables)
    hs_actual = dspredicted['hs_mean'].data
    logging.info('hs_actual %s',hs_actual)
    logging.info('hs_expected %s', hs_expected)
    mask_nan = np.isfinite(hs_expected)
    diff = hs_actual[mask_nan]-hs_expected[mask_nan]
    logging.info('diff : %s %s',diff.min(),diff.max())
    assert np.allclose(hs_actual[mask_nan],hs_expected[mask_nan],atol=0.1)


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)
    logging.info('start')
    test_hs_prediction(L1B_SAR_vv[0],hs_expected[0])
