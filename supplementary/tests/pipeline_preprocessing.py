import concurrent.futures
import datetime
import os
import shutil
import sys
import tarfile
import tempfile
import traceback
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from .dynamic_test import run_on_all_from_dict, run_on_all_from_dict_and_return


def group_files(directory: str) -> dict[str, list[str]]:
    def find_matching_files(file_list) -> list[str]:
        base_names = {}
        for file in file_list:
            base_name = ".".join(file.split(".")[:-1])
            ext = file.split(".")[-1]
            if base_name in base_names:
                base_names[base_name].append(ext)
            else:
                base_names[base_name] = [ext]
        try:
            matching_files = {
                k: v for k, v in base_names.items() if "nxml" in v and "pdf" in v
            }
            file_base_name = list(matching_files.keys())[0]
            return [
                file_base_name + ".pdf",
                file_base_name + ".nxml",
            ]
        except IndexError:
            """
            No matching pdf and nxml found (one or more is missing)
            """
            try:
                matching_file = {k: v for k, v in base_names.items() if "nxml" in v}
                file_base_name = list(matching_file.keys())[0]
                return [file_base_name + ".nxml"]
            except IndexError:
                """
                No nxml found
                """

                matching_file = {k: v for k, v in base_names.items() if "pdf" in v}
                file_base_name = list(matching_file.keys())[0]
                return [file_base_name + ".pdf"]

    file_list = os.listdir(directory)
    files_to_exclude = find_matching_files(file_list)
    for file in files_to_exclude:
        file_list.remove(file)
    grouped_files = defaultdict(list)
    for file_name in file_list:
        grouped_files[file_name.split(".")[-1].lower()].append(directory + file_name)
    return grouped_files


def download_supplementary_tar_gz(pmc_id: str, directory: str) -> bool:
    NUMBER_OF_RETRIES = 5
    DELAY = 120  # seconds
    session = requests.Session()
    retries = Retry(
        total=NUMBER_OF_RETRIES,
        backoff_factor=DELAY,
        status_forcelist=[500, 502, 503, 504],
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))

    url = f"https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id={pmc_id}"
    response = session.get(url, timeout=60)
    if response.status_code != 200:
        print(f"Failed to download {pmc_id} - {response.status_code}")
        return False
    root = ET.fromstring(response.text)
    link_element = root.find(".//link[@format='tgz']")
    try:
        tgz_link = link_element.get("href").replace("ftp://", "https://")
    except AttributeError:
        print(f"Failed to download {pmc_id} - No link found")
        return False
    file_path = os.path.join(directory, f"{pmc_id}.tar.gz")
    urllib.request.urlretrieve(tgz_link, file_path)
    return True


def download_supplementary_tar_gz_no_retries(pmc_id: str, directory: str) -> bool:
    api_url = f"https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id={pmc_id}"
    response = requests.get(api_url)
    if response.status_code != 200:
        print(f"Failed to download {pmc_id} - {response.status_code}")

        return False
    root = ET.fromstring(response.text)
    link_element = root.find(".//link[@format='tgz']")
    try:
        tgz_link = link_element.get("href").replace("ftp://", "https://")
    except AttributeError:
        print(f"Failed to download {pmc_id} - No link found")
        return False
    file_path = os.path.join(directory, f"{pmc_id}.tar.gz")
    urllib.request.urlretrieve(tgz_link, file_path)
    return True


def unpack_tar_gz(file_path: str, directory: str) -> None:
    with tarfile.open(file_path, "r:gz") as tar:
        tar.extractall(path=directory)


def parse_and_save_supplementary_for_pmc_id(
    pmc_id: str, output_directory_root: str
) -> None:
    with tempfile.TemporaryDirectory() as directory:
        if download_supplementary_tar_gz(pmc_id, directory):
            # unpack tar.gz
            # tempfile_save_directory = f"{directory}/{pmc_id}/parsed_supplementary/"
            tempfile_save_directory = os.path.join(
                directory, pmc_id, "parsed_supplementary"
            )
            output_directory = os.path.join(output_directory_root, pmc_id)
            unpack_tar_gz(f"{directory}/{pmc_id}.tar.gz", f"{directory}/{pmc_id}")
            grouped_files = group_files(f"{directory}/{pmc_id}/{pmc_id}/")
            os.makedirs(tempfile_save_directory, exist_ok=True)
            run_on_all_from_dict(pmc_id, grouped_files, tempfile_save_directory)
            print(os.listdir(tempfile_save_directory))
            os.makedirs(output_directory_root, exist_ok=True)
            shutil.copytree(tempfile_save_directory, output_directory)


