import json
import logging
import os
import re
import traceback
from datetime import datetime
from typing import Pattern
import re

# add basic logging with date and time function name
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# save to a file
file_handler = logging.FileHandler("300k_searching.log")
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)


METADATA_FIELDS = [
    "ids",
    "type",
    "supplementary_material",
]

TEXTUAL_SEARCH_FIELDS = [
    "title",
    # "alternative_title",
    "abstract",
    # "alternative_abstract",
    "text",
]
TABLE_TEXTUAL_SEARCH_FIELDS = [
    "label",
    "caption",
    "table_wrap_foot",
]

SUPPLEMENTARY_PATTERNS = [
    re.compile("[\s]CA[0-9]{6,}"),
    re.compile("^CA[0-9]{6,}"),
    re.compile(",CA[0-9]{6,}"),
    re.compile("[\s]rs[0-9]+"),
    re.compile(",rs[0-9]+"),
    re.compile("rs[0-9]+[ ]?[ACGT][>/-][ACGT]"),
    re.compile("[ACGT][/>-][ACGT][- ]rs[0-9]+"),
    re.compile("rs[0-9]+[- ]?[ACGT][ ]?"),
    re.compile("([-]?[0-9]+[ ]?(ins|del|ins/del)[ ]?[ACGT]+)"),
    re.compile(" [0-9]*[+-]?[0-9]+[ ]?[ACGT][ ]?[>/-][ ]?[ACGT]"),
    re.compile(
        "(Ala|Arg|Asn|Asp|Asx|Cys|Glu|Gln|Glx|Gly|His|Ile|Leu|Lys|Met|Phe|Pro|Ser|Thr|Trp|Tyr|Val)[0-9]+ (to|at|with) (Ala|Arg|Asn|Asp|Asx|Cys|Glu|Gln|Glx|Gly|His|Ile|Leu|Lys|Met|Phe|Pro|Ser|Thr|Trp|Tyr|Val)"
    ),
    re.compile(
        "(Ala|Arg|Asn|Asp|Asx|Cys|Glu|Gln|Glx|Gly|His|Ile|Leu|Lys|Met|Phe|Pro|Ser|Thr|Trp|Tyr|Val)[0-9]+ (to|at|with) (alanine|arginine|asparagine|aspartic acid|cysteine|glutamic acid|glutamine|glycine|histidine|isoleucine|leucine|lysine|methionine|phenylalanine|proline|serine|threonine|tryptophan|tyrosine|valine)"
    ),
    re.compile(
        "((Ala|Arg|Asn|Asp|Asx|Cys|Glu|Gln|Glx|Gly|His|Ile|Leu|Lys|Met|Phe|Pro|Ser|Thr|Trp|Tyr|Val)[0-9]+(fs|FS|Fs))"
    ),
    re.compile("[ARNDCQEGHILKMFPOSUTWYV][0-9]+fs"),
    re.compile("[ACGT] to [ACGT] at [0-9]+"),
]


