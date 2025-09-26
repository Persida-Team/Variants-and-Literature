import concurrent.futures
import json
import os
import re
from typing import Any
from utils.logging.logging_setup import (
    supplementary_error_logger,
    supplementary_info_logger,
)

PATTERNS = [
    re.compile("[\s]CA[0-9]+"),
    re.compile(",CA[0-9]+"),
    re.compile("[\s]rs[0-9]+"),
    re.compile(",rs[0-9]+"),
    re.compile("rs[0-9]+[ ]?[ACGT][>/][ACGT]"),
    re.compile("[ACGT][/>-][ACGT][- ]rs[0-9]+"),
    re.compile("rs[0-9]+[-]?[ACGT]"),
    re.compile("([-]?[0-9]+[ ]?(ins|del|ins/del)[ ]?[ACGT]+)"),
    re.compile(" [0-9]*[+-]?[0-9]+[ ]?[ACGT][ ]?[>/-][ ]?[ACGT]"),
    re.compile(
        "(Ala|Arg|Asn|Asp|Asx|Cys|Glu|Gln|Glx|Gly|His|Ile|Leu|Lys|Met|Phe|Pro|Ser|Thr|Trp|Tyr|Val)[0-9]+ (to|at|with) (Ala|Arg|Asn|Asp|Asx|Cys|Glu|Gln|Glx|Gly|His|Ile|Leu|Lys|Met|Phe|Pro|Ser|Thr|Trp|Tyr|Val)"
    ),
    re.compile(
        "(Ala|Arg|Asn|Asp|Asx|Cys|Glu|Gln|Glx|Gly|His|Ile|Leu|Lys|Met|Phe|Pro|Ser|Thr|Trp|Tyr|Val)[0-9]+ (to|at|with) (alanine|arginine|asparagine|aspartic acid|cysteine|glutamic acid|glutamine|glycine|histidine|isoleucine|leucine|lysine|methionine|phenylalanine|proline|serine|threonine|tryptophan|tyrosine|valine)"
    ),
    re.compile(
        "((Ala|Arg|Asn|Asp|Asx|Cys|Glu|Gln|Glx|Gly|His|Ile|Leu|Lys|Met|Phe|Pro|Ser|Thr|Trp|Tyr|Val)[0-9]+(fs|FS|Fs))"
    ),
    re.compile("[ARNDCQEGHILKMFPOSUTWYV][0-9]+fs"),
    re.compile("[ACGT] to [ACGT] at [0-9]+"),
]


def save_json(data: Any, file_path: str) -> None:
    """
    Save JSON data to a file.
    Args:
        data: The JSON data to be saved.
        file_path: The path of the file to save the JSON data to.
    Raises:
        ValueError: If the file_path is not a non-empty string.
    """

    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    if not isinstance(file_path, str) or not file_path:
        raise ValueError("Invalid filename. ")
    try:
        supplementary_info_logger.info(f"Saving JSON to file: {file_path}. ")
        with open(file_path, "w") as outfile:
            json.dump(data, outfile, indent=4)
        supplementary_info_logger.info(f"JSON '{file_path}' saved successfully")
    except Exception as e:
        supplementary_error_logger.error(
            f"An error occurred while saving the JSON file: {str(e)}", exc_info=True
        )
        raise Exception(f"An error occurred while saving the JSON file. ")


def load_json(file_path: str) -> Any:
    """
    Load JSON data from a file.
    Args:
        file_path (str): The path to the JSON file to be loaded.
    Returns:
        Any: The loaded JSON data.
    Raises:
        ValueError: If the file_path is not a non-empty string.
    """
    if not isinstance(file_path, str) or not file_path:
        raise ValueError("Invalid filename. ")
    try:
        supplementary_info_logger.info(f"Loading JSON from file: {file_path}. ")
        with open(file_path) as f:
            data = json.load(f)
        supplementary_info_logger.info(f"JSON '{file_path}' loaded successfully. ")
        return data
    except Exception as e:
        supplementary_error_logger.error(
            f"An error occurred while loading the JSON file: {str(e)}", exc_info=True
        )
        raise Exception(f"An error occurred while loading the JSON file. ")


