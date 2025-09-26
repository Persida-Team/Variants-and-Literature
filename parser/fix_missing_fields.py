"""

current missing fields are as follows:
- 'type'
- 'supplementary_list'

what needs to be done:
- provide a 2d tuple of paths, one for the xml and one for the parsed json.
- read the json file and check if the fields are missing.
- if the fields are missing, add them to the json file.
    - both fields should be contained in the xml file.
    - use **parse_article_type(root) and **parse_supplementary_list(root, file) to get the values.
    - reorganize json fields so they are in the correct order.
        -id
        -type
        -supplementary_list
        -title
        -abstract
        ...
- save the json file with the new fields added.

"""

import json
import os
import xml.etree.ElementTree as ET
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List

from pmc_xml_parser import parse_article_type, parse_supplementary_list


def fix_missing_fields(xml_path, json_path, save=True, override=True) -> bool:

    # for xml_path, json_path in xml_json_paths:
    with open(xml_path, "r", encoding="utf8") as f:
        tree = ET.parse(f)
        root = tree.getroot()
    with open(json_path, "r", encoding="utf8") as f:
        json_data = json.load(f)
    if (
        "type" not in json_data.keys()
        or "supplementary_material" not in json_data.keys()
        or override
    ):
        json_data.update(parse_article_type(root))
        json_data.update(parse_supplementary_list(root, xml_path))
        # reorded fields so type is second and supplementary_list is third
        json_data = {
            "ids": json_data["ids"],
            "type": json_data["type"],
            "supplementary_material": json_data["supplementary_material"],
            # the rest of keys are not guaranteed to be in the same order
            **{
                key: json_data[key]
                for key in json_data.keys()
                if key not in ["ids", "type", "supplementary_material"]
            },
        }
    if save:
        with open(json_path, "w", encoding="utf8") as f:
            json.dump(json_data, f, indent=4, ensure_ascii=False)
    else:
        print(json_data.keys())
        print(json_data["supplementary_material"])
        # print(parse_supplementary_list(root, xml_path))
    # raise Exception("Test")


def find_and_fix_files(xml_dir, json_dir):
    import time

    start = time.time()
    print(f"Searching for files in {xml_dir} and {json_dir}.")
    xml_files = sorted(f for f in os.listdir(xml_dir) if f.endswith(".xml"))
    json_files = sorted(f for f in os.listdir(json_dir) if f.endswith(".json"))

    xml_index, json_index = 0, 0
    pairs = []
    while xml_index < len(xml_files) and json_index < len(json_files):
        xml_file, json_file = xml_files[xml_index], json_files[json_index]
        if xml_file[:-4] == json_file[:-5]:  # Strip extensions and compare
            pairs.append(
                (os.path.join(xml_dir, xml_file), os.path.join(json_dir, json_file))
            )
            xml_index += 1
            json_index += 1
        elif xml_file < json_file:
            xml_index += 1
        else:
            json_index += 1
    print(f"Found {len(pairs)} pairs of files to fix.")
    with ProcessPoolExecutor(max_workers=10) as executor:
        # make subset of 100000 pairs to test
        INCREMENT = 10000
        lower = 0
        higher = INCREMENT
        # loop over increments
        while lower < len(pairs):
            pairs_to_work = pairs[lower:higher]

            futures = [
                executor.submit(fix_missing_fields, *pair) for pair in pairs_to_work
            ]
            for future in as_completed(futures):
                # Handle result or exceptions if needed
                # print(future.result())

                pass
            print(f"Fixed {higher} files.")
            lower = higher
            higher += INCREMENT

    print("All files have been fixed.")
    end = time.time()
    print(f"Time took: {end - start}")


def do_on_all_groups():
    AVAILABLE_GROUPS = [
        "PMC000xxxxxx",
        "PMC001xxxxxx",
        "PMC002xxxxxx",
        "PMC003xxxxxx",
        "PMC004xxxxxx",
        "PMC005xxxxxx",
        "PMC006xxxxxx",
        "PMC007xxxxxx",
        "PMC008xxxxxx",
        "PMC009xxxxxx",
        "PMC010xxxxxx",
        "PMC011xxxxxx",
    ]
    for group in AVAILABLE_GROUPS:
        xml_directory = f"../../PMC_articles/bulk/uncompressed/{group}"
        json_directory = f"../../PMC_articles/bulk/parsed/{group}"
        if not os.path.exists(xml_directory) or not os.path.exists(json_directory):
            print(f"Skipping {group} as directories do not exist.")
            continue
        find_and_fix_files(xml_directory, json_directory)


def debug():
    PMC_ID = "PMC4000008"
    xml_directory = f"../../PMC_articles/bulk/uncompressed/PMC004xxxxxx"
    json_directory = f"../../PMC_articles/bulk/parsed/PMC004xxxxxx"
    xml_path = f"{xml_directory}/{PMC_ID}.xml"
    json_path = f"{json_directory}/{PMC_ID}.json"
    fix_missing_fields(xml_path, json_path, save=False)


def do_one(pmc_id, save=True):
    xml_directory = f"../../PMC_articles/bulk/uncompressed/PMC009xxxxxx"
    json_directory = f"../../PMC_articles/bulk/parsed/PMC009xxxxxx"
    xml_path = f"{xml_directory}/{pmc_id}.xml"
    json_path = f"{json_directory}/{pmc_id}.json"
    fix_missing_fields(xml_path, json_path, save=save)

    ...


if __name__ == "__main__":
    do_on_all_groups()
    # pmc_id = "PMC9404646"
    # do_one(pmc_id)
    # debug()
# if __name__ == "__main__":
#     fix_missing_fields(
#         [
#             (
#                 "parser/fix_missing_fields/PMC29078.xml",
#                 "parser/fix_missing_fields/PMC29078.json",
#             )
#         ]
#     )
