import argparse
import logging
import os
import sys

import numpy as np
from sarwaveifrproc.utils import get_output_safe, load_config, load_models, process_files

def parse_args():
    
    parser = argparse.ArgumentParser(description="Generate a L2 WAVE product from a L1B or L1C SAFE.")

    # Define arguments
    parser.add_argument("--input_path", required=True, help="l1b or l1c safe path or listing path (.txt file).")
    parser.add_argument("--save_directory", required=True, help="where to save output data.")
    parser.add_argument("--product_id", required=True, help="3 digits ID representing the processing options. Ex: E00.")

    # Group related arguments under 'model' and 'bins'
    model_group = parser.add_argument_group('model', 'Arguments related to the neural models')
    model_group.add_argument("--model_intraburst", required=False, help="neural model path to predict sea states on intraburst data.")
    model_group.add_argument("--model_interburst", required=False, help="neural model path to predict sea states on interburst data.")

    model_group.add_argument("--scaler_intraburst", required=False, help="scaler path to standardize intraburst data before feeding it to the neural model.")
    model_group.add_argument("--scaler_interburst", required=False, help="scaler path to standardize interburst data before feeding it to the neural model.")

    model_group.add_argument("--bins_intraburst", required=False, help="bins path that depicts the range of predictions on intraburst data.")
    model_group.add_argument("--bins_interburst", required=False, help="bins path that depicts the range of predictions on interburst data.")

    model_group.add_argument("--predicted_variables", required=False, help="list of sea states variables to predict.")
    
    # Other arguments
    parser.add_argument("--overwrite", action="store_true", default=False, help="overwrite the existing outputs")
    parser.add_argument("--verbose", action="store_true", default=False)
   
    args = parser.parse_args()
    return args


def setup_logging(verbose=False):
    fmt = '%(asctime)s %(levelname)s %(filename)s(%(lineno)d) %(message)s'
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format=fmt, datefmt='%d/%m/%Y %H:%M:%S', force=True)

def get_files(dir_path, listing):
    
    fn = []
    for s in listing:
        search_path = os.path.join(dir_path, s.replace('WAVE', 'XSP_'), '*-?v-*.nc')
        fn+=glob.glob(search_path)

    print('Number of files :', len(fn))
    return fn


def main():
    args = parse_args()
    setup_logging(args.verbose)

    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress TensorFlow INFO and WARNING messages
    os.environ['CUDA_VISIBLE_DEVICES'] = '-1'  # Hide CUDA devices

    logging.info("Loading configuration file...")
    conf = load_config()

    input_path = args.input_path
    save_directory = args.save_directory
    product_id = args.product_id
    predicted_variables = args.predicted_variables or conf['predicted_variables']

    if input_path.endswith('.txt'):
        files = np.loadtxt(input_path, dtype=str)
        output_safes = np.array([get_output_safe(f, save_directory, product_id) for f in files])

        if not args.overwrite:
            mask = np.array([os.path.exists(f) for f in output_safes])
            files, output_safes = files[~mask], output_safes[~mask]

            logging.info(f"{np.sum(mask)} file(s) already exist(s) and overwriting is not allowed. Use --overwrite to overwrite existing files.")

            if not files.size:
                return None

        logging.info('Loading models...')
        # Define the paths. When args paths are None, the conf paths are set by default (the "or" operator returns first element if true, second element if first is None). 
        paths = {
        'model_intraburst': args.model_intraburst or conf['model_intraburst'],
        'model_interburst': args.model_interburst or conf['model_interburst'],
        'scaler_intraburst': args.scaler_intraburst or conf['scaler_intraburst'],
        'scaler_interburst': args.scaler_interburst or conf['scaler_interburst'],
        'bins_intraburst': args.bins_intraburst or conf['bins_intraburst'],
        'bins_interburst': args.bins_interburst or conf['bins_interburst'],
        }
        model_intraburst, model_interburst, scaler_intraburst, scaler_interburst, bins_intraburst, bins_interburst = load_models(paths, predicted_variables)
        logging.info('Models loaded.')

        logging.info('Processing files...')
        for f, output_safe in zip(files, output_safes):
            process_files(f, output_safe, model_intraburst, model_interburst, scaler_intraburst, scaler_interburst, bins_intraburst, bins_interburst, predicted_variables, product_id)

            
    else:
        logging.info("Checking if output safe already exists...")
        output_safe = get_output_safe(input_path, save_directory, product_id)

        if os.path.exists(output_safe) and not args.overwrite:
            logging.info(f"{output_safe} already exists and overwriting is not allowed. Use --overwrite to overwrite existing files.")
            return None

        logging.info('Loading models...')
        paths = {
            'model_intraburst': args.model_intraburst or conf['model_intraburst'],
            'model_interburst': args.model_interburst or conf['model_interburst'],
            'scaler_intraburst': args.scaler_intraburst or conf['scaler_intraburst'],
            'scaler_interburst': args.scaler_interburst or conf['scaler_interburst'],
            'bins_intraburst': args.bins_intraburst or conf['bins_intraburst'],
            'bins_interburst': args.bins_interburst or conf['bins_interburst'],
        }
        model_intraburst, model_interburst, scaler_intraburst, scaler_interburst, bins_intraburst, bins_interburst = load_models(paths, predicted_variables)
        logging.info('Models loaded.')

        logging.info('Processing files...')
        process_files(input_path, output_safe, model_intraburst, model_interburst, scaler_intraburst, scaler_interburst, bins_intraburst, bins_interburst, predicted_variables, product_id)

    logging.info(f'Processing terminated. Output directory: \n{save_directory}')
