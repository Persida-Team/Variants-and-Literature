from datetime import datetime
from functools import partial

from utils.filesystem_utils import file_exists

LOG_DIR = "logs/"

DOWNLOAD_XML_FAILED = LOG_DIR + "download_xml_failed.txt"
# DOWNLOAD_XML_SUCCESS = LOG_DIR + "download_xml_success.txt"
DOWNLOAD_TAR_GZ_FAILED = LOG_DIR + "download_tar_gz_failed.txt"
# DOWNLOAD_TAR_GZ_SUCCESS = LOG_DIR + "download_tar_gz_success.txt"
DOWNLOAD_FAILED = LOG_DIR + "download_failed.txt"
# DOWNLOAD_SUCCESS = LOG_DIR + "download_success.txt"
PARSE_FAILED = LOG_DIR + "parse_failed.txt"
# PARSE_SUCCESS = LOG_DIR + "parse_success.txt"
PMCID_NOT_IN_CSV = LOG_DIR + "pmcid_not_in_csv.txt"
PMID_NOT_IN_CSV = LOG_DIR + "pmid_not_in_csv.txt"


def add_timestamp() -> str:
    """
    Returns a timestamp

    :return: timestamp
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def error_message_prefix() -> str:
    """
    Returns the prefix for error messages

    :return: prefix for error messages
    """
    return "[ERROR]\t" + add_timestamp() + "\t"


def log(data: str, log_file: str, log_level: callable) -> None:
    """
    logs data to a file

    :param log_file: path to log file
    :param data: data to be logged
    """
    if not file_exists(log_file):
        with open(log_file, "w") as f:
            f.write(f"{log_level()}{data}\n")
    else:
        with open(log_file, "a") as f:
            f.write(f"{log_level()}{data}\n")


log_download_xml_failed = partial(log, log_file=DOWNLOAD_XML_FAILED)
# log_download_xml_success = partial(log, log_file=DOWNLOAD_XML_SUCCESS)
log_download_tar_gz_failed = partial(log, log_file=DOWNLOAD_TAR_GZ_FAILED)
# log_download_tar_gz_success = partial(log, log_file=DOWNLOAD_TAR_GZ_SUCCESS)
log_download_failed = partial(log, log_file=DOWNLOAD_FAILED)
# log_download_success = partial(log, log_file=DOWNLOAD_SUCCESS)
log_parse_failed = partial(log, log_file=PARSE_FAILED)
# log_parse_success = partial(log, log_file=PARSE_SUCCESS)
log_pmcid_not_in_csv = partial(log, log_file=PMCID_NOT_IN_CSV)
log_pmid_not_in_csv = partial(log, log_file=PMID_NOT_IN_CSV)


error_log_parse_failed = partial(log_parse_failed, log_level=error_message_prefix)