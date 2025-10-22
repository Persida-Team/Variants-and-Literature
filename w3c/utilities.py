import hashlib
import json
import logging
import os
import re
import time
import traceback
import uuid
from datetime import datetime, timezone
from typing import Any
from urllib.parse import quote

import requests
from dotenv import load_dotenv
from utils.logging.logging_setup import w3c_error_logger, w3c_info_logger
from w3c.logger_config import setup_logger

load_dotenv()


BODY_DIRECTORY = os.getenv("BODY_DIRECTORY", None)
EXISTING_BODIES_PATH = os.getenv("EXISTING_BODIES_PATH", None)
W3C_LOGIN = os.getenv("W3C_LOGIN", None)
W3C_PASSWORD = os.getenv("W3C_PASSWORD", None)
if not BODY_DIRECTORY:
    raise Exception("BODY_DIRECTORY is not set in the env file.")
if not EXISTING_BODIES_PATH:
    raise Exception("EXISTING_BODIES_PATH is not set in the env file.")
if not W3C_LOGIN:
    raise Exception("W3C_LOGIN is not set in the env file.")
if not W3C_PASSWORD:
    raise Exception("W3C_PASSWORD is not set in the env file.")

SAFE_CHARACTERS = "/:?=&"
ONE_RSID_REQUEST = "https://reg.genome.network/alleles?dbSNP.rs="
ONE_CAID_REQUEST = "https://reg.genome.network/allele/"
PUT_CAID = "http://reg.genome.network/annotateVcf?assembly=GRCh38&ids=CA"
CAID_FROM_FILE = "https://reg.genome.network/alleles?file=dbSNP.rs"
ONE_MONDO_REQUEST = "http://www.ebi.ac.uk/ols4/api/search?ontology=MONDO&exact=true&q="
DBSNP_RSID_REQUEST = "https://api.ncbi.nlm.nih.gov/variation/v0/refsnp/"
HGVS_REQUEST = "https://reg.genome.network/allele?hgvs="

CONTEXT_URL = "https://genboree.org/ldh-vss/CgLdhSchema/id/VIL-Context/latest"  # ako imamo neki file u kom su sve konstante/regexi/... treba tamo da prebacimo i odavde

REFSEQ = [
    "NC_000001.11",
    "NC_000002.12",
    "NC_000003.12",
    "NC_000004.12",
    "NC_000005.10",
    "NC_000006.12",
    "NC_000007.14",
    "NC_000008.11",
    "NC_000009.12",
    "NC_000010.11",
    "NC_000011.10",
    "NC_000012.12",
    "NC_000013.11",
    "NC_000014.9",
    "NC_000015.10",
    "NC_000016.10",
    "NC_000017.11",
    "NC_000018.10",
    "NC_000019.10",
    "NC_000020.11",
    "NC_000021.9",
    "NC_000022.11",
    "NC_000023.11",
    "NC_000024.10",
    "NC_012920.1",
]

UUID_ZERO = uuid.UUID("00000000-0000-0000-0000-000000000000")
NAMESPACE_VIL = uuid.uuid5(UUID_ZERO, "Variants in literature")

