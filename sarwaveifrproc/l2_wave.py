import numpy as np
import os
import xarray as xr
import datatree as dtt
from scipy import special
import sarwaveifrproc

attributes_missing_variables = \
{
    'sigma0_filt': {'long_name': 'calibrated sigma0 with BT correction', 'units': 'linear'},
    'normalized_variance_filt': {'long_name': 'normalized variance with BT correction', 'units': ''},
    'azimuth_cutoff': {'long_name': 'Azimuthal cut-off (2tau)', 'units': 'm'},
    'cwave_params': {'long_name': 'CWAVE parameters'},
    'k_gp': {'long_name': 'Gegenbauer polynoms dimension'},
    'phi_hf': {'long_name': 'Harmonic functions dimension (odd number)'}
}

def generate_l2_wave_product(xdt, intraburst_model, interburst_model, intraburst_scaler, interburst_scaler, intraburst_bins, interburst_bins, predicted_variables):
    """
    Generate a level-2 wave (L2 WAV) product.

    Parameters:
    - xdt (dict): DataTree containing intraburst and interburst datasets.
    - intraburst_model (tf.keras.Model): Machine learning model for intraburst predictions.
    - interburst_model (tf.keras.Model): Machine learning model for interburst predictions.
    - intraburst_scaler (Union[StandardScaler, MinMaxScaler, RobustScaler]): Scaler used for intraburst normalization.
    - interburst_scaler (Union[StandardScaler, MinMaxScaler, RobustScaler]): Scaler used for interburst normalization.
    - intraburst_bins (dict): Dictionary containing bins for intraburst variables.
    - interburst_bins (dict): Dictionary containing bins for interburst variables.
    - predicted_variables (list): List of predicted variable names.
    Returns:
    - l2_wave_product (dtt.DataTree): Level-2 wave product.
    
    Notes:
    - The scaler objects should be one of StandardScaler, MinMaxScaler, or RobustScaler from sklearn.preprocessing.
    """

    kept_variables = ['corner_longitude', 'corner_latitude', 'land_flag', 'sigma0_filt', 'normalized_variance_filt', 'incidence', 'azimuth_cutoff', 'cwave_params']
    ds_intraburst = generate_intermediate_product(xdt['intraburst'].ds, intraburst_model, intraburst_scaler, intraburst_bins, predicted_variables, kept_variables)
    ds_interburst = generate_intermediate_product(xdt['interburst'].ds, interburst_model, interburst_scaler, interburst_bins, predicted_variables, kept_variables)
    
    l2_wave_product = dtt.DataTree.from_dict({"intraburst": ds_intraburst, "interburst": ds_interburst})
    l2_wave_product.attrs['input_sar_product'] = os.path.basename(xdt.encoding['source'])
    return l2_wave_product


def generate_intermediate_product(ds, model, scaler, bins, predicted_variables, kept_variables):
    """
    Generate an intermediate l2 product, depending of the input dataset (intraburst or interburst).

    Parameters:
    - ds (xarray.Dataset): Input dataset.
    - model: Machine learning model for predicting sea parameters.
    - scaler: Scaler used for normalization.
    - bins (dict): Dictionary containing bins for each variable.
    - predicted_variables (list): List of predicted variable names.
    - kept_variables (list): List of variables from the input dataset that are kept in the final product.

    Returns:
    - ds_pred (xarray.Dataset): Intermediate predictions dataset.
    """
    
    if ds['land_flag'].all():
        return generate_product_on_land(ds, predicted_variables, kept_variables, bins)
    
    if '2tau' in ds.dims:
        ds = ds.squeeze(dim='2tau')
        ds.attrs['squeezed_dimensions']='2tau'
    
    tiles = ds[['sigma0_filt', 'normalized_variance_filt',  'incidence', 'azimuth_cutoff', 'cwave_params']]
    if 'burst' in ds.coords:
        tiles_stacked = tiles.stack(all_tiles = ['burst', 'tile_line','tile_sample'], k_phi = ['phi_hf', 'k_gp'])
    else:
        tiles_stacked = tiles.stack(all_tiles = ['tile_line','tile_sample'], k_phi = ['phi_hf', 'k_gp'])
            
    output_dims = [['all_tiles', f'{v}_mid'] for v in predicted_variables]
    inds = np.cumsum([0] + [len(bins[v]) -1 for v in predicted_variables])
    
    predictions = xr.apply_ufunc(predict_variables,
                                 tiles_stacked['sigma0_filt'], tiles_stacked['normalized_variance_filt'], tiles_stacked['incidence'], 
                                 tiles_stacked['azimuth_cutoff'], tiles_stacked['cwave_params'],
                                 model, scaler, inds,
                                 input_core_dims=[['all_tiles'], ['all_tiles'], ['all_tiles'], ['all_tiles'], ['all_tiles','k_phi'], [], [], []],
                                 output_core_dims=output_dims,
                                 vectorize=False)
    
    ds_pred = format_dataset(ds, predictions, predicted_variables, kept_variables, bins)
    
    return ds_pred

