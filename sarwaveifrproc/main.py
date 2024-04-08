import argparse
import logging
import os
import sys

def parse_args():
    
    parser = argparse.ArgumentParser(description="Generate a L2 WAVE product from a L1B or L1C SAFE.")

    # Define arguments
    parser.add_argument("--input_safe", required=True, help="l1b or l1c safe path.")
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

def main():
    
    args = parse_args()
    
    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress TensorFlow INFO and WARNING messages
    os.environ['CUDA_VISIBLE_DEVICES'] = '-1'  # Hide CUDA devices

    from sarwaveifrproc.utils import get_output_safe, load_config
        
    logging.info("Loading configuration file...")
    conf = load_config()
    
    # Parse arguments    
    input_safe = args.input_safe
    save_directory = args.save_directory
    product_id = args.product_id
    predicted_variables = args.predicted_variables or conf['predicted_variables']
    
    logging.info("Checking if output safe already exists...")
    output_safe = get_output_safe(input_safe, save_directory, product_id)
    if os.path.exists(output_safe) and not (args.overwrite):
        logging.info(f"{output_safe} already exists and overwriting is not allowed. Use --overwrite to overwrite existing files.")
        return None

    from sarwaveifrproc.utils import load_models, process_files

    # Define the paths. When args paths are None, the conf paths are set by default (the "or" operator returns first element if true, second element if first is None). 
    paths = {
        'model_intraburst': args.model_intraburst or conf['model_intraburst'],
        'model_interburst': args.model_interburst or conf['model_interburst'],
        'scaler_intraburst': args.scaler_intraburst or conf['scaler_intraburst'],
        'scaler_interburst': args.scaler_interburst or conf['scaler_interburst'],
        'bins_intraburst': args.bins_intraburst or conf['bins_intraburst'],
        'bins_interburst': args.bins_interburst or conf['bins_interburst'],
    }
    logging.info('Loading models...')
    model_intraburst, model_interburst, scaler_intraburst, scaler_interburst, bins_intraburst, bins_interburst = load_models(paths, predicted_variables)
    logging.info('Models loaded.')

    logging.info('Processing files...')
    process_files(input_safe, output_safe, model_intraburst, model_interburst, scaler_intraburst, scaler_interburst, bins_intraburst, bins_interburst, predicted_variables, product_id)
    logging.info(f'Processing terminated. Output directory: \n{output_safe}')