PATTERNS_RS = [
    re.compile("rs[ #]?[0-9]+"),
    re.compile("rs[ #]?[0-9]+,[0-9]+"),
]
PATTERNS_CA = [re.compile("CA[0-9]+")]
PATTERNS_COMPLEX = [
    re.compile("rs[0-9]+[ ]?[ACGT][>/-][ACGT]"),
    re.compile("rs[0-9]+[ -]?[ACGT][ ]"),
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
    if not isinstance(file_path, str) or not file_path:
        raise ValueError("Invalid filename. ")
    with open(file_path, "w") as outfile:
        json.dump(data, outfile, indent=4)
    try:
        w3c_info_logger.info(f"Saving JSON to file: {file_path}. ")
        w3c_info_logger.info(f"JSON '{file_path}' saved successfully")
    except Exception as e:
        w3c_error_logger.error(
            f"An error occurred while saving the JSON file: {str(e)}"
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
        w3c_info_logger.info(f"Loading JSON from file: {file_path}. ")
        with open(file_path) as f:
            data = json.load(f)
        w3c_info_logger.info(f"JSON '{file_path}' loaded successfully. ")
        return data
    except Exception as e:
        w3c_error_logger.error(
            f"An error occurred while loading the JSON file: {str(e)}\n{traceback.format_exc()}\n\n"
        )
        raise Exception(f"An error occurred while loading the JSON file. ")


def load_existing_bodies(file_path: str):
    """
    Opens and reads the contents of an existing file.
    The file is expected to have rows of rsIDs.
    """
    try:
        with open(file_path, "r") as f:
            data = f.readlines()
        data = list(map(lambda x: x.strip("\n"), data))
        return data
    except Exception as e:
        w3c_error_logger.error(
            f"An error occurred while loading the existing bodies: {str(e)}"
        )
        raise Exception(f"An error occurred while loading the existing bodies. ")


def append_to_existing_bodies(file_path: str, rsID: str):
    """
    Atomic append to the file.
    Check if the rsID is not contained inside the file, then append.
    """
    data = load_existing_bodies(file_path)
    if rsID in data:
        return
    with open(file_path, "a", buffering=1) as file:
        file.write(f"{rsID}\n")


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
        # w3c_info_logger.info(f"Directory '{destination}' already exists.")
        return
    try:
        os.makedirs(destination)
        w3c_info_logger.info(f"Directory '{destination}' is created.")
    except Exception as e:
        w3c_error_logger.error(f"Failed to create directory '{destination}': {str(e)}.")
        raise Exception(f"Failed to create directory '{destination}'.")


def build_url(url: str, safe: str = SAFE_CHARACTERS) -> str:
    """
    Build a URL by quoting special characters in the given URL.
    Args:
        url (str): The URL to be built.
        safe (str): Characters that should not be quoted in the URL. Default is '/:?=&'.
    Returns:
        str: The built URL with special characters quoted.
    Raises:
        ValueError: If the provided URL is empty or not a string.
        Exception: If an error occurs while building the URL.
    """
    if not isinstance(url, str) or not url:
        w3c_error_logger.error(f"Invalid URL: '{url}'")
        raise ValueError("Invalid URL.")
    try:
        return quote(url, safe=safe)
    except Exception as e:
        w3c_error_logger.error(f"An error occurred while building the URL: {str(e)}")
        raise Exception("An error occurred while building the URL.")


def send_get_request(URL: str, params: dict = None) -> dict:
    """
    Send a GET request to the specified URL with optional parameters.
    Args:
        URL (str): The URL to send the request to.
        params (dict): Optional parameters to include in the request. Default is None.
    Returns:
        dict: The JSON response if it is a valid JSON.
    """
    with requests.get(
        url=build_url(URL), params=params, headers={"Accept": "application/json"}
    ) as r:
        w3c_info_logger.info(r.url)
        if r.status_code != 200:
            w3c_error_logger.error(
                f"GET Request to '{r.url}' failed with status code {r.status_code}"
            )
            return {}
            # raise Exception(f"Request failed with status code {r.status_code}")
        try:
            return r.json()
        except json.JSONDecodeError:
            w3c_error_logger.error(f"Response from {r.url} not a json!")
            return {}
            # raise Exception(f"Response from {r.url} not a json!")


def send_post_request(URL: str, data: dict) -> dict:
    """
    Sends a POST request to the specified URL with the given data.
    Args:
        URL (str): The URL to send the request to.
        data (dict): The data to send with the request.
    Returns:
        dict: The JSON response if it is a valid JSON.
    """
    with requests.post(url=build_url(URL), data=data) as r:
        w3c_info_logger.info(r.url)
        if r.status_code != 200:
            w3c_error_logger.error(
                f"POST Request to '{r.url}' failed with status code {r.status_code}"
            )
            # raise Exception(f"Request failed with status code {r.status_code}")
            return {}
        try:
            return r.json()
        except:
            w3c_error_logger.error(f"Response from {r.url} not a json!")
            return {}
            # raise Exception(f"Response from {r.url} not a json!")


def send_put_request(
    url: str, data: str, login: str, password: str, response_type: str
) -> str:
    """
    Send a PUT request to the specified URL with the given data, login, and password.
    Args:
        url (str): The URL to send the request to.
        data (str): The data to send with the request.
        login (str): The login for authentication.
        password (str): The password for authentication.
        response_type (str): text or json
    Returns:
        str: The response from the PUT request.
    """
    # calculate token & full URL
    identity = hashlib.sha1((login + password).encode("utf-8")).hexdigest()
    gbTime = str(int(time.time()))
    token = hashlib.sha1((url + identity + gbTime).encode("utf-8")).hexdigest()
    request = url + "&gbLogin=" + login + "&gbTime=" + gbTime + "&gbToken=" + token
    # send request & parse response
    try:
        res = requests.put(request, data=data)
        if response_type == "json":
            response = res.json()
        else:
            response = res.text
        # check status
        if res.status_code != 200:
            w3c_error_logger.error(
                f"PUT Request to '{url}' failed with status code {res.status_code} for data: {data} and response: {response}"
            )
            return ""
            # raise Exception("Error for PUT requests: " + response)
        return response
    except requests.exceptions.RequestException as e:
        w3c_error_logger.error(f"An error occurred during the PUT request: {str(e)}")
        return ""
        # raise Exception("An error occurred during the PUT request.")


def get_results_caid(caid: str) -> dict:
    """
    Get the CAIDs data.
    Args:
        caid (str): The CAID for which to retrieve data.
    Returns:
        dict: The JSON response for given CAID.
    """
    w3c_info_logger.info(f"Requesting CAIDs for {caid}")
    return send_get_request(ONE_CAID_REQUEST + caid)


def get_results_rsid(rsid: str) -> list:
    """
    Get the rsIDs data.
    Args:
        rsid (str): The rsID for which to retrieve data.
    Returns:
        list: The JSON response for given rsID.
    """
    w3c_info_logger.info(f"Requesting rsID data for {rsid}")
    return send_get_request(ONE_RSID_REQUEST + rsid)


def get_results_mondo(id: str) -> dict:
    """
    Get the equivalent MONDO id for MESH id.
    Args:
        id (str): The MESH or OMIM for which to retrieve MONDO. MESH in format 'MESH:xxxxx', OMIM in format 'OMIM:xxxx'.
    Returns:
        dict: The JSON response for given MESH.
    """
    w3c_info_logger.info(f"Requesting CAIDs for {id}")
    return send_get_request(ONE_MONDO_REQUEST + id)


def get_results_vcf_file(pmc_id: str):
    """
    Get the results in VCF format and save them to a file.
    Returns:
        None
    """
    filename = f"{pmc_id}_variants.vcf"
    out_name = f"{pmc_id}_variants_result.vcf"
    login = W3C_LOGIN
    password = W3C_PASSWORD
    url = build_url(PUT_CAID)
    with open(filename) as file:
        data = file.read()
    res = send_put_request(url, data, login, password, "text")
    with open(out_name, "w") as f:
        f.write(res)


def register_new_indel(hgvs: str):
    """
    Get the results in VCF format and save them to a file.
    Returns:
        None
    """
    login = W3C_LOGIN
    password = W3C_PASSWORD
    url = build_url(HGVS_REQUEST + hgvs)
    res = send_put_request(url, None, login, password, "json")
    return res


def get_results_txt_file(filename) -> dict:
    """
    Reads the contents of a text file and sends a POST request to a specified URL with the file data.
    Parameters:
        filename (str): The name of the text file to read.
    Returns:
        dict: The JSON response if it is a valid JSON.
    """
    data = open(filename).read()
    return send_post_request(CAID_FROM_FILE, data)


def get_results_allReg_hgvs(hgvs: str) -> list:
    """
    Get the HGVS data from Allele Registry.
    Args:
        hgvs (str): The HGVS for which to retrieve data.
    Returns:
        list: The JSON response for given rsID.
    """
    w3c_info_logger.info(f"Requesting HGVS data for {hgvs}")
    return send_get_request(HGVS_REQUEST + hgvs)


def get_results_dbSNP_rsid(rsid: str) -> list:
    """
    Get the rsIDs data from dbSNP.
    Args:
        rsid (str): The rsID for which to retrieve data.
    Returns:
        list: The JSON response for given rsID.
    """
    w3c_info_logger.info(f"Requesting rsID data for {rsid}")
    return send_get_request(DBSNP_RSID_REQUEST + rsid)


def get_files(outputs_folder: str) -> dict:
    """
    Get a dictionary of files in the specified folder and its subfolders.
    Args:
        outputs_folder (str): The path to the folder.
    Returns:
        dict: A dictionary where the keys are folder paths and the values are lists of file names.
    """
    try:
        res = {}
        for folder, subdir, filename in os.walk(outputs_folder):
            if filename:
                res[folder] = filename
        return res
    except Exception as e:
        w3c_error_logger.error(f"Error occurred while getting files: {e}")
        return {}


def create_document_id(pmcid: str, exact: str) -> str:
    """
    Create a document ID based on the provided PMCID and exact variant match string.
    Args:
        pmcid (str): The PMCID of the document.
        exact (str): The exact match.
    Returns:
        uuid.UUID: The generated document ID.
    """
    concat_id = pmcid + "; " + exact
    res_id = uuid.uuid5(NAMESPACE_VIL, concat_id)
    return str(res_id)


def create_uuid_for_submission() -> str:
    """
    Generate a random UUID for a submission.
    """
    return str(uuid.uuid4())