def validate_variant(data: str) -> bool:
    """
    Validate a variant based on certain patterns.
    Args:
        data (str): The variant data to be validated.
    Returns:
        bool: True if the data is a valid variant, False otherwise.
    """
    # print(data)
    if isinstance(data, tuple):
        # Convert tuple to string
        data = data[0]
    patterns = [
        re.findall("[\s]CA[0-9]{6,}", data),
        re.findall("^CA[0-9]{6,}", data),
        re.findall(",CA[0-9]{6,}", data),
        re.findall("[\s]rs[0-9]+", data),
        re.findall(",rs[0-9]+", data),
        re.findall("rs[0-9]+[ ]?[ACGT][>/-][ACGT]", data),
        re.findall("[ACGT][/>-][ACGT][- ]rs[0-9]+", data),
        re.findall("rs[0-9]+[- ]?[ACGT][ ]?", data),
        re.findall("([-]?[0-9]+[ ]?(ins|del|ins/del)[ ]?[ACGT]+)", data),
        re.findall(" [0-9]*[+-]?[0-9]+[ ]?[ACGT][ ]?[>/-][ ]?[ACGT]", data),
        re.findall(
            "(Ala|Arg|Asn|Asp|Asx|Cys|Glu|Gln|Glx|Gly|His|Ile|Leu|Lys|Met|Phe|Pro|Ser|Thr|Trp|Tyr|Val)[0-9]+ (to|at|with) (Ala|Arg|Asn|Asp|Asx|Cys|Glu|Gln|Glx|Gly|His|Ile|Leu|Lys|Met|Phe|Pro|Ser|Thr|Trp|Tyr|Val)",
            data,
        ),
        re.findall(
            "(Ala|Arg|Asn|Asp|Asx|Cys|Glu|Gln|Glx|Gly|His|Ile|Leu|Lys|Met|Phe|Pro|Ser|Thr|Trp|Tyr|Val)[0-9]+ (to|at|with) (alanine|arginine|asparagine|aspartic acid|cysteine|glutamic acid|glutamine|glycine|histidine|isoleucine|leucine|lysine|methionine|phenylalanine|proline|serine|threonine|tryptophan|tyrosine|valine)",
            data,
        ),
        re.findall(
            "((Ala|Arg|Asn|Asp|Asx|Cys|Glu|Gln|Glx|Gly|His|Ile|Leu|Lys|Met|Phe|Pro|Ser|Thr|Trp|Tyr|Val)[0-9]+(fs|FS|Fs))",
            data,
        ),
        re.findall("[ARNDCQEGHILKMFPOSUTWYV][0-9]+fs", data),
        re.findall("[ACGT] to [ACGT] at [0-9]+", data),
        data.lower().startswith("rs"),
        data.startswith("c."),
        data.startswith("p."),
        data.startswith("g."),
        re.findall(
            "((Ala|Arg|Asn|Asp|Asx|Cys|Glu|Gln|Glx|Gly|His|Ile|Leu|Lys|Met|Phe|Pro|Ser|Thr|Trp|Tyr|Val)[0-9]+(Ala|Arg|Asn|Asp|Asx|Cys|Glu|Gln|Glx|Gly|His|Ile|Leu|Lys|Met|Phe|Pro|Ser|Thr|Trp|Tyr|Val|X))",
            data,
        ),
        re.findall("[ARNDCQEGHILKMFPOSUTWYV][0-9]+[ARNDCQEGHILKMFPOSUTWYVX]", data),
        re.findall("ss[0-9]+", data),
        re.findall("[0-9]*[+-]?[0-9]+[ ]?[ACGTacgt][ ]?[>/-][ ]?[ACGTacgt]", data),
        re.findall("[0-9]+del[0-9]+", data),
        re.findall("[0-9]+del[ACGT]+", data),
        re.findall("[0-9]+ins[0-9]+", data),
        re.findall("[0-9]+ins[ACGT]+", data),
        re.findall(
            r"(transition|transversion|substitution|deletion|mutation) (on|at|in) (codon |position )?[-+]?[0-9]+",
            data,
        ),
        re.findall(r"(on|in|at) (positions|position|codon|exon) [-+]?[0-9]+", data),
        re.findall(r"at (amino acid|codon|residue) (position )?[-+]?[0-9]+", data),
        re.findall(
            r"(Ala|Arg|Asn|Asp|Asx|Cys|Glu|Gln|Glx|Gly|His|Ile|Leu|Lys|Met|Phe|Pro|Ser|Thr|Trp|Tyr|Val)[0-9]+ (to|at|with) (Ala|Arg|Asn|Asp|Asx|Cys|Glu|Gln|Glx|Gly|His|Ile|Leu|Lys|Met|Phe|Pro|Ser|Thr|Trp|Tyr|Val)",
            data,
        ),
        re.findall(
            r"(Ala|Arg|Asn|Asp|Asx|Cys|Glu|Gln|Glx|Gly|His|Ile|Leu|Lys|Met|Phe|Pro|Ser|Thr|Trp|Tyr|Val)[0-9]+ (to|at|with) (alanine|arginine|asparagine|aspartic acid|cysteine|glutamic acid|glutamine|glycine|histidine|isoleucine|leucine|lysine|methionine|phenylalanine|proline|serine|threonine|tryptophan|tyrosine|valine)",
            data,
        ),
        re.findall(
            "((Ala|Arg|Asn|Asp|Asx|Cys|Glu|Gln|Glx|Gly|His|Ile|Leu|Lys|Met|Phe|Pro|Ser|Thr|Trp|Tyr|Val)[0-9]+(fs|FS|Fs))",
            data,
        ),
        re.findall("[ARNDCQEGHILKMFPOSUTWYV][0-9]+fs", data),
        re.findall("[ACGT] to [ACGT] at [0-9]+", data),
        re.findall("CA[0-9]+", data),
    ]
    for pattern in patterns:
        if pattern:
            return True
    return False