def parse_supplementary_for_pmc_id(pmc_id: str) -> None:
    with tempfile.TemporaryDirectory() as directory:
        if download_supplementary_tar_gz(pmc_id, directory):
            unpack_tar_gz(f"{directory}/{pmc_id}.tar.gz", f"{directory}/{pmc_id}")
            grouped_files = group_files(f"{directory}/{pmc_id}/{pmc_id}/")
            results = run_on_all_from_dict_and_return(pmc_id, grouped_files)
            return results


# if __name__ == "__main__":
#     pmc_id = "PMC8192451"
#     output_directory_root = "make_some/directory/"
#     parse_and_save_supplementary_for_pmc_id(pmc_id, output_directory_root)
#     print("Done")


def run_on_all_pmc_ids_from_dir(
    dir_containing_pmc_ids, output_directory_root, pmc_group, max_workers=None
):
    # input directory has PMC123.json
    if not os.path.exists(output_directory_root):
        os.makedirs(output_directory_root)
    pmc_ids = list(map(lambda x: x.split(".")[0], os.listdir(dir_containing_pmc_ids)))

    pmc_ids = [
        pmc_id
        for pmc_id in pmc_ids
        if not os.path.exists(os.path.join(output_directory_root, pmc_id))
    ]
    # open error file and search for PMC ids that failed, include them in the list
    # with open(error_path, "r") as error_file:
    #     lines = error_file.readlines()
    #     for line in lines:
    #         if " | PMC" in line:
    #             pmc_id = line.split(" | ")[1]
    #             if "PMC" + pmc_id[3:-6].zfill(3) + "xxxxxx" == pmc_group:
    #                 pmc_ids.append(pmc_id)

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        INCREMENT = 10000
        lower = 0
        upper = INCREMENT
        while lower < len(pmc_ids):
            executor.map(
                parse_and_save_supplementary_for_pmc_id,
                pmc_ids[lower:upper],
                [output_directory_root] * (upper - lower),
                # [error_path] * len(pmc_ids),
            )
            lower = upper
            upper += INCREMENT
            if upper > len(pmc_ids):
                upper = len(pmc_ids)


def main():
    print("Starting")
    args = sys.argv[1:]
    input_dir = args[0]
    output_dir = args[1]
    try:
        max_workers = int(args[2])
    except:
        max_workers = None

    # error_path = args[2]
    PMC_GROUPS = [
        "PMC010xxxxxx",
        "PMC009xxxxxx",
        "PMC008xxxxxx",
        "PMC007xxxxxx",
        "PMC006xxxxxx",
        "PMC005xxxxxx",
        "PMC004xxxxxx",
        "PMC003xxxxxx",
        "PMC002xxxxxx",
        "PMC001xxxxxx",
        "PMC000xxxxxx",
    ]
    for PMC_GROUP in PMC_GROUPS:
        print("Starting with", PMC_GROUP)
        run_on_all_pmc_ids_from_dir(
            f"{input_dir}/{PMC_GROUP}/",
            f"{output_dir}/{PMC_GROUP}/",
            # error_path,
            PMC_GROUP,
            max_workers,
        )


def main_for_debuging():
    input_dir = "pipeline_preprocessing_debugging/input_1"
    output_dir = "pipeline_preprocessing_debugging/output_1"
    # error_path = "pipeline_preprocessing_debugging/error_1.log"

    run_on_all_pmc_ids_from_dir(f"{input_dir}/", f"{output_dir}/", "PMC003xxxxxx")


