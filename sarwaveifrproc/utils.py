import sarwaveifrproc
import tensorflow as tf
import datatree as dtt
import numpy as np
import glob
import logging
import yaml 
import pickle
import os
from datetime import datetime
from sarwaveifrproc.l2_wave import generate_l2_wave_product

def get_safe_date(safe):
    """
    Extracts and returns the date and time from a given SAFE directory name.

    Parameters:
        safe (str): SAFE directory name.

    Returns:
        datetime: A datetime object representing the extracted date and time.
    """
    date_str = safe.split('_')[5]
    date = datetime.strptime(date_str, '%Y%m%dT%H%M%S')
    return date

def get_output_safe(l1x_safe, root_savepath, tail='E00'):
    """
    Generates the final SAFE filename with specified modifications.

    Parameters:
        l1x_safe (str): The input SAFE path.
        root_savepath (str): The root path for saving the output.
        tail (str): The tail to append to the filename. Defaults to 'E00'.

    Returns:
        str: The output savepath.
        
    Raises:
        ValueError: If the input SAFE does not meet the filename requirements.
    """
    l1x_safe = l1x_safe.rstrip('/') # remove trailing slash
    safe = l1x_safe.split(os.sep)[-1]
    final_safe = safe
    
    if all((pattern in safe) for pattern in ['XSP_', '1SDV', '.SAFE']):
        
        date = get_safe_date(safe)

        final_safe = final_safe.replace('XSP_', 'WAV_')
        final_safe = final_safe.replace('1SDV', '2SDV')
        final_safe = final_safe.replace('.SAFE', f'_{tail.upper()}.SAFE')
        
        output_safe = os.path.join(root_savepath, date.strftime('%Y'), date.strftime('%j'), final_safe)

        return output_safe
    
    else:
        raise ValueError(f"The input SAFE does not meet the filename requirements.")
    
def get_output_filename(l1x_path, output_safe, tail='e00'):
    """
    Constructs and returns the file path for saving a processed file based on input parameters.
    
    Parameters:
        l1x_path (str): The path to the input file. It can be either a L1B or L1C file.
        root_savepath (str): The root directory where the processed file will be saved.
        tail (str, optional): The tail string to be appended to the filename corresponding to the processing options. Defaults to 'e00'.
        
    Returns:
        str: File path for saving the processed file.
    """
    filename = l1x_path.split(os.sep)[-1]
    filename_exploded = filename.split('-')
    final_filename = '-'.join([*filename_exploded[:3], 'dv', *filename_exploded[4:-1], f'{tail.lower()}.nc'])
    
    savepath = os.path.join(output_safe, final_filename)
    return savepath

def load_config():
    """

    Returns:
        conf: dict
    """
    local_config_path = os.path.join(os.path.dirname(sarwaveifrproc.__file__), 'localconfig.yaml')

    if os.path.exists(local_config_path):
        config_path = local_config_path
    else:
        config_path = os.path.join(os.path.dirname(sarwaveifrproc.__file__), 'config.yaml')
        
    logging.info('config path: %s', config_path)
    stream = open(config_path, 'r')
    conf = yaml.load(stream, Loader=yaml.CLoader)
    return conf