def open_article_data(path: str):
    with open(path) as fp:
        return json.load(fp)


def get_keys_from_article_data(article_data: dict):
    return set(article_data.keys())


def union_all_keys(article_path: list[str]):
    all_keys = set()
    for i, path in enumerate(article_path):
        article_data = open_article_data(path)
        all_keys = all_keys.union(get_keys_from_article_data(article_data))
        print(f"Processing {i+1}/{len(article_path)}: {path} {all_keys}", end="\r")
    return all_keys


def extract_unique_matches(
    patterns: list[Pattern], json_data: dict, previous_variants: list[str]
) -> list[str]:
    json_string = json.dumps(json_data)
    all_matches = set(previous_variants)
    for pattern in patterns:
        all_matches.update(re.findall(pattern, json_string))

    return list(all_matches)


def fix_missing_fields(searched_path, parsed_path, replace=True):

    from itertools import islice

    def insert_at_nth_position(d, key, value, n):
        new_dict = dict(
            list(islice(d.items(), n))
            + [(key, value)]
            + list(islice(d.items(), n, None))
        )
        return new_dict

    with open(searched_path, "r") as f:
        searched_data = json.load(f)
    with open(parsed_path, "r") as f:
        parsed_data = json.load(f)
    MISSING_FIELD = "supplementary_material"

    searched_data = insert_at_nth_position(
        searched_data, MISSING_FIELD, parsed_data[MISSING_FIELD], 2
    )
    if replace:
        with open(searched_path, "w") as f:
            json.dump(searched_data, f, indent=4)


def do_one_article(
    article_path: str,
    variants: list[str],
    supplementary_dir: str,
    data_to_persist: dict = {},
):
    pmc_id = article_path.split("/")[-1].split(".")[0]
    article_data = open_article_data(article_path)

    available_textual_search_keys = list(
        filter(lambda x: x in TEXTUAL_SEARCH_FIELDS, article_data.keys())
    )
    available_metadata_keys = filter(
        lambda x: x in METADATA_FIELDS, article_data.keys()
    )

    result = {}
    for key in available_metadata_keys:
        result[key] = article_data[key]
    result = {
        **result,
        **data_to_persist,
    }
    result["searches"] = {
        "textual": [],
        "tabular": {},
        "supplementary": [],
    }
    variants = extract_unique_matches(SUPPLEMENTARY_PATTERNS, article_data, variants)
    variants = list(filter(validate_variant, variants))
    variants = [x[0] if isinstance(x, tuple) else x for x in variants]
    variants = [x.lstrip() for x in variants]
    variants = list(set(variants))

    result["searches"]["textual"] = search_text(
        article_data, variants, available_textual_search_keys
    )

    result["searches"]["tabular"] = search_table(
        article_data.get("tables", []), variants
    )
    supplementary_material_path_dir = os.path.join(supplementary_dir, f"{pmc_id}")
    result["searches"]["supplementary"] = search_supplementary_material_from_path(
        supplementary_material_path_dir
    )

    # TODO: delete all empty values from result, do it for arbitrary depth
    # if not result["searches"]["supplementary_material"]:
    #     del result["searches"]["supplementary_material"]
    return result


def do_one_article_with_save(
    article_path: str,
    variants: list[str],
    save_dir: str,
    supplementary_dir: str,
    data_to_persist: dict = {},
):
    pmc_id = article_path.split("/")[-1].split(".")[0]

    result = do_one_article(article_path, variants, supplementary_dir, data_to_persist)
    # create a directory if it does not exist
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    # print(f"{save_dir}/{pmc_id}_searched.json")
    with open(f"{save_dir}/{pmc_id}_searched.json", "w") as fp:
        json.dump(result, fp, indent=4)
    return result


def do_one_article_parallel(article_path, variants, save_dir):
    pmc_id = article_path.split("/")[-1].split(".")[0]
    try:
        do_one_article(article_path, variants, save_dir)
    except Exception as e:
        print(f"Error while processing {pmc_id}: {e}")
        # log the error into a file
        with open(f"{save_dir}/error.txt", "a") as f:
            f.write(f"{pmc_id}: {e}\n")
        return False
    return True