def run_on_set_of_pmcids():
    PMC_IDS = [
        # "PMC7947485",
        # "PMC7441158",
        # "PMC7933943",
        # "PMC7988717",
        # "PMC7455695",
        # "PMC7021553",
        # "PMC7734007",
        # "PMC7394438",
        # "PMC7348942",
        # "PMC7210010",
        "PMC7060178",
        # "PMC7535141",
        # "PMC7059190",
        # "PMC7210971",
        # "PMC7763932",
        # "PMC7492264",
        # "PMC7826616",
        # "PMC7054216",
        # "PMC7290068",
        # "PMC7791049",
        # "PMC5700166",
        # "PMC9005588",
        # "PMC9727330",
        # "PMC9665137",
        # "PMC9578258",
        # "PMC9676631",
        # "PMC9664718",
        # "PMC9918532",
        # "PMC9160072",
        # "PMC9817970",
        # "PMC9975667",
        # "PMC9877310",
        # "PMC9336482",
        # "PMC9449356",
        # "PMC9974098",
        # "PMC9746828",
        # "PMC9531306",
        # "PMC7873381",
        # "PMC7520348",
    ]

    # PMC_IDS = [
    #     # "PMC4336150",
    #     # "PMC4288352",
    #     # "PMC4104442",
    #     # "PMC4640665",
    # ]
    output_directory_root = "pipeline_preprocessing_debugging/output_pmc007_killed"
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        executor.map(
            parse_and_save_supplementary_for_pmc_id,
            PMC_IDS,
            [output_directory_root] * len(PMC_IDS),
        )


def run_on_pmc_list_from_file():
    with open("pipeline_preprocessing_debugging/pmc_list.txt", "r") as fp:
        pmc_list = [line.strip() for line in fp]
    output_directory_root = "pipeline_preprocessing_debugging/output_pmc_list"
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        executor.map(
            parse_and_save_supplementary_for_pmc_id,
            pmc_list,
            [output_directory_root] * len(pmc_list),
        )


def run_on_pmc_list_from_var_gen_dis_file(
    file_path: str, output_directory_root: str, max_workers=10
):
    import json

    print(os.path.exists(file_path), file_path)
    filename = file_path.split("/")[-1].split(".")[0]
    with open(file_path, "r") as fp:
        pmc_list = list(json.load(fp).keys())
        print(len(pmc_list), f"PMC ids in {filename}")
    # return
    OUTPUT_DIR = os.path.join(output_directory_root, filename, "output/")
    PMC_TRIGGERS_OUTPUT_DIR = os.path.join(output_directory_root, filename, "trigger/")
    PMC_ERRORS = os.path.join(output_directory_root, filename, "errors/")
    PMC_ERRORS_TRACEBACK = os.path.join(
        output_directory_root, filename, "errors_traceback/"
    )

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(PMC_TRIGGERS_OUTPUT_DIR, exist_ok=True)
    os.makedirs(PMC_ERRORS, exist_ok=True)
    os.makedirs(PMC_ERRORS_TRACEBACK, exist_ok=True)

    def wrapper(pmc_id, output):
        if os.path.exists(PMC_TRIGGERS_OUTPUT_DIR + pmc_id):
            return
        try:
            parse_and_save_supplementary_for_pmc_id(pmc_id, output)
        except FileExistsError as e:
            return
        except Exception as e:
            with open(PMC_ERRORS + pmc_id, "w") as fp:
                fp.write(f"{pmc_id} - {str(e)}")
                fp.write("\n")
            with open(PMC_ERRORS_TRACEBACK + pmc_id, "w") as fp:
                fp.write(f"{pmc_id} - {traceback.format_exc()}")
                fp.write("\n\n")
            # print(traceback.format_exc())
        else:
            # touch empty file to indicate completion
            with open(PMC_TRIGGERS_OUTPUT_DIR + pmc_id, "w") as fp:
                pass

    # pmc_list = [pmc_list[0]]
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(
            wrapper,
            pmc_list,
            [OUTPUT_DIR] * len(pmc_list),
        )


def run_on_pmc_list_from_var_gen_dis_file_from_outside():
    args = sys.argv[1:]
    file_path = args[0]
    output_directory_root = args[1]
    try:
        max_workers = int(args[2])
    except:
        max_workers = 10
    run_on_pmc_list_from_var_gen_dis_file(file_path, output_directory_root, max_workers)


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 0:
        print("No arguments provided")
        sys.exit(1)
    if args[0] == "run_on_pmc_list_from_var_gen_dis_file":
        run_on_pmc_list_from_var_gen_dis_file_from_outside()
        sys.exit(0)
    if args[0] == "parse_and_save_supplementary_for_pmc_id":
        parse_and_save_supplementary_for_pmc_id(args[1], args[2])
        sys.exit(0)
    # print("Starting")
    # run_on_set_of_pmcids()
    # main()
    run_on_pmc_list_from_var_gen_dis_file_from_outside()
    # main_for_debuging()
