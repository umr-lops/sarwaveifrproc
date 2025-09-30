import glob
import logging
import os
import re
import traceback
from datetime import datetime

import xarray as xr

from sarwaveifrproc.l2_wave import generate_l2_wave_product

SAFE_PATTERN = (
    r"^(?P<mission_id>S1[A-Z])_"
    r"(?P<mode>[IE]W)_"
    r"(?P<type>[A-Z]{3})__"
    r"(?P<level>[0-9])(?P<class>[A-Z])(?P<pol>[A-Z]{2})_"
    r"(?P<starttime>\d{8}T\d{6})_"
    r"(?P<endtime>\d{8}T\d{6})_"
    r"(?P<orbit_no>\d{6})_"
    r"(?P<datatake_id>[A-Z0-9]{6})_"
    r"(?P<id>[A-Z0-9]{4})"
    r"(?:_(?P<suffix>[A-Z0-9]{3}))?"  # optional _B02, _A02, etc.
    r"\.SAFE$"
)


def get_safe_date(safe):
    """
    Extracts and returns the date and time from a given SAFE directory name.

    Parameters:
        safe (str): SAFE directory name.

    Returns:
        datetime: A datetime object representing the extracted date and time.
    """
    date_str = safe.split("_")[5]
    date = datetime.strptime(date_str, "%Y%m%dT%H%M%S")
    return date


def get_output_safe(l1x_safe, root_savepath, tail="E00"):
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
    l1x_safe = l1x_safe.rstrip("/")  # remove trailing slash
    safe = l1x_safe.split(os.sep)[-1]
    final_safe = safe
    info = re.match(SAFE_PATTERN, final_safe)
    m = info.groupdict()
    cond1 = m["type"] == "XSP"
    cond2 = m["pol"] in ["SV", "DV"]
    cond3 = final_safe.endswith(".SAFE")
    if cond1 and cond2 and cond3:
        date = get_safe_date(safe)

        final_safe = final_safe.replace("XSP_", "WAV_")
        final_safe = final_safe.replace("1SDV", "2SDV")
        final_safe = final_safe.replace("1SSV", "2SSV")
        regexA = re.compile("A[0-9]{2}.SAFE")
        regexB = re.compile("B[0-9]{2}.SAFE")
        if re.search(regexA, final_safe.split("_")[-1]) or re.search(
            regexB, final_safe.split("_")[-1]
        ):
            final_safe = final_safe.replace(
                final_safe.split("_")[-1], f"{tail.upper()}.SAFE"
            )
        else:
            print("no slug existing-> just add the product ID")
            final_safe = final_safe.replace(".SAFE", f"_{tail.upper()}.SAFE")

        output_safe = os.path.join(
            root_savepath, date.strftime("%Y"), date.strftime("%j"), final_safe
        )

        return output_safe

    else:
        raise ValueError("The input SAFE does not meet the filename requirements.")


def get_output_filename(l1x_path, output_safe, tail="e00"):
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
    filename_exploded = filename.split("-")
    regex_file_number = re.compile("[0-9]{2}[0-6]")
    if filename[0:2] == "l1":
        final_filename = "-".join(
            [
                *filename_exploded[:4],
                "dv",
                *filename_exploded[5:-1],
                f"{tail.lower()}.nc",
            ]
        )
        if re.search(regex_file_number, final_filename.split("-")[9]):
            final_filename = final_filename.replace(
                final_filename.split("-")[9] + "-", ""
            )  # remove the -004- giving the number of the file
    else:
        final_filename = "-".join(
            [
                *filename_exploded[:3],
                "dv",
                *filename_exploded[4:-1],
                f"{tail.lower()}.nc",
            ]
        )
        if re.search(regex_file_number, final_filename.split("-")[8]):
            final_filename = final_filename.replace(
                final_filename.split("-")[8] + "-", ""
            )  # remove the -004- giving the number of the file
    final_filename = final_filename.replace("l1b", "l2")
    final_filename = final_filename.replace("l1c", "l2")
    final_filename = final_filename.replace("xsp", "wav")
    savepath = os.path.join(output_safe, final_filename)
    return savepath


def process_files(
    input_safe, output_safe, models, models_outputs, predicted_variables, product_id
):
    """
    Processes files in the input directory, generates predictions, and saves results in the output directory.

    Parameters:
        input_safe (str): Input safe path.
        output_safe (str): Path to the directory where output data will be saved.
        models (dict): dict of onnx runtime inference sessions
        models_outputs (dict): dict of List of model outputs names
        predicted_variables (list): List of variable names to be predicted.
        product_id (str): Identifier for the output product.
    Returns:
        files_in_error (list): List of files that encountered errors during processing.
    """
    subswath_filenames = glob.glob(os.path.join(input_safe, "*?v*.nc"))
    logging.debug(f"{len(subswath_filenames)} subswaths found in given safe.")
    files_in_error = []
    for path in subswath_filenames:
        try:
            xdt = xr.DataTree.from_dict(xr.open_groups(path))
            l2_product = generate_l2_wave_product(
                xdt, models, models_outputs, predicted_variables
            )

            os.makedirs(output_safe, exist_ok=True)
            savepath = get_output_filename(path, output_safe, product_id)
            l2_product.to_netcdf(savepath)
        except Exception:
            logging.errror(traceback.format_exc())
            logging.error(f"Error processing {path}. Skipping this file.")
            files_in_error.append(path)
            continue
    return files_in_error  # can be used to reprocess the files in failure