def do_all_parallel(
    variants_path: str, articles_path: str, save_dir, number_of_workers=None
):
    import concurrent.futures

    # create full path

    article_paths = list(
        map(lambda x: f"{articles_path}/{x}", os.listdir(articles_path))
    )
    pmc_number = len(article_paths)
    with open(variants_path) as fp:
        raw_data = json.load(fp)
        variants = [raw_data[x.split("/")[-1].split(".")[0]] for x in article_paths]
    # return
    with concurrent.futures.ProcessPoolExecutor(
        max_workers=number_of_workers
    ) as executor:
        results = list(
            executor.map(
                do_one_article_parallel,
                article_paths,
                variants,
                [save_dir] * pmc_number,
            )
        )
    failed_number = results.count(False)
    return failed_number






def extract_prefix_and_suffix(raw_text: str, variant: str, fragment_size: int = 400):
    """
    Using regex to find locations of exact match of variant in raw_text
    """
    variant = re.escape(variant)
    indecies = [
        (m.start(), m.end()) for m in re.compile(f"{variant}").finditer(raw_text)
    ]
    result = []
    for start, end in indecies:
        prefix = raw_text[max(0, start - fragment_size) : start]
        suffix = raw_text[end : min(len(raw_text), end + fragment_size)]
        result.append({"prefix": prefix, "suffix": suffix})
    return result


def search_text(article_data, variants, available_textual_search_keys):
    result = []
    for variant in variants:
        variant_result = {
            key: extract_prefix_and_suffix(article_data[key], variant)
            for key in available_textual_search_keys
        }
        variant_result = {key: value for key, value in variant_result.items() if value}
        if variant_result:
            result.append(
                {
                    "exact_match": variant,
                    **variant_result,
                }
            )
    return result
def find_exact_match_in_rows(table_rows, exact_match):
    rows_to_return = []
    for row in table_rows:
        for key, value in row.items():
            if exact_match in str(value):
                rows_to_return.append(row)
    if rows_to_return:
        return filter_duplicates(rows_to_return)


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


def filter_duplicates(dictionaries):
    """
    Filter out duplicate dictionaries from a list of dictionaries.
    """
    unique_dictionaries = []
    seen = set()

    for d in dictionaries:
        t = tuple(sorted(d.items()))
        if t not in seen:
            seen.add(t)
            unique_dictionaries.append(d)

    return unique_dictionaries


def search_table(tables: list[dict], variants: list[str]):
    result = []
    for variant in variants:
        variant_result = {"exact_match": variant, "tables": []}
        for table in tables:
            # table_result = {"label": table.get("label", "")}
            table_result = {}
            # label, caption, table_wrap_foot, contents
            available_textual_search_keys = list(
                filter(lambda x: x in TABLE_TEXTUAL_SEARCH_FIELDS, table.keys())
            )
            for key in available_textual_search_keys:
                if prefix_and_suffix := extract_prefix_and_suffix(table[key], variant):
                    table_result[key] = prefix_and_suffix
            if in_rows := find_exact_match_in_rows(table["contents"], variant):
                table_result["found_in_rows"] = in_rows
            if in_columns := find_exact_match_in_columns(table["contents"], variant):
                table_result["found_in_columns"] = in_columns
            if table_result:
                table_result = {"label": table.get("label", ""), **table_result}
                variant_result["tables"].append(table_result)
        if variant_result["tables"]:
            result.append(variant_result)
    return result


def find_matches_collected(text: str, patterns=SUPPLEMENTARY_PATTERNS) -> set:
    """
    Find and collect matches in the given text using the specified patterns.
    Args:
        text (str): The text to search for matches.
        patterns (list): The list of patterns to use for matching.
    Returns:
        set: A set of collected matches found in the text.
    """
    res = set()
    for pattern in patterns:
        compiled_pattern = re.compile(pattern)
        res.update(
            map(
                lambda match: (
                    match.strip() if isinstance(match, str) else match[0].strip()
                ),
                (match for match in compiled_pattern.findall(text) if match),
            )
        )
    return res


def check_contents_paginated(data: dict) -> dict:
    """
    Check the contents of paginated data and return a dictionary of matches.
    Args:
        data (dict): The paginated data to check.
    Returns:
        dict: A dictionary of matches found in the paginated data.
    """
    if not isinstance(data, dict) or len(data) == 0:
        return {}
    res = {key: find_matches_collected(data[key]) for key in data}
    return res


