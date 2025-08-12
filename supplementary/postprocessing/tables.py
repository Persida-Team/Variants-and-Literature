import json
import os

# TODO: add extensions as we expand our support
EXTENSIONS = (
    "csv",
    "xls",
)

INPUT_PATH = "./outputs/"
INTERMEDIARY_FILES_PATH = (
    "./postprocessing/intermediary_files/pmcid_key_tables_value.json"
)
VARIANTS_FILE_PATH = (
    "./postprocessing/intermediary_files/Aggregated_by_pmcid_subset.json"
)
OUTPUT_FILE_PATH = "./postprocessing/intermediary_files/tables_final.json"

ROW_TYPE = dict[str, str]
TABLE_TYPE = dict[str, list[ROW_TYPE]]  # table_name -> rows


def get_file_paths() -> dict[int, list]:
    files = {}
    for pmc_dir in os.listdir(INPUT_PATH):
        pmc_key = get_pmc(pmc_dir)
        files[pmc_key] = []
        for file in os.listdir(INPUT_PATH + pmc_dir):
            if file.endswith(EXTENSIONS):
                files[pmc_key].append(INPUT_PATH + pmc_dir + "/" + file)
    return files


def get_pmc(file_path: str) -> str:
    return file_path[3:]


def get_table_name(file_path: str) -> str:
    return file_path.split("/")[-1]  # .split("_")[0]


def create_pmc_key_tables_value(files: dict) -> dict[str, TABLE_TYPE]:
    tables = {}
    for pmc_key, file_paths in files.items():
        tables[pmc_key] = {}
        for file_path in file_paths:
            table_name = get_table_name(file_path)
            with open(file_path, "r") as supplementary_file:
                json_data = json.load(supplementary_file)
            table_contents = json_data["PMC" + pmc_key][table_name]["contents"]
            tables[pmc_key][table_name] = table_contents
    return tables


def save_pmc_key_tables_value(tables: dict[str, TABLE_TYPE]) -> None:
    with open(INTERMEDIARY_FILES_PATH, "w") as tables_file:
        json.dump(tables, tables_file, indent=4)


def find_exact_match(tables_final: dict, article_tables_dict: dict):
    result = {}
    for pmcid, table_dict in article_tables_dict.items():
        variants_dicts = tables_final[pmcid]
        # print(pmcid, table_dict, variants_dicts)
        # table_dict = {k.strip(): v for (k, v) in article_tables_dict[pmcid].items()}
        result[pmcid] = {}
        for variant, exact_match in variants_dicts.items():
            # print(variant, exact_match)
            # exact_match = variant_dict["exact_match"]
            if tables_data := find_exact_match_in_tables(table_dict, exact_match, {}):
                result[pmcid][variant] = {
                    "exact_match": exact_match,
                    "tables": tables_data,
                }
        if not result[pmcid]:
            del result[pmcid]

    return result


def find_exact_match_in_tables(tables_dict, exact_match, tables_final_dict):
    result = {}
    for table_label in tables_dict.keys():
        result[table_label] = handle_table_metadata(
            tables_dict, exact_match, table_label, {}
        )

    return result


def handle_table_metadata(tables_dict, exact_match, table_label, table_metadata):
    # if exact match is not a list of matches
    if not isinstance(exact_match, list):
        result = {}
        if in_column_header := find_exact_match_in_columns(
            tables_dict[table_label], exact_match
        ):
            result["found_in_column_header"] = in_column_header
        if in_rows := find_exact_match_in_rows(tables_dict[table_label], exact_match):
            result["found_in_rows"] = in_rows
        for key, value in table_metadata.items():
            if value:
                result[key] = value
        return {exact_match: result}

    # if exact match is a list of matches
    result = {}
    for match in exact_match:
        result[match] = {}
        if in_column_header := find_exact_match_in_columns(
            tables_dict[table_label], match
        ):
            result[match]["found_in_column_header"] = in_column_header
        if in_rows := find_exact_match_in_rows(tables_dict[table_label], match):
            result[match]["found_in_rows"] = in_rows
        for key, value in table_metadata.items():
            if value:
                result[match][key] = value
    return result


def find_exact_match_in_columns(table_rows, exact_match):
    try:
        columns = table_rows[0].keys()
    except IndexError:
        columns = []
    found_in = {}
    for column in columns:
        if exact_match in column:
            found_in[column] = list(map(lambda x: x[column], table_rows))
    if found_in:
        return found_in


def find_exact_match_in_rows(table_rows, exact_match):
    rows_to_return = []
    for row in table_rows:
        for key, value in row.items():
            # if exact_match in value: # TODO look into this -> TypeError: argument of type 'float' is not iterable
            if exact_match in str(value):  # TODO fix this
                rows_to_return.append(row)
    if rows_to_return:
        return filter_duplicates(rows_to_return)


def dict_to_tuple(d):
    """
    Convert a dictionary to a tuple of its items, sorted by key.
    """
    return tuple(sorted(d.items()))


def filter_duplicates(dictionaries):
    """
    Filter out duplicate dictionaries from a list of dictionaries.
    """
    unique_dictionaries = []
    seen = set()

    for d in dictionaries:
        t = dict_to_tuple(d)
        if t not in seen:
            seen.add(t)
            unique_dictionaries.append(d)

    return unique_dictionaries


def do_the_thing():
    """
    step 1:
        get all the file paths
    step 2:
        modify the input files so they resemble
        the format for table variant search
    step 3:
        save the modified files
    step 4:
        read the modified files and read the variants file
    step 5:
        perform variant search and save the results


    ps. uncomment the code below to test the functions on a small sample
    """
    # INTERMEDIARY_FILES_PATH = "./postprocessing/intermediary_files/test_tables.json"
    # VARIANTS_FILE_PATH = "./postprocessing/intermediary_files/test_variants.json"
    # OUTPUT_FILE_PATH = "./processed_data/test_tables_final.json"

    files = get_file_paths()
    tables = create_pmc_key_tables_value(files)
    save_pmc_key_tables_value(tables)

    with open(INTERMEDIARY_FILES_PATH, "r") as tables_file:
        tables = json.load(tables_file)
    with open(VARIANTS_FILE_PATH, "r") as variants_file:
        variants = json.load(variants_file)
    result = find_exact_match(tables_final=variants, article_tables_dict=tables)
    with open(OUTPUT_FILE_PATH, "w") as tables_final_file:
        json.dump(result, tables_final_file, indent=4)
    print("done")


if __name__ == "__main__":
    do_the_thing()