def load_models(paths, predicted_variables):
    """
    Loads models, scalers, and bins necessary for prediction.

    Parameters:
    paths (dict): Dictionary containing paths to model files, scaler files, and bin files.
        Keys:
            - 'model_intraburst': Path to the intraburst model file.
            - 'model_interburst': Path to the interburst model file.
            - 'scaler_intraburst': Path to the intraburst scaler file.
            - 'scaler_interburst': Path to the interburst scaler file.
            - 'bins_intraburst': Path to the intraburst bins directory.
            - 'bins_interburst': Path to the interburst bins directory.
    predicted_variables (list): List of variable names to be predicted.

Returns:
    tuple: Tuple containing the following items:
        - model_intraburst (tf.keras.Model): Intraburst model loaded from the provided path.
        - model_interburst (tf.keras.Model): Interburst model loaded from the provided path.
        - scaler_intraburst (RobustScaler): Intraburst scaler loaded from the provided path.
        - scaler_interburst (RobustScaler): Interburst scaler loaded from the provided path.
        - bins_intraburst (dict): Dictionary containing intraburst bins for each predicted variable.
        - bins_interburst (dict): Dictionary containing interburst bins for each predicted variable.
    """    
    # Unpack paths
    path_model_intraburst, path_model_interburst, path_scaler_intraburst, path_scaler_interburst, path_bins_intraburst, path_bins_interburst = paths.values()
    
    # Load models and scalers using paths provided
    model_intraburst = tf.keras.models.load_model(path_model_intraburst, compile=False)
    scaler_intraburst_array = np.load(path_scaler_intraburst)
    scaler_intraburst = RobustScaler(medians=scaler_intraburst_array[0], iqrs=scaler_intraburst_array[1])    
    
    model_interburst = tf.keras.models.load_model(path_model_interburst, compile=False)
    scaler_interburst_array = np.load(path_scaler_interburst)
    scaler_interburst = RobustScaler(medians=scaler_interburst_array[0], iqrs=scaler_interburst_array[1]) 
    
    bins_intraburst = {f'{var}': np.load(os.path.join(path_bins_intraburst, f'bins_{var}.npy')) for var in predicted_variables}
    bins_interburst = {f'{var}': np.load(os.path.join(path_bins_interburst, f'bins_{var}.npy')) for var in predicted_variables}

    return model_intraburst, model_interburst, scaler_intraburst, scaler_interburst, bins_intraburst, bins_interburst
    
    
def process_files(input_safe, output_safe, model_intraburst, model_interburst, scaler_intraburst, scaler_interburst, bins_intraburst, bins_interburst, predicted_variables, product_id):
    """
    Processes files in the input directory, generates predictions, and saves results in the output directory.

    Parameters:
        input_safe (str): Input safe path.
        output_safe (str): Path to the directory where output data will be saved.
        model_intraburst (tf.keras.Model): Intraburst model for prediction.
        model_interburst (tf.keras.Model): Interburst model for prediction.
        scaler_intraburst (RobustScaler): Scaler for intraburst data.
        scaler_interburst (RobustScaler): Scaler for interburst data.
        bins_intraburst (dict): Dictionary containing intraburst bins for each predicted variable.
        bins_interburst (dict): Dictionary containing interburst bins for each predicted variable.
        predicted_variables (list): List of variable names to be predicted.
        product_id (str): Identifier for the output product.

    Returns:
        None
    """
    subswath_filenames = glob.glob(os.path.join(input_safe, '*-?v-*.nc'))
    logging.info(f'{len(subswath_filenames)} subswaths found in given safe.')
    
    for path in subswath_filenames:
        xdt = dtt.open_datatree(path)
        l2_product = generate_l2_wave_product(xdt, model_intraburst, model_interburst, scaler_intraburst, scaler_interburst, bins_intraburst, bins_interburst, predicted_variables)

        os.makedirs(output_safe, exist_ok=True)
        savepath = get_output_filename(path, output_safe, product_id)
        l2_product.to_netcdf(savepath)
        
    
class RobustScaler:
    """
    Class to mimic scikit-learn RobustScaler. This is done in order to prevent warning messages when using pickle to load the scikit-learn scaler.
    """

    def __init__(self, medians, iqrs):
        """
        Initialize the RobustScaler with provided medians and IQRs.

        Parameters:
            medians (np.ndarray): Median values for each feature.
            iqrs (np.ndarray): Interquartile ranges (IQRs) for each feature.
        """
        self.medians = medians
        self.iqrs = iqrs

    def transform(self, X):
        """
        Scale the input data X using the stored medians and IQRs.

        Parameters:
            X (np.ndarray): Input data to be scaled.

        Returns:
            X_scaled (np.ndarray): Scaled data.
        """
        X_scaled = (X - self.medians) / self.iqrs
        return X_scaled
