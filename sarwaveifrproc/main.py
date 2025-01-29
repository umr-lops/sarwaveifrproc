import logging
from pathlib import Path
import hydra_zen
import hydra
import os
import glob
import numpy as np
import sarwaveifrproc.utils as utils
from dataclasses import dataclass
import onnxruntime
import re


@dataclass
class Model:
    """
    path: path to the onnx file
    outputs: names of the model output variables
    """

    path: str
    outputs: list[str]


@dataclass
class Prediction:
    """
    model: name of the model that predict this variable
    output_name: name of the model output
    attrs: attribute dictionnary of the variable
    """

    model: str
    output: str
    attrs: dict[str, str]




@dataclass
class PredictedVariables:
    """
    intraburst: variables to add in the intraburst
    interburst: variables to add in the interburst
    """

    intraburst: dict[str, Prediction]
    interburst: dict[str, Prediction]


def main(
    input_path,
    save_directory: str,
    product_id: str,
    models: dict[str, Model],
    predicted_variables: PredictedVariables,
    supported_input_product_versions: list[str]=[],
    overwrite: bool = False,
    verbose: bool = False,
    dry_run: bool = False
):
    """
    Generate a L2 WAVE product from a L1B or L1C SAFE.

    input_path: l1b or l1c safe path or listing path (.txt file).
    save_directory: where to save output data
    product_id: 3 digits ID representing the processing options. Ex: E00.
    models: onnx models and output
    predicted_variables:  model outputs and associated variables name to add to the L2 product
    overwrite: overwrite the existing outputs
    verbose: debug log level if True
    supported_input_product_versions: list of product versions the model exlicitely supports
    dry_run: flag to skip the actual processing
    """

    setup_logging(verbose)
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = (
        "3"  # Suppress TensorFlow INFO and WARNING messages
    )
    os.environ["CUDA_VISIBLE_DEVICES"] = "-1"  # Hide CUDA devices
    logging.info("Loading configuration file...")

    logging.info("Loading models...")
    ort_mods = {k: onnxruntime.InferenceSession(d.path) for k, d in models.items()}
    mod_outs = {k: d.outputs for k, d in models.items()}
    logging.info("Models loaded.")

    if input_path.endswith(".txt"):
        files = np.loadtxt(input_path, dtype=str)
        output_safes = np.array(
            [utils.get_output_safe(f, save_directory, product_id) for f in files]
        )

        if not overwrite:
            mask = np.array([os.path.exists(f) for f in output_safes])
            files, output_safes = files[~mask], output_safes[~mask]

            logging.info(
                f"{np.sum(mask)} file(s) already exist(s) and overwriting is not allowed. Use --overwrite to overwrite existing files."
            )

            if not files.size:
                return None

        logging.info("Processing files...")
        for f, output_safe in zip(files, output_safes):
            name = Path(f).name
            m = re.match(utils.VERS_SAFE_PATTERN, name)
            if m is None or m.groupdict().get('version') not in supported_input_product_versions:
                logging.warning(f'Unsupported product version for SAFE {name}')
            if dry_run: continue
            utils.process_files(
                f, output_safe, ort_mods, mod_outs, predicted_variables, product_id
            )

    else:
        name = Path(input_path).name
        m = re.match(utils.VERS_SAFE_PATTERN, name)
        if m is None or m.groupdict().get('version') not in supported_input_product_versions:
            logging.warning(f'Unsupported product version for SAFE {name}')
        logging.info("Checking if output safe already exists...")
        output_safe = utils.get_output_safe(input_path, save_directory, product_id)

        if os.path.exists(output_safe) and not overwrite:
            logging.info(
                f"{output_safe} already exists and overwriting is not allowed. Use --overwrite to overwrite existing files."
            )
            return None

        logging.info("Processing files...")
        if not dry_run:
            utils.process_files(
                input_path, output_safe, ort_mods, mod_outs, predicted_variables, product_id
            )

    logging.info(f"Processing terminated. Output directory: \n{save_directory}")


def setup_logging(verbose=False):
    fmt = "%(asctime)s %(levelname)s %(filename)s(%(lineno)d) %(message)s"
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level, format=fmt, datefmt="%d/%m/%Y %H:%M:%S", force=True
    )


def get_files(dir_path, listing):

    fn = []
    for s in listing:
        search_path = os.path.join(dir_path, s.replace("WAVE", "XSP_"), "*-?v-*.nc")
        fn += glob.glob(search_path)

    print("Number of files :", len(fn))
    return fn


hydra_main = hydra.main(
    config_name="e11",
    config_path="pkg://sarwave_config",
    version_base="1.3",
)(hydra_zen.zen(main))