def check_contents_table(data: list) -> dict:
    """
    Find matches in the given table data.
    Args:
        data (list): The table data to search for matches.
    Returns:
        dict: A dictionary containing the matches found in the column headers and rows of the table.
            The dictionary has two keys:
            - "found_in_column_header": A set of matches found in the column headers.
            - "found_in_rows": A set of matches found in the rows.
    """
    keys = "  ".join(list(data[0].keys()))
    res = {}
    res["found_in_column_header"] = find_matches_collected(keys)
    res["found_in_rows"] = set()
    for item in data:
        for key, value in item.items():
            res["found_in_rows"].update(find_matches_collected(str(value)))
    return res


def infer_supplementary_type_from_path(path: str) -> str:
    extension = path.split(".")[-2].split("_")[-1].lower()
    return infer_supplementary_type(extension)


def infer_supplementary_type(extension: str) -> str:
    """
    bed - bed
    csv - table
    doc, docx - doc
    pdf - pdf
    png, jpg, jpeg, tif, tiff - image
    ppt, pptx - powerpoint
    txt - text
    xls, xlsx - excel
    """
    if extension in ["bed"]:
        return "bed"
    if extension in ["csv"]:
        return "table"
    if extension in ["doc", "docx"]:
        return "doc"
    if extension in ["pdf"]:
        return "pdf"
    if extension in ["png", "jpg", "jpeg", "tif", "tiff"]:
        return "image"
    if extension in ["ppt", "pptx"]:
        return "powerpoint"
    if extension in ["txt"]:
        return "text"
    if extension in ["xls", "xlsx"]:
        return "excel"
    return "unknown"


class SupplementaryDataProcessor:
    def __init__(self, path=None, data=None):
        if path:
            self.path = path
            self.data_type = infer_supplementary_type_from_path(path)
            self.filename = "_".join(path.split("/")[-1].split(".")[0].split("_")[1:])
            self.result = None
            with open(path, "r") as fp:
                self.contents = json.load(fp)
        elif data:
            self.filename, self.contents = data
            self.path = None
            self.data_type = infer_supplementary_type(
                self.filename.split(".")[-1].split("_")[-1].lower()
            )
            self.result = None

    def process_text_image_bed(self):

        res = find_matches_collected(self.contents)
        if res:
            self.result = sorted(res)

    def process_pdf_powerpoint_excel_doc(self):
        res = check_contents_paginated(self.contents)
        for key in list(res.keys()):
            if res[key]:
                res[key] = sorted(res[key])
            else:
                res.pop(key)
        if res:
            self.result = res

    def process_table(self):
        res = check_contents_table(self.contents)
        for key in list(res.keys()):
            if res[key]:
                res[key] = sorted(res[key])
            else:
                res.pop(key)
        if res:
            self.result = res

    def process_data(self):
        processing_methods = {
            "text": self.process_text_image_bed,
            "image": self.process_text_image_bed,
            "bed": self.process_text_image_bed,
            "pdf": self.process_pdf_powerpoint_excel_doc,
            "powerpoint": self.process_pdf_powerpoint_excel_doc,
            "excel": self.process_pdf_powerpoint_excel_doc,
            "doc": self.process_pdf_powerpoint_excel_doc,
            "table": self.process_table,
        }
        if self.data_type in processing_methods:
            processing_methods[self.data_type]()
            if self.result:
                return {
                    "name": self.filename,
                    "type": self.data_type,
                    "contents": self.result,
                }
        return {}


def search_supplementary_material_from_path(supplementary_path_dir: str):
    """
    "supplementary_material": [
        {
            "name": "pone.0000001.s001_doc",
            "type": "doc",
            "contents" : [] | {} | ...
        }
    ],

    """
    result = []
    if not os.path.exists(supplementary_path_dir):
        return result
    supplementary_files = list(
        map(
            lambda x: f"{supplementary_path_dir}/{x}",
            os.listdir(supplementary_path_dir),
        )
    )

    for supplementary_file in supplementary_files:
        processed_data = SupplementaryDataProcessor(
            path=supplementary_file
        ).process_data()
        if processed_data:
            result.append(processed_data)

    return result


def search_supplementary_material(supplementary_dict_data: dict):
    """
    "supplementary_material": [
        {
            "name": "pone.0000001.s001_doc",
            "type": "doc",
            "contents" : [] | {} | ...
        }
    ],

    """
    result = []

    for item in supplementary_dict_data.items():
        processed_data = SupplementaryDataProcessor(data=item).process_data()
        if processed_data:
            result.append(processed_data)

    return result


