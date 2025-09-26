import json
from parser.combined_parsing import combine_xml_and_txt_no_save

import pandas as pd
from db.pubtator.db_queries import get_full_related_data
from db.pubtator.VARIABLES import get_session
from supplementary.tests.pipeline_preprocessing import parse_supplementary_for_pmc_id
from variant_search.search import (
    do_one_article_w_diseases_automation,
    raw_search_one_article,
)
from w3c.create_w3c_document import prepare_one_w3c
from w3c.format_check import format_check
from w3c.prepare_for_submittion import generate_submission_file
from dotenv import load_dotenv
import os 
load_dotenv()
OUTPUT_DIR = os.getenv("PIPELINE_OUTPUT_DIR", None)
if not OUTPUT_DIR:
    raise Exception("PIPELINE_OUTPUT_DIR variable not set in env file.")


def generate_path(pmc_id: str) -> str:
    """
    Generate the path prefix for the XML and TXT files based on the PMC ID.
    """
    pmc_group = "PMC" + pmc_id[3:-6].zfill(3) + "xxxxxx"
    return f"/home/novak/Clingen/PMC_articles/bulk/uncompressed/{pmc_group}/{pmc_id}"


def do_one_article(pmc_id: str):
    path_prefix = generate_path(pmc_id)
    xml_path = path_prefix + ".xml"
    txt_path = path_prefix + ".txt"

    try:
        text_parsing_result = combine_xml_and_txt_no_save(xml_path, txt_path)
    except FileNotFoundError:
        print(f"Files for {pmc_id} not found. Skipping.")
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
        return
    # TODO: generate w3c
    w3c_document = prepare_one_w3c(searched_data, pmc_id)
    submission_file = generate_submission_file(pmc_id, w3c_document)
    # with open(OUTPUT_DIR + f"{pmc_id}_parsed_data.json", "w") as f:
    #     json.dump(text_parsing_result, f, indent=4)
    # with open(OUTPUT_DIR + f"{pmc_id}_searched_data.json", "w") as f:
    #     json.dump(searched_data, f, indent=4)
    # with open(OUTPUT_DIR + f"{pmc_id}_w3c_document_for_submission.json", "w") as f:
    #     json.dump(submission_file, f, indent=4)
    # with open(OUTPUT_DIR + f"{pmc_id}_w3c_document.json", "w") as f:
    #     json.dump(w3c_document, f, indent=4)
    # with open(OUTPUT_DIR + f"{pmc_id}_pubtator.json", "w") as f:
    #     json.dump(pubtator_data, f, indent=4)
    # print(submission_file)
    # print(format_check(submission_file))
    if not format_check(submission_file):
        print("OBJECT NOT IN GOOD FORMAT: TODO: something about this")
        return

    # w3c_document = generate_w3c_document(searched_data, ...)
    # submit_w3c_document(w3c_document, ...)
    # TODO: submit

    with open(OUTPUT_DIR + f"{pmc_id}_w3c_document_for_submission.json", "w") as f:
        json.dump(submission_file, f, indent=4)


# x = parse_supplementary_for_pmc_id("PMC4826182")
# print(x.keys())

# if __name__ == "__main__":
#     pmc_ids = [
#     "PMC4580381",
#     "PMC7569700",
#     "PMC8180858",
#     ]
#     OUTPUT_DIR = "/home/novak/Clingen/repo_to_send/test_outputs/some_missing_w3c_files/"
#     for i, pmc_id in enumerate(pmc_ids,1):
#         # if i > 1:
#         #     break
#         do_one_article(pmc_id)
        
# def abc():
if __name__ == "__main__":
    # import time
    # for i in range(600):
    #     print(f"waiting\t{i}/600", end="\r")
    #     time.sleep(1)
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
            do_one_article(pmc_id)

    # do_one_article("PMC1702556")