def create_directory(destination: str) -> None:
    """
    Create a directory at the specified destination path if it does not already exist.
    Args:
        destination (str): The path where the directory should be created.
    Raises:
        Exception: If an error occurs during the directory creation process.
    Returns:
        None
    """
    if os.path.isdir(destination):
        supplementary_info_logger.info(f"Directory '{destination}' already exists.")
        return
    try:
        os.makedirs(destination)
        supplementary_info_logger.info(f"Directory '{destination}' is created.")
    except Exception as e:
        supplementary_error_logger.error(
            f"Failed to create directory '{destination}': {str(e)}.", exc_info=True
        )
        raise Exception(f"Failed to create directory '{destination}'.")


def find_matches_collected(text: str, patterns=PATTERNS) -> set:
    """
    Find and collect matches in the given text using the specified patterns.
    Args:
        text (str): The text to search for matches.
        patterns (list): The list of patterns to use for matching.
    Returns:
        set: A set of collected matches found in the text.
    """
    res = set()
    for pattern in patterns:
        compiled_pattern = re.compile(pattern)
        res.update(
            map(
                lambda match: (
                    match.strip() if isinstance(match, str) else match[0].strip()
                ),
                (match for match in compiled_pattern.findall(text) if match),
            )
        )
    return res


def check_contents_paginated(data: dict) -> dict:
    """
    Check the contents of paginated data and return a dictionary of matches.
    Args:
        data (dict): The paginated data to check.
    Returns:
        dict: A dictionary of matches found in the paginated data.
    """
    if not isinstance(data, dict) or len(data) == 0:
        return {}
    res = {key: find_matches_collected(data[key]) for key in data}
    return res


def check_contents_table(data: list) -> dict:
    """
    Find matches in the given table data.
    Args:
        data (list): The table data to search for matches.
    Returns:
        dict: A dictionary containing the matches found in the column headers and rows of the table.
            The dictionary has two keys:
            - "found_in_column_header": A set of matches found in the column headers.
            - "found_in_rows": A set of matches found in the rows.
    """
    keys = "  ".join(list(data[0].keys()))
    res = {}
    res["found_in_column_header"] = find_matches_collected(keys)
    res["found_in_rows"] = set()
    for item in data:
        for key, value in item.items():
            res["found_in_rows"].update(find_matches_collected(str(value)))
    return res


class DataProcessor:
    def __init__(self, data_type, contents, path, filename, out_folder, metadata):
        self.data_type = data_type
        self.contents = contents
        self.path = path
        self.filename = filename
        self.out_folder = out_folder
        self.pmc_id = list(metadata.keys())[0]

    def process_text_image_bed(self):
        res = find_matches_collected(self.contents)
        if res:
            self.contents = sorted(res)
            self.create_directory()
            self.save_json()

    def process_pdf_powerpoint_excel_doc(self):
        print("proccessing-> process_pdf_powerpoint_excel_doc")
        res = check_contents_paginated(self.contents)
        print(res)
        for key in list(res.keys()):
            if res[key]:
                res[key] = sorted(res[key])
            else:
                res.pop(key)
        if res:
            self.contents = res
            self.create_directory()
            self.save_json()

    def process_table(self):
        res = check_contents_table(self.contents)
        for key in list(res.keys()):
            if res[key]:
                res[key] = sorted(res[key])
            else:
                res.pop(key)
        if res:
            self.contents = res
            self.create_directory()
            self.save_json()

    def process_data(self):
        processing_methods = {
            "text": self.process_text_image_bed,
            "image": self.process_text_image_bed,
            "bed": self.process_text_image_bed,
            "pdf": self.process_pdf_powerpoint_excel_doc,
            "powerpoint": self.process_pdf_powerpoint_excel_doc,
            "excel": self.process_pdf_powerpoint_excel_doc,
            "doc": self.process_pdf_powerpoint_excel_doc,
            "table": self.process_table,
        }
        if self.data_type in processing_methods:
            processing_methods[self.data_type]()

    def create_directory(self):
        out_path = os.path.join(self.out_folder, self.path.split("/")[-1])
        os.makedirs(out_path, exist_ok=True)

    def save_json(self):
        data_path = os.path.join(self.path, self.filename)
        # data = load_json(data_path)
        # data[self.path.split("/")[-1]][list(data[self.path.split("/")[-1]].keys())[0]]["contents"] = self.contents
        # os.path.join(self.out_folder, self.path.split("/")[-1], self.filename)
        OUTPUT = os.path.join(self.out_folder, self.pmc_id, f"{self.filename}.json")
        to_save = {
            self.pmc_id: {
                self.filename: {
                    "type": self.data_type,
                    "contents": self.contents,
                }
            }
        }
        save_json(to_save, OUTPUT)


