import os

from pmc_txt_parser import parse_text_to_string
from pmc_xml_parser import parse_article as xml_parse_article
from table_parser import extract_data as table_parse_article
from utils.filesystem_utils import check_if_files_exist
from utils.logging.logger_setup import parsing_info_logger

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