def generate_product_on_land(ds, predicted_variables, kept_variables, bins):
    """ 
    Patch function when input dataset does not contain all necessary variables.
    
    Parameters:
    - ds (xarray.Dataset): Input dataset.
    - predicted_variables (list): List of predicted variable names.
    - kept_variables (list): List of variables from the input dataset that are kept in the final product.
    - bins (dict): Dictionary containing bins for each variable.
    """
    ds = ds[['corner_longitude', 'corner_latitude', 'incidence', 'land_flag']]
    
    shape = ds['land_flag'].shape
    dims = ds['land_flag'].dims
    
    data_to_merge = []

    if set(predicted_variables).issubset(ds.keys()):
        kept_variables = kept_variables + predicted_variables
    
    for v in kept_variables:
        if v not in ds.variables:
            v_array = xr.DataArray(data = np.full(shape, np.nan), dims = dims).rename(v)
            v_array.attrs = attributes_missing_variables[v]
            data_to_merge.append(v_array)
            
    # Add CWAVES independently because the required dimensions are not in the input dataset when there is only land.
    k_gp = xr.DataArray(data=range(1, 5), dims='k_gp')
    k_gp.attrs = attributes_missing_variables['k_gp']
    phi_hf = xr.DataArray(data=range(1, 6), dims='phi_hf')
    phi_hf.attrs = attributes_missing_variables['phi_hf']
    
    cwaves = xr.DataArray(data=np.full(shape + (4, 5), np.nan), dims=dims + ('k_gp', 'phi_hf')).rename('cwave_params')
    cwaves.attrs = attributes_missing_variables['cwave_params']
    data_to_merge.append(cwaves.assign_coords({'k_gp': k_gp, 'phi_hf': phi_hf}))
    
    for v in predicted_variables:
        attributes = get_attributes(v)
        v_mid = xr.DataArray(data=(bins[v][:-1] + bins[v][1:])/2, dims=f'{v}_mid')
        v_mid.attrs = attributes['mid']
        
        v_pdf = xr.DataArray(data=np.full(v_mid.shape + shape, np.nan), dims=(f'{v}_mid', ) + dims).rename(f'{v}_pdf')
        v_pdf.attrs = attributes['pdf']
        data_to_merge.append(v_pdf.assign_coords({f'{v}_mid': v_mid}))
                
        v_mean = xr.DataArray(data=np.full(shape, np.nan), dims=dims).rename(f'{v}_mean')
        v_mean.attrs = attributes['mean']
        data_to_merge.append(v_mean)

        v_most_likely = xr.DataArray(data=np.full(shape, np.nan), dims=dims).rename(f'{v}_most_likely') 
        v_most_likely.attrs = attributes['most_likely']
        data_to_merge.append(v_most_likely)

        v_std = xr.DataArray(data=np.full(shape, np.nan), dims=dims).rename(f'{v}_std') 
        v_std.attrs = attributes['std']
        data_to_merge.append(v_std)
        
    ds = xr.merge([ds] + data_to_merge)                         
    
    ds.attrs.pop('name', None)
    ds.attrs.pop('multidataset', None)
    return ds

def predict_variables(sigma0, normalized_variance, incidence, azimuth_cutoff, cwave_params, model, scaler, indices):
    """
    Launch predictions using a neural model.

    Parameters:
    - sigma0 (xarray.DataArray): Array containing sigma0 values.
    - normalized_variance (xarray.DataArray): Array containing normalized variance values.
    - incidence (xarray.DataArray): Array containing incidence values.
    - azimuth_cutoff (xarray.DataArray): Array containing azimuth cutoff values.
    - cwave_params (xarray.DataArray): Array containing the cwave parameters.
    - model (tf.keras.Model): Machine learning model for predicting sea parameters.
    - scaler (Union[StandardScaler, MinMaxScaler, RobustScaler]): Scaler used for normalization.
    - indices (list): List of indices to segment predictions.

    Returns:
    - res (tuple): Tuple containing predictions for each variable.
    """   
    X_stacked = np.vstack([sigma0, normalized_variance, incidence, azimuth_cutoff]).T
    X_stacked = np.hstack([X_stacked, cwave_params])
    X_normalized = scaler.transform(X_stacked)
    
    predictions = model.predict(X_normalized)
    
    res = tuple(predictions[:, indices[i]:indices[i+1]] for i in range(len(indices)-1))
    
    return res

