=====
Usage
=====

To use sarwaveifrproc in a project::

    import sarwaveifrproc


.. code-block::

    L2-wave-processor -h
    usage: L2-wave-processor [-h] --input_path INPUT_PATH --save_directory SAVE_DIRECTORY --product_id PRODUCT_ID [--model_intraburst MODEL_INTRABURST]
                             [--model_interburst MODEL_INTERBURST] [--scaler_intraburst SCALER_INTRABURST] [--scaler_interburst SCALER_INTERBURST]
                             [--bins_intraburst BINS_INTRABURST] [--bins_interburst BINS_INTERBURST] [--predicted_variables PREDICTED_VARIABLES] [--overwrite] [--verbose]

    Generate a L2 WAVE product from a L1B or L1C SAFE.

    options:
      -h, --help            show this help message and exit
      --input_path INPUT_PATH
                            l1b or l1c safe path or listing path (.txt file).
      --save_directory SAVE_DIRECTORY
                            where to save output data.
      --product_id PRODUCT_ID
                            3 digits ID representing the processing options. Ex: E00.
      --overwrite           overwrite the existing outputs
      --verbose

    model:
      Arguments related to the neural models

      --model_intraburst MODEL_INTRABURST
                            neural model path to predict sea states on intraburst data.
      --model_interburst MODEL_INTERBURST
                            neural model path to predict sea states on interburst data.
      --scaler_intraburst SCALER_INTRABURST
                            scaler path to standardize intraburst data before feeding it to the neural model.
      --scaler_interburst SCALER_INTERBURST
                            scaler path to standardize interburst data before feeding it to the neural model.
      --bins_intraburst BINS_INTRABURST
                            bins path that depicts the range of predictions on intraburst data.
      --bins_interburst BINS_INTERBURST
                            bins path that depicts the range of predictions on interburst data.
      --predicted_variables PREDICTED_VARIABLES
                            list of sea states variables to predict.
