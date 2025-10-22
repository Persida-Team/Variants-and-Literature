import json
import os
from parser.combined_parsing import combine_xml_and_txt_no_save

import pandas as pd
from db.pubtator.db_queries import get_full_related_data
from db.pubtator.VARIABLES import get_session
from dotenv import load_dotenv
from supplementary.tests.pipeline_preprocessing import parse_supplementary_for_pmc_id
from utils.logging.logging_setup import main_error_logger, main_info_logger
from variant_search.search import (
    do_one_article_w_diseases_automation,
    raw_search_one_article,
)
from w3c.create_w3c_document import prepare_one_w3c
from w3c.format_check import format_check
from w3c.prepare_for_submittion import (
    generate_submission_file,
    submit_one_article_from_w3c,
)

load_dotenv()

OUTPUT_DIR = os.getenv("PIPELINE_OUTPUT_DIR", None)
UNCOMPRESSED_ARTICLES_DIR = os.getenv("UNCOMPRESSED_ARTICLES_DIR", None)
if not OUTPUT_DIR:
    raise Exception("PIPELINE_OUTPUT_DIR variable not set in env file.")
if not UNCOMPRESSED_ARTICLES_DIR:
    raise Exception("UNCOMPRESSED_ARTICLES_DIR variable not set in env file.")


def generate_path(pmc_id: str) -> str:
    """
    Generate the path prefix for the XML and TXT files based on the PMC ID.
    """
    pmc_group = "PMC" + pmc_id[3:-6].zfill(3) + "xxxxxx"
    return f"{UNCOMPRESSED_ARTICLES_DIR}/{pmc_group}/{pmc_id}"


def do_one_article(pmc_id: str, submission_out_dir: str):
    path_prefix = generate_path(pmc_id)
    xml_path = path_prefix + ".xml"
    txt_path = path_prefix + ".txt"

    try:
        text_parsing_result = combine_xml_and_txt_no_save(xml_path, txt_path)
    except FileNotFoundError:
        main_info_logger.info(f"Files for {pmc_id} not found. Skipping.")
        return

    supplementary_parsing_results = parse_supplementary_for_pmc_id(pmc_id)
    # supplementary_parsing_results = {}
    with get_session() as session:
        pubtator_data = get_full_related_data(
            session=session, entity_type="article", field="pmc_id", value=pmc_id
        )
    searched_data = do_one_article_w_diseases_automation(
        pmc_id=pmc_id,
        article_data=text_parsing_result,
        supplementary_data=supplementary_parsing_results,
        pubtator_data=pubtator_data,
    )
    if not searched_data:
        main_info_logger.info(f"No searched data for {pmc_id}.")
        return

    w3c_document = prepare_one_w3c(searched_data, pmc_id)
    submission_file = generate_submission_file(pmc_id, w3c_document)
    if not format_check(submission_file):
        main_info_logger.info(f"Submission file not in good format for {pmc_id}")
        return

    submit_one_article_from_w3c(pmc_id, w3c_document, submission_out_dir)


def abc():
    input_output = [
        (
            "/home/novak/Clingen/repo_to_send/test_outputs/pmc_list_512_articles_with_ours_null",
            "/home/novak/Clingen/repo_to_send/test_outputs/512_articles_with_ours_null_new_new/",
        ),
        (
            "/home/novak/Clingen/repo_to_send/test_outputs/200_plus_articles_with_ours_something.txt",
            "/home/novak/Clingen/repo_to_send/test_outputs/200_plus_articles_with_ours_something_new_new/",
        ),
    ]
    for INPUT_DIR, OUTPUT_DIR in input_output:
        # from w3c.prepare_for_submittion import submit_directory
        # submit_directory(OUTPUT_DIR, OUTPUT_DIR)

        with open(
            INPUT_DIR,
            "r",
        ) as f:
            pmc_ids = f.read().splitlines()
        l = len(pmc_ids)
        for i, pmc_id in enumerate(pmc_ids):
            print(f"{i}/{l} - {pmc_id}")
            # if i > 2:
            #     break
            # if pmc_id != "PMC1702556":
            #     continue
            do_one_article(pmc_id, OUTPUT_DIR)

    # do_one_article("PMC1702556")


if __name__ == "__main__":
    print("main done")
    pmc_ids_file_path = (
        "/home/novak/Clingen/PMC_articles/bulk/uncompressed/all_pmc_ids_22_10_2025.txt"
    )
    with open(pmc_ids_file_path, "r") as fp:
        pmc_ids = fp.read().split("\n")

    for index, pmc_id in enumerate(pmc_ids, 0):
        try:
            do_one_article(pmc_id=pmc_id, submission_out_dir=OUTPUT_DIR)
        except Exception as e:
            main_error_logger.error(f"ID: {pmc_id}\tINDEX: {index}\t Exception: {e}")
