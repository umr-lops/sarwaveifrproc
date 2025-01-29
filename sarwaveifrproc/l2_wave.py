import numpy as np
import os
import xarray as xr
from scipy import special
import sarwaveifrproc

attributes_missing_variables = {
    "sigma0_filt": {
        "long_name": "calibrated sigma0 with BT correction",
        "units": "linear",
    },
    "normalized_variance_filt": {
        "long_name": "normalized variance with BT correction",
        "units": "",
    },
    "azimuth_cutoff": {"long_name": "Azimuthal cut-off (2tau)", "units": "m"},
    "cwave_params": {"long_name": "CWAVE parameters"},
    "k_gp": {"long_name": "Gegenbauer polynoms dimension"},
    "phi_hf": {"long_name": "Harmonic functions dimension (odd number)"},
}


def generate_l2_wave_product(xdt, models, models_outputs, predicted_variables):
    """
    Generate a level-2 wave (L2 WAV) product.

    Parameters:
    - xdt (dict): DataTree containing intraburst and interburst datasets.
    - models (dict[str, onnxruntime.InferenceSession): different ml models used
    - models_outputs (dict[str, list]): list of variables predicted by each model
    - predicted_variables (dict[dict]):  variables to add to the product and corresponding model and output name
    Returns:
    - l2_wave_product (xr.DataTree): Level-2 wave product.

    Notes:
    - The scaler objects should be one of StandardScaler, MinMaxScaler, or RobustScaler from sklearn.preprocessing.
    """

    kept_variables = [
        "corner_longitude",
        "corner_latitude",
        "land_flag",
        "sigma0_filt",
        "normalized_variance_filt",
        "incidence",
        "azimuth_cutoff",
        "cwave_params",
    ]
    intraburst_models = {
        k: m
        for k, m in models.items()
        if k in [v.model for v in predicted_variables.intraburst.values()]
    }
    interburst_models = {
        k: m
        for k, m in models.items()
        if k in [v.model for v in predicted_variables.interburst.values()]
    }
    ds_intraburst = generate_intermediate_product(
        xdt["intraburst"].ds,
        intraburst_models,
        models_outputs,
        predicted_variables.intraburst,
        kept_variables,
    )
    ds_interburst = generate_intermediate_product(
        xdt["interburst"].ds,
        interburst_models,
        models_outputs,
        predicted_variables.interburst,
        kept_variables,
    )

    l2_wave_product = xr.DataTree.from_dict(
        {"intraburst": ds_intraburst, "interburst": ds_interburst}
    )
    l2_wave_product.attrs["input_sar_product"] = os.path.basename(
        xdt.encoding["source"]
    )
    return l2_wave_product


def generate_intermediate_product(
    ds, models, models_outputs, predicted_variables, kept_variables, pol="VV"
):
    """
    Generate an intermediate l2 product, depending of the input dataset (intraburst or interburst).

    Parameters:
    - ds (xarray.Dataset): Input dataset.
    - models (dict[str, onnxruntime.InferenceSession): different ml models used
    - models_outputs (dict[str, list]): list of variables predicted by each model
    - predicted_variables (dict[dict]):  variables to add to the product and corresponding model and output name
    - kept_variables (list): List of variables from the input dataset that are kept in the final product.
    - pol (str): polarisation to select

    Returns:
    - ds_pred (xarray.Dataset): Intermediate predictions dataset.
    """

    if ds["land_flag"].all():
        return generate_product_on_land(ds, predicted_variables, kept_variables)

    if "2tau" in ds.dims:
        ds = ds.squeeze(dim="2tau")
        ds.attrs["squeezed_dimensions"] = "2tau"

    tiles = ds[
        [
            "sigma0_filt",
            "normalized_variance_filt",
            "incidence",
            "azimuth_cutoff",
            "cwave_params",
        ]
    ].sel(pol=pol)
    if "burst" in ds.coords:
        tiles_stacked = tiles.stack(
            all_tiles=["burst", "tile_line", "tile_sample"], k_phi=["k_gp", "phi_hf"]
        )
    else:
        tiles_stacked = tiles.stack(
            all_tiles=["tile_line", "tile_sample"], k_phi=["k_gp", "phi_hf"]
        )

    output_dims = [["preds", "all_tiles"]]

    predictions = xr.concat(
        [
            xr.apply_ufunc(
                predict_variables,
                tiles_stacked["sigma0_filt"],
                tiles_stacked["normalized_variance_filt"],
                tiles_stacked["incidence"],
                tiles_stacked["azimuth_cutoff"],
                tiles_stacked["cwave_params"],
                model,
                input_core_dims=[
                    ["all_tiles"],
                    ["all_tiles"],
                    ["all_tiles"],
                    ["all_tiles"],
                    ["all_tiles", "k_phi"],
                    [],
                ],
                output_core_dims=output_dims,
                vectorize=False,
            ).assign_coords(preds=[f"{k}_{o}" for o in models_outputs[k]])
            for (k, model) in models.items()
        ],
        dim="preds",
    )

    ds_pred = format_dataset(ds, predictions, predicted_variables, kept_variables)

    return ds_pred