def search_variants_and_save(path: str, filename: str, out_folder: str) -> None:
    """
    Search for variants in the given data and save the results in a specified folder.
    Args:
        path (str): The path to the data file.
        filename (str): The name of the data file.
        out_folder (str): The folder to save the results in.
    Returns:
        None
    """
    data_path = os.path.join(path, filename)
    supplementary_info_logger.info(f"Working with '{filename}' in '{path}'")
    data = load_json(data_path)
    pmc = path.split("/")[-1]
    data_type = data[pmc][list(data[pmc].keys())[0]]["type"]
    contents = data[pmc][list(data[pmc].keys())[0]]["contents"]

    data_processor = DataProcessor(data_type, contents, path, filename, out_folder)
    data_processor.process_data()


from collections import defaultdict


def get_files(outputs_folder: str) -> dict:
    """
    Get a dictionary of files in the specified folder and its subfolders.
    Args:
        outputs_folder (str): The path to the folder.
    Returns:
        dict: A dictionary where the keys are folder paths and the values are lists of file names.
    """
    try:
        res = defaultdict(list)
        for folder, subdir, filename in os.walk(outputs_folder):
            if filename:
                res[folder].append(filename)
        return res
    except Exception as e:
        supplementary_error_logger.error(
            f"Error occurred while getting files: {e}", exc_info=True
        )
        return {}


def find_variants_from_supplementary(input_folder: str, output_folder: str) -> None:
    """
    Find variants from the supplementary data files in the specified input folder and save the results in the specified output folder.
    Args:
        input_folder (str): The path to the folder containing the input data files.
        output_folder (str): The path to the folder where the results should be saved.
    Returns:
        None
    """
    if input_folder == output_folder:
        raise ValueError("Input folder and output folder should not be the same.")
    create_directory(output_folder)
    input_files = get_files(input_folder)
    for link in input_files:
        files = input_files[link][0]
        print(files)
        with concurrent.futures.ProcessPoolExecutor() as executor:
            results = [
                executor.submit(search_variants_and_save, link, file, output_folder)
                for file in files
            ]
            for result in concurrent.futures.as_completed(results):
                try:
                    result.result()
                except FileNotFoundError as e:
                    supplementary_error_logger.error(
                        f"File not found error occurred while processing file: {str(e)}",
                        exc_info=True,
                    )
                except json.JSONDecodeError as e:
                    supplementary_error_logger.error(
                        f"JSON decoding error occurred while processing file: {str(e)}",
                        exc_info=True,
                    )
                except Exception as e:
                    supplementary_error_logger.error(
                        f"Error occurred while processing file: {str(e)}", exc_info=True
                    )
        # for file in files:
        #     search_variants_and_save(link, file, destination)


if __name__ == "__main__":
    logging.basicConfig(
        filename="logging.log",
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        filemode="w",
        encoding="utf-8",
        level=logging.INFO,
    )
    # change in_folder to folder containing parsed documents - should have subfolder named as PMCID
    in_folder = "./outputs"
    destination = "./find_variants_from_supplementary_results"
    find_variants_from_supplementary(in_folder, destination)
    # rename in_folder
