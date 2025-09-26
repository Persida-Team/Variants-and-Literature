import json
import os
from enum import Enum

from dotenv import load_dotenv

from .data_fetching import create_directory

load_dotenv()
SUPPLEMENTARY_DOWNLOAD_DIRECTORY = os.getenv("SUPPLEMENTARY_DOWNLOAD_DIRECTORY", None)
if not SUPPLEMENTARY_DOWNLOAD_DIRECTORY:
    raise Exception("SUPPLEMENTARY_DOWNLOAD_DIRECTORY variable not set in env file.")


class OUTPUT_TYPE(Enum):
    TABLE = "table"
    TEXT = "text"
    PDF = "pdf"
    EXCEL = "excel"
    WORD = "doc"
    POWERPOINT = "powerpoint"
    IMAGE = "image"
    COMPRESSED_FILE = "compressed_file"
    UNKNOWN = "unknown"


OUTPUT_TYPE_DICT = {
    "csv": OUTPUT_TYPE.TABLE,
    "txt": OUTPUT_TYPE.TEXT,
    "xls": OUTPUT_TYPE.EXCEL,
    "xlsx": OUTPUT_TYPE.EXCEL,
    "doc": OUTPUT_TYPE.WORD,
    "docx": OUTPUT_TYPE.WORD,
    "pdf": OUTPUT_TYPE.PDF,
    "pptx": OUTPUT_TYPE.POWERPOINT,
    "ppt": OUTPUT_TYPE.POWERPOINT,
    "png": OUTPUT_TYPE.IMAGE,
    "jpeg": OUTPUT_TYPE.IMAGE,
    "jpg": OUTPUT_TYPE.IMAGE,
    "tiff": OUTPUT_TYPE.IMAGE,
    "tif": OUTPUT_TYPE.IMAGE,
    "zip": OUTPUT_TYPE.COMPRESSED_FILE,
}


def get_output_type(file_extension: str) -> OUTPUT_TYPE:
    return OUTPUT_TYPE_DICT.get(file_extension, OUTPUT_TYPE.UNKNOWN)


def save(
    pmcid: str,
    material_filename: str,
    data: dict | str | list[dict | str],
    type: OUTPUT_TYPE,  # = OUTPUT_TYPE.TABLE,
) -> None:
    if not data:
        print(f"Skipping {material_filename} as it has no data")
        return
    output_directory = os.path.join(SUPPLEMENTARY_DOWNLOAD_DIRECTORY, pmcid)
    create_directory(output_directory)
    output_path = os.path.join(output_directory, material_filename) + ".json"
    to_save_data = {
        pmcid: {
            material_filename: {
                "type": type.value,
                "contents": data,
            },
        },
    }
    # print(f"Saving {output_path}")
    with open(output_path, "w") as output_file:
        json.dump(to_save_data, output_file, indent=4, default=str)


def pack_result(
    existing_contents: dict,
    material_filename: str,
    data: dict | str | list[dict | str],
    extension: str,
) -> dict:
    existing_contents[material_filename] = {
        "type": get_output_type(extension).value,
        "contents": data,
    }
    return existing_contents


if __name__ == "__main__":
    ...
