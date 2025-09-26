import json
import os
import queue
import threading

from parser.pmc_txt_parser import parse_text_to_string
from parser.pmc_xml_parser import parse_article as xml_parse_article
from parser.table_parser import extract_data as table_parse_article
from utils.filesystem_utils import check_if_files_exist
from utils.logging.logging_setup import parsing_info_logger, parsing_error_logger

def combine_xml_and_txt_no_save(xml_path: str, txt_path: str) -> dict:
    pmc_id = xml_path.split("/")[-1].split(".")[0]
    if not check_if_files_exist(xml_path, txt_path):
        parsing_info_logger.info("%s | xml or txt file does not exist", pmc_id)
        raise FileNotFoundError(f"{pmc_id}: xml or txt file does not exist")
    result = {
        **xml_parse_article(xml_path),
        **{"text": parse_text_to_string(txt_path)},
        **{"tables": table_parse_article(xml_path, pmc_id)},
    }
    return result

lock = threading.Lock()

def write_error(pmc_id, e, save_dir):
    with lock:
        parsing_error_logger.error(f"Error while processing {pmc_id}: {e}")
        with open(f"{save_dir}/../error.txt", "a") as f:
            f.write(f"{pmc_id}: {e}\n")


def combine_xml_and_txt(xml_path: str, txt_path: str, save_dir: str) -> dict:
    pmc_id = xml_path.split("/")[-1].split(".")[0]
    if not check_if_files_exist(xml_path, txt_path):
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        parsing_info_logger.info("%s | xml or txt file does not exist", pmc_id)
        raise FileNotFoundError(f"{pmc_id}: xml or txt file does not exist")
    result = {
        **xml_parse_article(xml_path),
        **{"text": parse_text_to_string(txt_path)},
        **{"tables": table_parse_article(xml_path, pmc_id)},
    }
    return result


def find_text_for_xml(xml_path: str, txt_path: str) -> str:
    return combine_xml_and_txt(xml_path, txt_path)


def do_one_article(pmc_id: str, txt_data_dir: str, xml_data_dir: str, save_dir: str):
    xml_path = f"{xml_data_dir}/{pmc_id}.xml"
    txt_path = f"{txt_data_dir}/{pmc_id}.txt"
    result = combine_xml_and_txt(xml_path, txt_path, save_dir)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    with open(f"{save_dir}/{pmc_id}.json", "w", encoding="utf8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)


def do_one_article_with_logging(
    pmc_id: str, txt_data_dir: str, xml_data_dir: str, save_dir: str
):
    try:
        do_one_article(pmc_id, txt_data_dir, xml_data_dir, save_dir)
    except Exception as e:
        parsing_error_logger.error(f"%s | %s | %s", pmc_id, str(e), save_dir, exc_info=True)
        return False
    return True


def do_one_article_parallel(pmc_id, txt_data_dir, xml_data_dir, save_dir):
    try:
        do_one_article(pmc_id, txt_data_dir, xml_data_dir, save_dir)
    except Exception as e:
        parsing_error_logger.error(f"%s | %s | %s", pmc_id, str(e), save_dir, exc_info=True)
        return False
    return True


# Function to parse a single file (to be run in threads)
def parse_file(file, lock):
    # Simulate file parsing
    pmc_id, txt_data_dir, xml_data_dir, save_dir = file
    with lock:
        do_one_article_with_logging(pmc_id, txt_data_dir, xml_data_dir, save_dir)


# Worker function that each thread will run
def worker(file_queue, lock):
    while not file_queue.empty():
        try:
            # Get a file from the queue
            file = file_queue.get_nowait()
            parse_file(file, lock)
        except queue.Empty:
            break  # Queue is empty, exit the worker


# Function to run the file parsing in parallel threads
def run_file_parsing_in_threads(file_list, num_threads):
    # Create a queue to hold the files
    file_queue = queue.Queue()

    # Put all files into the queue
    for file in file_list:
        file_queue.put(file)

    # Create a lock for thread-safe operations
    lock = threading.Lock()

    # List to hold the thread objects
    threads = []

    # Start each thread
    for _ in range(num_threads):
        thread = threading.Thread(target=worker, args=(file_queue, lock))
        thread.start()
        threads.append(thread)

    # Wait for all threads to finish
    for thread in threads:
        thread.join()


def do_all_in_threads(
    pmc_ids, txt_data_dir, xml_data_dir, save_dir, pmc_number, num_threads
):
    file_list = [(pmc_id, txt_data_dir, xml_data_dir, save_dir) for pmc_id in pmc_ids]
    run_file_parsing_in_threads(file_list, num_threads)


if __name__ == "__main__":
    pass