def format_dataset(ds, predictions, predicted_variables, kept_variables, bins):
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
    
    n = len(predicted_variables)
    for i in range(n):
        v = predicted_variables[i]
        attributes = get_attributes(v)
        v_mid = xr.DataArray(data = (bins[v][:-1] + bins[v][1:])/2, dims = f'{v}_mid')
        v_mid.attrs = attributes['mid']

        v_pdf = xr.apply_ufunc(lambda x: special.softmax(x, axis=1),
                               predictions[i]).rename(f'{v}_pdf').assign_coords({f'{v}_mid': v_mid}).to_dataset()
        v_pdf[f'{v}_pdf'].attrs = attributes['pdf']
        data_to_merge.append(v_pdf)
        
        v_mean = compute_values(v_pdf, v, compute_mean).rename(f'{v}_mean')
        v_mean.attrs = attributes['mean']
        data_to_merge.append(v_mean)
        
        v_most_likely = compute_values(v_pdf, v, get_most_likely).rename(f'{v}_most_likely')
        v_most_likely.attrs = attributes['most_likely']
        data_to_merge.append(v_most_likely)
        
        v_std = compute_values(v_pdf, v, compute_std, True).rename(f'{v}_std')
        v_std.attrs = attributes['std']
        data_to_merge.append(v_std)

    if set(predicted_variables).issubset(ds.keys()):
        kept_variables = kept_variables + predicted_variables
            
    data_to_merge = [ds.unstack() for ds in data_to_merge]
    ds = ds[kept_variables]
    
    ds = xr.merge([ds] + data_to_merge)
    ds = ds.drop_vars(['tile_line', 'tile_sample'])        
    ds.attrs['l2_processor_name'] = 'sarwaveifrproc'
    ds.attrs['l2_processor_version'] = sarwaveifrproc.__version__
    ds.attrs.pop('name', None)
    ds.attrs.pop('multidataset', None)
    
    return ds

def compute_values(ds, var, function, vectorize=False):
    """
    Compute values for the given variable using the given function.

    Args:
        ds (xr.Dataset): Dataset containing the data.
        var (str): Variable name.
        function (callable): Function to compute values.
        vectorize (bool): Whether to vectorize the computation.

    Returns:
        xr.DataArray: Computed values.
    """
    values = xr.apply_ufunc(function,
                            ds[f'{var}_mid'], ds[f'{var}_pdf'], 
                            input_core_dims=[[f'{var}_mid'],[f'{var}_mid']],
                            vectorize=vectorize)
    return values 

def get_attributes(var):
    """
    Generate a dictionary of attributes for a given variable.

    Parameters:
    - var (str): The variable name for which attributes are to be generated. This should correspond to keys in the `spec_dict`.

    Returns:
    - attributes (dict): A dictionary containing various attributes for the given variable.

    The function uses a predefined `spec_dict` to look up information about the variable.
    If the variable is not found in `spec_dict`, default attributes are generated with the variable name itself.
    """
    spec_dict = {
           'hs': {'long_name': 'significant wave height', 'units': 'm'},
           'phs0': {'long_name': 'wind sea significant wave height', 'units': 'm'},
           't0m1': {'long_name': 'mean wave period', 'units': 's'},
            }
    
    var_spec = spec_dict.get(var, {"long_name": f'{var}', 'units': ''})
    
    attributes = {
     'mid': {'long_name': f'central values of the bins used for discretizing the range of {var_spec["long_name"]} encountered during neural model training', 'units': var_spec['units']},
     'pdf': {'long name': f'{var_spec["long_name"]} discrete probability density function', 'units': 'probability'},
     'mean': {'long name': f'first-order moment of the {var_spec["long_name"]} discrete probability density function', 'units': var_spec['units']},
     'most_likely': {'long name': f'most likely value of {var_spec["long_name"]} given its discrete probability density function', 'units': var_spec['units']},
     'std': {'long name': f'square root of the second-order moment of the {var_spec["long_name"]} discrete probability density function', 'units': var_spec['units']}
    }
    
    return attributes

def get_most_likely(x, y):
    """
    Get the maximum of probability for each prediction.

    Args:
        x (np.ndarray): Input values.
        y (np.ndarray): Probabilities.

    Returns:
        np.ndarray: Most likely values.
    """
    i_max = np.argmax(y, axis=1)
    most_likely = x[i_max]
    return most_likely

def compute_mean(x, y):
    """
    Compute the expected value.

    Args:
        x (np.ndarray): Input values.
        y (np.ndarray): Probabilities.

    Returns:
        np.ndarray: Expected value.
    """
    return np.sum(x * y, axis=1)

def compute_std(x, y):
    """
    Compute the standard deviation.

    Args:
        x (np.ndarray): Input values.
        y (np.ndarray): Probabilities.

    Returns:
        np.ndarray: Standard deviation.
    """
    mean = np.sum(x * y)
    variance = np.sum(y * (x - mean) ** 2)
    return np.sqrt(variance)
