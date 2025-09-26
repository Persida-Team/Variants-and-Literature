import os
import shutil
from requests.models import Response
import pandas as pd
import tarfile
import json


def file_exists(path: str) -> bool:
    """
    Check if a file exists

    :param path: path to file
    :return: True if file exists, False otherwise
    """
    return os.path.exists(path)


def check_if_files_exist(xml_path: str, txt_path: str) -> bool:
    """
    Check if both xml and txt files exist

    :param xml_path: path to xml file
    :param txt_path: path to txt file
    :return: True if both files exist, False otherwise
    """
    return os.path.exists(xml_path) and os.path.exists(txt_path)


def remove_file(filename: str) -> bool:
    """
    Remove a file if it exists

    :param filename: name of the file to be removed
    :return: True if file was removed, False otherwise
    """
    if os.path.isfile(filename):
        os.remove(filename)
        return True
    return False


def get_files(path: str) -> iter:
    """
    Get all files in a given directory

    :param path: path to directory
    :return: iterator of files
    """
    return (f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)))


def remove_files(path: str, condition: callable, skip: list = []) -> None:
    """
    Remove all files in a given directory that satisfies a given condition

    :param path: path to directory
    :param condition: condition to filter files
    :return: None
    """
    files = get_files(path)
    for f in files:
        if condition(f) and f not in skip:
            remove_file(os.path.join(path, f))


def remove_tar_gzs(path: str, skip: list = []) -> None:
    """
    Remove all tar.gz files in a given directory

    :param path: path to directory
    :return: None
    """
    remove_files(path, lambda x, y: x.endswith(".tar.gz") and x not in y, skip=skip)


def remove_dir(path: str) -> None:
    """
    Remove a directory if it exists

    :param path: path to directory
    :return: None
    """
    if os.path.isdir(path):
        shutil.rmtree(path)


def is_non_essential(filename: str) -> bool:
    """
    If the file is .csv and is not a formatted file, remove it

    :param filename: name of the file to be filtered
    :return: True if file should be removed, False otherwise
    """
    return filename.endswith(".csv")


def create_dir(path: str) -> None:
    """
    Create a directory if it doesn't exist

    :param path: path to directory
    :return: None
    """
    if not os.path.isdir(path):
        os.mkdir(path)


def save_csv(df: pd.DataFrame, file_name: str) -> None:
    """
    Save a pandas DataFrame to a csv file

    :param df: pandas DataFrame
    :param file_name: name of the csv file
    :return: None
    """
    df.to_csv(file_name, index=False)


def open_csv(file_name: str, sep: str = ",") -> pd.DataFrame:
    """
    Open a csv file and return a pandas DataFrame

    :param file_name: name of the csv file
    :return: pandas DataFrame
    """
    return pd.read_csv(file_name, sep=sep)

def open_txt_file(file_name: str) -> str:
    """
    Open a txt file and return its contents

    :param file_name: name of the txt file
    :return: contents of the txt file
    """
    with open(file_name, "r", encoding="utf-8", errors="replace") as f:
        return f.read()

def save_tar_gz(res: Response, file_name: str, pwd: str) -> None:
    """
    Save a tar.gz file

    :param res: response from a request
    :param file_name: name of the file to be saved
    :param pwd: save directory path
    """
    with open(pwd + "/" + file_name, "wb") as f:
        f.write(res.raw.read())


def save_file(res: Response, file_name: str, pwd: str) -> None:
    """
    Save a file

    :param res: response from a request
    :param file_name: name of the file to be saved
    :param pwd: save directory path
    """
    with open(pwd + "/" + file_name, "w") as f:
        f.write(res.text)


def tar_ungzip(file_name: str, pwd: str) -> None:
    """
    Unzip a tar.gz file

    :param file_name: name of the file to be unzipped
    :param pwd: save directory path
    :return: None
    """
    with tarfile.open(pwd + "/" + file_name, "r:gz") as tar:
        tar.extractall(pwd)

def write_to_json(data: dict, file_name: str, pwd: str) -> None:
    """
    Write data to a json file

    :param data: data to be written
    :param file_name: name of the json file
    :param pwd: save directory path
    :return: None
    """
    with open(pwd + "/" + file_name, "w") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def open_json(file_name: str) -> list[dict]:
    """
    Open a json file and return its contents

    :param file_name: name of the json file
    :return: contents of the json file
    """
    with open(file_name, "r") as f:
        return json.load(f)

def get_article_path_pairs(
    article_pmc_id: str,
    data_path: str,
) -> tuple[str, str]:
    """
    Find the path of the txt and xml files for a given article pmc id
    
    :param article_pmc_id: pmc id of the article
    :param data_path: path to the data directory
    :return: tuple of paths to the txt and xml files
    """
    parent_dir = f"PMC{article_pmc_id[3:-6].zfill(3)}xxxxxx"
    txt_path = os.path.join(data_path, parent_dir, article_pmc_id + ".txt")
    xml_path = os.path.join(data_path, parent_dir, article_pmc_id + ".xml")
    return txt_path, xml_path

def main():
    pwd = "tmp"
    # file_name = "oa_other_txt.incr.2022-11-23.tar.gz"
    file_name = "oa_other_txt.incr.2022-11-24.tar.gz"

    # tar_ungzip(file_name, pwd)
    remove_tar_gzs(pwd)


if __name__ == "__main__":
    # main()
    pass