def generate_product_on_land(ds, predicted_variables, kept_variables):
    """
    Patch function when input dataset does not contain all necessary variables.

    Parameters:
    - ds (xarray.Dataset): Input dataset.
    - predicted_variables (list): List of predicted variable names.
    - kept_variables (list): List of variables from the input dataset that are kept in the final product.
    - bins (dict): Dictionary containing bins for each variable.
    """
    ds = ds[["corner_longitude", "corner_latitude", "incidence", "land_flag"]]

    shape = ds["land_flag"].shape
    dims = ds["land_flag"].dims

    data_to_merge = []

    if set(predicted_variables).issubset(ds.keys()):
        kept_variables = kept_variables + predicted_variables

    for v in kept_variables:
        if v not in ds.variables:
            v_array = xr.DataArray(data=np.full(shape, np.nan), dims=dims).rename(v)
            v_array.attrs = attributes_missing_variables[v]
            data_to_merge.append(v_array)

    # Add CWAVES independently because the required dimensions are not in the input dataset when there is only land.
    k_gp = xr.DataArray(data=range(1, 5), dims="k_gp")
    k_gp.attrs = attributes_missing_variables["k_gp"]
    phi_hf = xr.DataArray(data=range(1, 6), dims="phi_hf")
    phi_hf.attrs = attributes_missing_variables["phi_hf"]

    cwaves = xr.DataArray(
        data=np.full(shape + (4, 5), np.nan), dims=dims + ("k_gp", "phi_hf")
    ).rename("cwave_params")
    cwaves.attrs = attributes_missing_variables["cwave_params"]
    data_to_merge.append(cwaves.assign_coords({"k_gp": k_gp, "phi_hf": phi_hf}))

    for v, vd in predicted_variables.items():
        attributes = vd.attrs
        preds = xr.DataArray(data=np.full(shape, np.nan), dims=dims).rename(v)
        preds.attrs = attributes
        data_to_merge.append(preds)

    ds = xr.merge([ds] + data_to_merge)

    ds.attrs.pop("name", None)
    ds.attrs.pop("multidataset", None)
    return ds


def predict_variables(
    sigma0, normalized_variance, incidence, azimuth_cutoff, cwave_params, model
):
    """
    Launch predictions using a neural model.

    Parameters:
    - sigma0 (xarray.DataArray): Array containing sigma0 values.
    - normalized_variance (xarray.DataArray): Array containing normalized variance values.
    - incidence (xarray.DataArray): Array containing incidence values.
    - azimuth_cutoff (xarray.DataArray): Array containing azimuth cutoff values.
    - cwave_params (xarray.DataArray): Array containing the cwave parameters.
    - model (tf.keras.Model): Machine learning model for predicting sea parameters.

    Returns:
    - res (tuple): Tuple containing predictions for each variable.
    """
    X_stacked = np.vstack([sigma0, normalized_variance, incidence, azimuth_cutoff]).T
    X_stacked = np.hstack([cwave_params, X_stacked])
    # X_normalized = scaler.transform(X_stacked)

    input_name = model.get_inputs()[0].name
    inputs = {input_name: X_stacked.astype(np.float32)}

    res = model.run(None, inputs)
    res = [r[:, i] for r in res for i in range(r.shape[-1])]
    return res


def format_dataset(ds, predictions, predicted_variables, kept_variables):
    """
    Format a dataset based on predictions, variables, and bins.

    Parameters:
    - ds (xarray.Dataset): Input dataset (l1b or l1c).
    - predictions (list): Predictions for each variable.
    - predicted_variables (list): List of predicted variable names.
    - kept_variables (list): List of variables from the input dataset that are kept in the final product.
    - bins (dict): Dictionary containing bin values for each variable.

    Returns:
    - ds_pred (xarray.Dataset): Formatted dataset with predictions and original data.

    The function computes various statistical values (mean, most likely, standard deviation)
    from the predictions and adds them to the new dataset. It also includes original data
    from the input dataset and some additional attributes.
    """

    data_to_merge = []

    for v, vd in predicted_variables.items():
        attributes = vd.attrs
        preds = predictions.sel(preds=f"{vd.model}_{vd.output}", drop=True).rename(v)
        preds.attrs = attributes
        data_to_merge.append(preds)

    if set(predicted_variables).issubset(ds.keys()):
        kept_variables = kept_variables + predicted_variables

    data_to_merge = [ds.unstack() for ds in data_to_merge]
    ds = ds[kept_variables]

    ds = xr.merge([ds] + data_to_merge)
    ds = ds.drop_vars(["tile_line", "tile_sample"])
    ds.attrs["l2_processor_name"] = "sarwaveifrproc"
    ds.attrs["l2_processor_version"] = sarwaveifrproc.__version__
    ds.attrs.pop("name", None)
    ds.attrs.pop("multidataset", None)

    return ds
