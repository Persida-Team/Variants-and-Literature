import os
import time
from datetime import datetime, timezone
from json import JSONDecodeError

import requests
from dotenv import load_dotenv

from utils.logging.logging_setup import submission_info_logger
from w3c.utilities import (
    create_directory,
    create_uuid_for_submission,
    get_files,
    load_json,
    save_json,
)

load_dotenv()


TOKEN_GENERATOR = os.getenv("SUBMIT_TOKEN_GENERATOR", None)
SUBMIT_URL = os.getenv("SUBMIT_URL", None)

event_type = os.getenv("SUBMIT_EVENT_TYPE", None)
event_name = os.getenv("SUBMIT_EVENT_NAME", None)
event_triggered_by_host = os.getenv("SUBMIT_EVENT_TRIGGERED_BY_HOST", None)
event_triggered_by_id = os.getenv("SUBMIT_EVENT_TRIGGERED_BY_ID", None)
event_triggered_by_iri = os.getenv("SUBMIT_EVENT_TRIGGERED_BY_IRI", None)
if not event_type:
    raise Exception("SUBMIT_EVENT_TYPE is not set in env file.")
if not event_name:
    raise Exception("SUBMIT_EVENT_NAME is not set in env file.")
if not event_triggered_by_host:
    raise Exception("SUBMIT_EVENT_TRIGGERED_BY_HOST is not set in env file.")
if not event_triggered_by_id:
    raise Exception("SUBMIT_EVENT_TRIGGERED_BY_ID is not set in env file.")
if not event_triggered_by_iri:
    raise Exception("SUBMIT_EVENT_TRIGGERED_BY_IRI is not set in env file.")


def prepare_event(pmc: str):
    event = {}
    event["type"] = event_type
    event["name"] = event_name
    event["uuid"] = create_uuid_for_submission()
    event["sbj"] = {}
    event["sbj"]["id"] = pmc
    event["sbj"]["iri"] = ""
    event["triggered"] = {}
    event["triggered"]["by"] = {}
    event["triggered"]["by"]["host"] = event_name
    event["triggered"]["by"]["id"] = event_triggered_by_id
    event["triggered"]["by"]["iri"] = event_triggered_by_iri
    event["triggered"]["at"] = (
        datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )
    return event


def submit_result(data: dict, token: str, pmc: str, max_retries=5, timeout=60):
    token_full = "Bearer " + token
    head = {"Authorization": token_full, "Content-Type": "application/json"}
    for attempt in range(max_retries):
        try:
            temp_res = requests.put(
                SUBMIT_URL, headers=head, json=data, timeout=timeout
            )
            res = temp_res.json()
            status_message = str(res["status"]["code"])
            submission_info_logger.info(
                f"{pmc} - Finished with status code: " + status_message
            )

            return res

        except requests.exceptions.Timeout as e:
            submission_info_logger.info(
                f"{pmc} - Attempt {attempt + 1} - TimeoutError - {e}"
            )
            if attempt < max_retries - 1:
                time.sleep(2**attempt)  # Exponential backoff
            else:
                raise
        except JSONDecodeError as e:
            status_message = f"JSONDecodeError - {e} - {temp_res}"
            submission_info_logger.info(
                f"{pmc} - Finished with status code: " + status_message
            )
            return None


def generate_token():
    data = {"type": "plain", "val": "literatura"}
    head = {"Content-Type": "application/json"}
    res = requests.post(TOKEN_GENERATOR, headers=head, json=data).json()
    return res["data"]["jwt"]


def submission(pmc: str, data: list, out_folder: str, token: str, group: str):
    submit = {}
    submit["event"] = prepare_event(pmc)
    submit["content"] = {}
    # data_without_body = []
    # for one_data in data:
    #     if "body" in one_data:
    #         continue
    #     else:
    #         data_without_body.append(one_data)
    if len(data) > 0:
        submit["content"]["annotations"] = data
    if len(data) > 0:
        output_directory = out_folder + "/" + group + "/"
        create_directory(output_directory)
        submit["content"]["annotations"] = data
        save_json(submit, output_directory + pmc + "_submitted.json")
        response = submit_result(submit, token, pmc)
        if isinstance(response, dict):
            save_json(response, output_directory + pmc + "_submitted_response.json")
        # else:
        #     with open (out_folder + pmc + "_error_response.json", "w") as fp:
        #         fp.write(response)
    else:
        submission_info_logger.info(pmc + " - no valid annotations for submission.")


def generate_submission_file(pmc: str, data: list) -> dict:
    """
    Generate a submission file for a given PMCID and data.
    Args:
        pmc (str): The PMCID of the publication.
        data (list): The data to be included in the submission.
    Returns:
        dict: A dictionary representing the submission file.
    """
    if not data:
        return {}
        # raise ValueError("Data cannot be empty for submission.")
    submission_file = {"event": prepare_event(pmc), "content": {"annotations": data}}
    return submission_file


