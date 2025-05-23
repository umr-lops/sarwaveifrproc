import logging
import os
import pytest
import xarray as xr
import hydra_zen
import hydra
from hydra import initialize, compose
from omegaconf import DictConfig,OmegaConf
import sarwaveifrproc
import onnxruntime
from sarwaveifrproc.l2_wave import generate_intermediate_product

# reference prediction is E01 (rmarquart January 2024), validated by L.Maillard
def get_hs_values(ff):
    ds = xr.open_dataset(ff, group="intraburst")
    return ds["hs_mean"].data

# expected outputs
subswathSAR = [
    os.path.join(
        os.path.dirname(sarwaveifrproc.__file__),
        "reference_data",
        # "s1a-iw2-slc-dv-20231128t035702-20231128t035727-051412-063451-e01.nc",
        # "l2-s1a-iw2-wav-dv-20220307t015815-20220307t015843-042209-0507b6-e11.nc"
        "l2-s1b-iw2-wav-dv-20210311t055224-20210311t055250-025963-0318d0-e11.nc"
    ),
]
# L1B_SAR_vh = [os.path.join(os.path.dirname(sarwaveifrproc.__file__),'reference_data','s1a-iw2-slc-vh-20231128t035702-20231128t035727-051412-063451-002_L1B_xspec_IFR_3.7.6nospectra.nc')]
L1B_SAR_vv = [
    os.path.join(
        os.path.dirname(sarwaveifrproc.__file__),
        "reference_data",
        # "s1a-iw2-slc-vv-20231128t035702-20231128t035727-051412-063451-005_L1B_xspec_IFR_3.7_nospectra.nc",
        "l1c-s1b-iw2-xsp-1sdv-20210311t055224-20210311t055250-025963-0318d0-b09.nc"
    )
]
hs_expected = []
for ii in subswathSAR:
    # hs_expected[ii] = get_hs_values(ff=ii)
    hs_expected.append(get_hs_values(ff=ii))


# @pytest.mark.parametrize(
#     "L1B_SAR_vv, hs_expected",
#     [(L1B_SAR_vv[0], hs_expected[0])],
# )
# def test_hs_prediction(L1B_SAR_vv, hs_expected):
#     from sarwaveifrproc.utils import load_config, load_models
#
#     ds = xr.open_dataset(
#         L1B_SAR_vv
#     )  # no group in this light l1B without interburst and without xspectra
#     conf = load_config()
#     predicted_variables = conf["predicted_variables"]
#     paths = {
#         "model_intraburst": conf["model_intraburst"],
#         "model_interburst": conf["model_interburst"],
#         "scaler_intraburst": conf["scaler_intraburst"],
#         "scaler_interburst": conf["scaler_interburst"],
#         "bins_intraburst": conf["bins_intraburst"],
#         "bins_interburst": conf["bins_interburst"],
#     }
#     logging.info("Loading models...")
#     (
#         model_intraburst,
#         model_interburst,
#         scaler_intraburst,
#         scaler_interburst,
#         bins_intraburst,
#         bins_interburst,
#     ) = load_models(paths, predicted_variables)
#     logging.info("Models loaded.")
#     # kept_variables = ['corner_longitude', 'corner_latitude', 'land_flag', 'sigma0_filt', 'normalized_variance_filt',
#     #                   'incidence', 'azimuth_cutoff', 'cwave_params']
#     kept_variables = []
#     dspredicted = sarwaveifrproc.l2_wave.generate_intermediate_product(
#         ds,
#         model_intraburst,
#         scaler_intraburst,
#         bins_intraburst,
#         predicted_variables,
#         kept_variables,
#     )
#     hs_actual = dspredicted["hs_mean"].data
#     logging.info("hs_actual %s", hs_actual)
#     logging.info("hs_expected %s", hs_expected)
#     mask_nan = np.isfinite(hs_expected)
#     diff = hs_actual[mask_nan] - hs_expected[mask_nan]
#     logging.info("diff : minimal %s maximal %s", diff.min(), diff.max())
#     assert np.allclose(hs_actual[mask_nan], hs_expected[mask_nan], atol=0.002)


@pytest.mark.parametrize(
    "L1B_SAR_vv, hs_expected",
    [(L1B_SAR_vv[0], hs_expected[0])],
)
def test_hs_prediction_E11(L1B_SAR_vv, hs_expected):
    # Manually initialize Hydra
    initialize(config_path="pkg://sarwave_config", version_base="1.3")
    cfg = compose(config_name="e11")
    models = cfg['models']
    xdt = xr.DataTree.from_dict(xr.open_groups(L1B_SAR_vv))
    logging.info("Loading models...")
    ort_mods = {k: onnxruntime.InferenceSession(d.path) for k, d in models.items()}
    mod_outs = {k: d.outputs for k, d in models.items()}
    logging.info("Models loaded.")
    predicted_variables = cfg['predicted_variables']
    kept_variables = cfg['kept_variables']
    ds_intraburst = generate_intermediate_product(
        xdt["intraburst"].ds,
        models=ort_mods,
        models_outputs=mod_outs,
        predicted_variables=predicted_variables.intraburst,
        kept_variables = kept_variables,
        pol='VV'
    )
    print('ds_intraburst',ds_intraburst)
    actual_hs_values = ds_intraburst["hs_mean"].data
    assert actual_hs_values==hs_expected

if __name__ == "__main__":
    import argparse
    import logging

    parser = argparse.ArgumentParser(description="testHsinference")
    parser.add_argument("--verbose", action="store_true", default=False)
    parser.add_argument(
        "--input",
        required=False,
        default=L1B_SAR_vv[0],
        help="path of the l1b measurement to test (s1a-iw2-slc-vv-20231128t035702-20231128t035727-051412-063451-005)",
    )
    args = parser.parse_args()
    fmt = "%(asctime)s %(levelname)s %(filename)s(%(lineno)d) %(message)s"
    if args.verbose:
        logging.basicConfig(
            level=logging.DEBUG, format=fmt, datefmt="%d/%m/%Y %H:%M:%S", force=True
        )
    else:
        logging.basicConfig(
            level=logging.INFO, format=fmt, datefmt="%d/%m/%Y %H:%M:%S", force=True
        )
    logging.info("start")
    test_hs_prediction_E11(args.input, hs_expected[0])