def do_one_article_w_diseases(
    article_path: str, save_dir: str, supplementary_dir: str, article_tuple_data
):
    pmc_id, variants, data_to_persist = article_tuple_data
    pmc_group = "PMC" + pmc_id[3:-6].zfill(3) + "xxxxxx"
    my_article_path = os.path.join(article_path, pmc_group, f"{pmc_id}.json")
    my_supplementary_dir = os.path.join(supplementary_dir, pmc_group)
    my_save_dir = os.path.join(save_dir, pmc_group)
    if not os.path.exists(my_save_dir):
        os.makedirs(my_save_dir)
    # print(f"Processing {pmc_id}")
    logger.log(logging.INFO, f"{pmc_id} - STARTED")
    try:
        do_one_article(
            my_article_path,
            variants,
            my_save_dir,
            my_supplementary_dir,
            data_to_persist,
        )
        # fix_missing_fields(
        #     f"{my_save_dir}/{pmc_id}_searched.json", my_article_path, True
        # )
    except Exception as e:
        logger.error(f"{pmc_id} - {e}\n")
        # logger.error(f"{pmc_id} - {traceback.format_exc()}\n")
        return False
    logger.log(logging.INFO, f"{pmc_id} - ENDED")
    return True


def do_one_article_w_diseases_automation_paths(
    pmc_id: str,
    article_path: str,
    save_dir: str,
    supplementary_dir: str,
    pubtator_data_path: str,
):
    with open(pubtator_data_path, "r") as f:
        data = json.load(f)

    article_data = data[pmc_id]
    variants = list(map(lambda x: x[1], article_data["variant"]))
    data_to_persist = {
        "gene": article_data["gene"],
        "disease": article_data["disease"],
    }
    pmc_group = "PMC" + pmc_id[3:-6].zfill(3) + "xxxxxx"
    my_article_path = os.path.join(article_path, pmc_group, f"{pmc_id}.json")
    my_supplementary_dir = os.path.join(supplementary_dir, pmc_group)
    my_save_dir = os.path.join(save_dir, pmc_group)
    if not os.path.exists(my_save_dir):
        os.makedirs(my_save_dir)
    logger.log(logging.INFO, f"{pmc_id} - STARTED")
    try:
        do_one_article(
            my_article_path,
            variants,
            my_save_dir,
            my_supplementary_dir,
            data_to_persist,
        )
        # fix_missing_fields(
        #     f"{my_save_dir}/{pmc_id}_searched.json", my_article_path, True
        # )
    except Exception as e:
        logger.error(f"{pmc_id} - {e}\n")
        # logger.error(f"{pmc_id} - {traceback.format_exc()}\n")
        return False
    logger.log(logging.INFO, f"{pmc_id} - ENDED")
    return True


def run_do_one_article_w_diseases_automation():
    args = sys.argv

    pmc_id = args[2]
    pubtator_data_path = args[3]
    article_path = args[4]
    save_dir = args[5]
    supplementary_dir = args[6]

    do_one_article_w_diseases_automation_paths(
        pmc_id,
        article_path,
        save_dir,
        supplementary_dir,
        pubtator_data_path,
    )