def submission_all_data_in_folder(in_folder: str, out_folder: str, group: str):
    files = get_files(in_folder)
    create_directory(out_folder)
    token = generate_token()
    token_time = datetime.now()
    submission_info_logger.info("Token: " + token + "\n" + "Time: " + str(token_time))
    for link in files:
        for file in files[link]:
            pmc = file.split(".")[0]
            if os.path.exists(out_folder + pmc + "_submitted_response.json"):
                continue
            data = load_json(link + file)
            submission_info_logger.info(file)
            if (datetime.now() - token_time).days > 0:
                token = generate_token()
                token_time = datetime.now()
                submission_info_logger.info(
                    "Token: " + token + "\n" + "Time: " + str(token_time)
                )

            submission(pmc, data, out_folder, token, group)


def submit_one_article_from_w3c(pmc_id, w3c_document, output_path):
    group = "PMC" + pmc_id[3:-6].zfill(3) + "xxxxxx"
    token = generate_token()
    submission(pmc_id, w3c_document, output_path, token, group)


def submit_something():
    OVERRIDE = True
    INPUT_PATH = "./results/300k/"
    OUTPUT_PATH = "./results/300k_submitted/"
    PMC_LIST = [
        "PMC3073906",
        "PMC3560267",
        "PMC3605834",
        "PMC3814312",
        "PMC3832360",
        "PMC3858560",
        "PMC3974641",
        "PMC5066235",
        "PMC5507568",
        "PMC5560704",
        "PMC5598015",
        "PMC6003537",
        "PMC6118300",
        "PMC6244569",
        "PMC6245352",
        "PMC6590666",
        "PMC6735957",
        "PMC6748966",
        "PMC6923336",
        "PMC7400765",
        "PMC7545610",
        "PMC7837267",
        "PMC7880356",
        "PMC8012150",
        "PMC8128300",
        "PMC8150312",
        "PMC8196904",
        "PMC8326839",
        "PMC8360745",
        "PMC8468204",
        "PMC8535342",
        "PMC8706866",
        "PMC8780329",
        "PMC8882989",
    ]
    token = generate_token()
    token_time = datetime.now()
    create_directory(OUTPUT_PATH)
    for pmc in PMC_LIST:
        group = "PMC" + pmc[3:-6].zfill(3) + "xxxxxx"
        path_to_file = os.path.join(INPUT_PATH, group, pmc + "_w3c.json")
        print(path_to_file, os.path.exists(path_to_file))
        if not OVERRIDE and os.path.exists(
            OUTPUT_PATH + pmc + "_submitted_response.json"
        ):
            continue
        data = load_json(path_to_file)
        submission_info_logger.info(pmc + "_w3c.json")

        if (datetime.now() - token_time).days > 0:
            token = generate_token()
            token_time = datetime.now()
            submission_info_logger.info(
                "Token: " + token + "\n" + "Time: " + str(token_time)
            )

        submission(pmc, data, OUTPUT_PATH, token, group)


def submit_directory(input_path, output_path):
    OVERRIDE = True
    token = generate_token()
    token_time = datetime.now()
    create_directory(output_path)
    # walk input_path and submit all json files
    for root, dirs, files in os.walk(input_path):
        for file in files:
            if not file.endswith(".json"):
                continue
            if not OVERRIDE and os.path.exists(
                output_path + file.split(".")[0] + "_submitted_response.json"
            ):
                continue
            # if file not in ["PMC9014219_w3c.json", "PMC8678088_w3c.json"]:
            #     continue
            data = load_json(os.path.join(root, file))
            group = "PMC" + file.split("_")[0][3:-6].zfill(3) + "xxxxxx"
            submission_info_logger.info(file.split("_")[0])
            if (datetime.now() - token_time).days > 0:
                token = generate_token()
                token_time = datetime.now()
                submission_info_logger.info(
                    "Token: " + token + "\n" + "Time: " + str(token_time)
                )

            submission(file.split(".")[0], data, output_path, token, group)


if __name__ == "__main__":
    # data = load_json("example_result.json")
    # submission("PMC2001184", data, "./submitted/")
    # submit_something()
    paths = [
        (
            "/home/novak/Clingen/pipeline/automate/test_output/300k/",
            "/home/novak/Clingen/pipeline/automate/test_output/300k_w3c_submitted/",
        ),
        (
            "/home/novak/Clingen/pipeline/automate/test_output/300k_plus/",
            "/home/novak/Clingen/pipeline/automate/test_output/300k_plus_w3c_submitted/",
        ),
        # ("results/300k_w3c/", "results/300k_w3c_submitted/"),
        # ("results/300k_plus_w3c/", "results/300k_plus_w3c_submitted/"),
    ]
    for input_path, output_path in paths:
        submit_directory(input_path, output_path)
