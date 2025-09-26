import os
import sys


import re

from utils.filesystem_utils import open_txt_file


def parse_body(full_text: str) -> str:
    """
    Parse the body of the article from the full text of the article

    :param full_text: full text of the article
    :return: the body of the article (containing tables)
    """
    try:
        return full_text.split("==== Body")[1].split("==== Refs")[0]
    except IndexError:
        # the article does not contain the body section (probably odd formatting),
        # so return the full text without the references
        return full_text.split("REFERENCES")[0]
        


def parse_text_to_string(file_path: str) -> str:
    """
    Convert the text from a file into a json object

    :param file_path: path to the file
    :return: a string object containing the body text from the file
    """
    full_text = re.sub(
        r"\t", "    ", re.sub(r"\n+", " ", parse_body(open_txt_file(file_path)))
    ).strip()
    return full_text