def do_one_article_w_diseases_automation(
    pmc_id: str,
    article_data: dict,
    supplementary_data: dict,
    pubtator_data: dict,
    # save_dir: str,
):
    if not pubtator_data:
        logger.log(logging.INFO, f"{pmc_id} - NO PUBTATOR DATA")
        return {}
    variants = list(map(lambda x: x[1], pubtator_data["variant"]))
    data_to_persist = {
        "gene": pubtator_data["gene"],
        "disease": pubtator_data["disease"],
    }
    pmc_group = "PMC" + pmc_id[3:-6].zfill(3) + "xxxxxx"
    # my_article_path = os.path.join(article_path, pmc_group, f"{pmc_id}.json")
    # my_supplementary_dir = os.path.join(supplementary_dir, pmc_group)
    # my_save_dir = os.path.join(save_dir, pmc_group)
    # if not os.path.exists(my_save_dir):
    #     os.makedirs(my_save_dir)
    logger.log(logging.INFO, f"{pmc_id} - STARTED")
    result = {}

    try:
        available_textual_search_keys = list(
            filter(lambda x: x in TEXTUAL_SEARCH_FIELDS, article_data.keys())
        )
        available_metadata_keys = filter(
            lambda x: x in METADATA_FIELDS, article_data.keys()
        )

        for key in available_metadata_keys:
            result[key] = article_data[key]
        result = {
            **result,
            **data_to_persist,
        }
        result["searches"] = {
            "textual": [],
            "tabular": {},
            "supplementary": [],
        }
        variants = extract_unique_matches(
            SUPPLEMENTARY_PATTERNS, article_data, variants
        )
        variants = list(filter(validate_variant, variants))
        variants = [x[0] if isinstance(x, tuple) else x for x in variants]
        variants = [x.lstrip() for x in variants]
        variants = list(set(variants))
        result["searches"]["textual"] = search_text(
            article_data, variants, available_textual_search_keys
        )

        result["searches"]["tabular"] = search_table(
            article_data.get("tables", []), variants
        )

        result["searches"]["supplementary"] = search_supplementary_material(
            supplementary_data
        )
        # TODO: delete all empty values from result, do it for arbitrary depth
        # if not result["searches"]["supplementary_material"]:
        #     del result["searches"]["supplementary_material"]
        # fix_missing_fields(
        #     f"{my_save_dir}/{pmc_id}_searched.json", my_article_path, True
        # )
    except Exception as e:
        logger.error(f"{pmc_id} - {e}\n")
        # logger.error(f"{pmc_id} - {traceback.format_exc()}\n")
        return False
    logger.log(logging.INFO, f"{pmc_id} - ENDED")
    return result


def raw_search_one_article(
    pmc_id: str,
    article_data: dict,
    supplementary_data: dict,
    pubtator_data: dict,
):

    variants = list(map(lambda x: x[1], pubtator_data["variant"]))
    result = {}
    try:
        available_textual_search_keys = list(
            filter(lambda x: x in TEXTUAL_SEARCH_FIELDS, article_data.keys())
        )
        available_metadata_keys = filter(
            lambda x: x in METADATA_FIELDS, article_data.keys()
        )

        for key in available_metadata_keys:
            result[key] = article_data[key]
        result = {
            **result,
        }
        result["searches"] = {
            "textual": [],
            "tabular": {},
            "supplementary": [],
        }
        variants = [x[0] if isinstance(x, tuple) else x for x in variants]
        variants = [x.lstrip() for x in variants]
        variants = list(set(variants))

        result["searches"]["textual"] = search_text(
            article_data, variants, available_textual_search_keys
        )

        result["searches"]["tabular"] = search_table(
            article_data.get("tables", []), variants
        )

        result["searches"]["supplementary"] = search_supplementary_material(
            supplementary_data
        )
        if not result["searches"]["textual"] or not result["searches"]["tabular"]:
            return False
    except Exception as e:
        return False
    return result


if __name__ == "__main__":
    import sys

    args = sys.argv
    function_to_call = args[1]
    if function_to_call == "do_one_article_w_diseases_automation":
        run_do_one_article_w_diseases_automation()

    # pmc_id = "PMC_TEST"
    # logger.log(logging.INFO, f"{pmc_id} - STARTED")
    # logger.info(f"{pmc_id} - STARTED")

    # ARTICLE_ROOT_DIR = "/mnt/d/Storage/WORK/P/Clingen/PubMedCentral/50k_articles/articles_ready_for_elastic/PMC002xxxxxx/"
    # # ARTICLE_PATHS = list(
    # #     map(lambda x: f"{ARTICLE_ROOT_DIR}/{x}", os.listdir(ARTICLE_ROOT_DIR))
    # # )
    # # all_keys = union_all_keys(ARTICLE_PATHS)
    # # print(all_keys)
    # article_path = f"{ARTICLE_ROOT_DIR}/PMC2873115.json"
    # # text = "Mara voli Mara Milovana"
    # # variant = "Cathepsin B"
    # # print(extract_prefix_and_suffix(text, variant))
    # variants = [
    #     " treat several important",
    #     "Cathepsin B",
    #     "SMILES",
    #     "C18H14N2O6",
    #     "compound structure and ",
    #     "aThe informatio",
    # ]
    # # variants = [
    # #     "Cathepsin B",
    # # ]
    # do_one_article(article_path, variants, save_dir)
