import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

from utils.logging.logging_setup import w3c_info_logger
from w3c.article_info import (
    create_exact_based_on_pattern,
    create_starting_part_w3c,
    reformat_article_info_data,
)
from w3c.body import collect_w3c_body_per_pmcid, collect_w3c_body_per_pmcid_in_temp_dir
from w3c.supplementary import add_supplementary_data
from w3c.target import add_table_data, create_target_table, create_target_text
from w3c.utilities import load_json


def prepare_one_w3c_textual(one_variant: dict, pmcid: str, article_info: dict) -> list:
    """
    Prepare W3C document for one variant search result from textual data
    Args:
        one_variant (dict): The variant search result information.
        pmcid (str): The PMCID of the article.
        article_info (dict): Starting part of the W3C document.
    Returns:
        list: A list containing the prepared W3C annotation from textual search result data.
    """
    result = []
    exact_in_text = one_variant["exact_match"]
    temp = create_starting_part_w3c(pmcid, exact_in_text, article_info)
    temp2 = {}
    temp2["source"] = "https://www.ncbi.nlm.nih.gov/pmc/articles/" + pmcid
    temp2["selector"] = create_target_text(exact_in_text, one_variant)
    if len(temp2["selector"]) > 0:
        temp["target"]["items"].append(temp2)
    if len(temp["target"]["items"]) > 0:
        result.append(temp)
    return result


def prepare_one_w3c_tabular(sec_variant, pmcid, article_info):
    """
    Prepare a W3C document for one variant search result from textual data, or update if variant already appears in textual search results.
    Args:
        sec_variant (dict): The variant search result information.
        pmcid (str): The PMCID of the publication.
        article_info (dict): Starting part of the W3C document.
    Returns:
        list: A list containing the prepared/updated W3C annotation from tabular search result data.
    """
    result = []
    exact_in_text = sec_variant["exact_match"]
    temp = create_starting_part_w3c(pmcid, exact_in_text, article_info)
    temp2 = {}
    temp2["source"] = "https://www.ncbi.nlm.nih.gov/pmc/articles/" + pmcid
    temp2["selector"] = create_target_table(exact_in_text, sec_variant["tables"])
    if len(temp2["selector"]) > 0:
        temp["target"]["items"] += [temp2]
    if len(temp["target"]["items"]) > 0:
        result += [temp]
    return result


def prepare_one_w3c(data: dict, pmcid: str):
    w3c_info_logger.info(f"Started preparing {pmcid}")
    result = []
    article_info = reformat_article_info_data(data)
    # collect_w3c_body_per_pmcid(data, pmcid)
    collect_w3c_body_per_pmcid_in_temp_dir(data, pmcid)
    textuals = data["searches"]["textual"]
    tabulars = data["searches"]["tabular"]
    supplementaries = data["searches"]["supplementary"]
    local_variants = []
    for one_variant in textuals:
        exact_match = one_variant["exact_match"]
        exact = create_exact_based_on_pattern(exact_match)
        result += prepare_one_w3c_textual(one_variant, pmcid, article_info)
    for res in result:
        local_variants.append(res["variantMatch"])
    for sec_variant in tabulars:
        exact_match = sec_variant["exact_match"]
        exact = create_exact_based_on_pattern(exact_match)
        if exact in local_variants:
            result = add_table_data(exact, sec_variant, result)
        else:
            result += prepare_one_w3c_tabular(sec_variant, pmcid, article_info)
    if len(supplementaries) > 0:
        add_supplementary_data(pmcid, result, article_info, supplementaries)
    w3c_info_logger.info(f"Finished preparing {pmcid}")
    return result


def do_110k():
    SEARCHED_ARTICLES_PATH = "../variant_search/110k/"
    # recursive search for all files in the directory


def create_w3c_for_one_pmc():
    args = sys.argv

    pmc_id = args[2]
    searched_path = args[3]
    output_path = args[4]
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    data = load_json(searched_path)
    prepared_data = prepare_one_w3c(data, pmc_id)
    with open(output_path, "w") as f:
        json.dump(prepared_data, f, indent=4)


def process_file(output_sup_dir, root, file):
    pmc_id = file.split("_")[0]
    searched_path = os.path.join(root, file)
    data = load_json(searched_path)
    group = "PMC" + pmc_id[3:-6].zfill(3) + "xxxxxx"
    group_dir = os.path.join(output_sup_dir, group)
    file_name = pmc_id + "_w3c.json"
    output_path = os.path.join(group_dir, file_name)
    if os.path.exists(output_path):
        return
    prepared_data = prepare_one_w3c(data, pmc_id)
    if not os.path.exists(group_dir):
        os.makedirs(group_dir)
    with open(output_path, "w") as f:
        json.dump(prepared_data, f, indent=4)


def process_directory(search_dir):
    k_dir = search_dir.split("/")[-2]
    output_sup_dir = f"./results/{k_dir}_w3c/"
    if not os.path.exists(output_sup_dir):
        os.makedirs(output_sup_dir)
    # skip existing files in output directory

    already_processed = []
    for root, dirs, files in os.walk(output_sup_dir):
        for file in files:
            pmc_id = file.split("_")[0]
            already_processed.append(pmc_id)

    # for root, dirs, files in os.walk(search_dir):
    #     for file in files:
    #         pmc_id = file.split("_")[0]
    #         if pmc_id in already_processed:
    #             continue
    #         process_file(output_sup_dir, root, file)

    tasks = []
    with ThreadPoolExecutor() as executor:
        for root, dirs, files in os.walk(search_dir):
            for file in files:
                pmc_id = file.split("_")[0]
                if pmc_id in already_processed:
                    continue
                task = executor.submit(process_file, output_sup_dir, root, file)
                tasks.append(task)
    # Ensure all tasks are complete
    for task in tasks:
        task.result()


if __name__ == "__main__":

    args = sys.argv
    function_to_call = args[1]
    if function_to_call == "create_w3c_for_one_pmc":
        create_w3c_for_one_pmc()
    # else:
    # """
    else:

        search_dirs = [
            "/home/novak/Clingen/pipeline/variant_search/results/300k/",
            "/home/novak/Clingen/pipeline/variant_search/results/300k_plus/",
        ]
        for search_dir in search_dirs:
            process_directory(search_dir)

    # """
    # data = load_json("example.json")
    # temp = prepare_one_w3c(data, "PMC2001184")
    # save_json(temp, "example_result.json")
