import re

from w3c.article_info import create_starting_part_w3c

PATTERNS = [
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


def find_matches_collected(text: str, patterns=PATTERNS) -> set:
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


def create_target_text(exact: str, data: dict):
    """
    Create a target text based on the exact string and data provided.
    Args:
        exact (str): The exact string to be included in the target text.
        data (dict): The data containing variant search results for textual data.
    Returns:
        list: A list of dictionaries containing the target information for W3C annotation
    """
    res = []
    for key in data.keys():
        if key in ["text", "abstract", "title"]:
            for i in range(len(data[key])):
                if (
                    "    " not in data[key][i]["prefix"]
                    and "    " not in data[key][i]["suffix"]
                ):
                    temp = {}
                    temp["type"] = "TextQuoteSelector"
                    temp["exact"] = exact
                    temp["prefix"] = data[key][i]["prefix"]
                    temp["suffix"] = data[key][i]["suffix"]
                    temp["sourceDescription"] = key
                    additional = find_matches_collected(
                        data[key][i]["prefix"]
                    ) | find_matches_collected(data[key][i]["suffix"])
                    if len(additional) > 0:
                        temp["additionalInfo"] = list(additional)
                    res += [temp]
    return res


def create_target_table(exact: str, data: list):
    """
    Create a target table based on the exact string and data provided.
    Args:
        exact (str): The exact string to be included in the target table.
        data (dict): The data containing variant search results for tabular data.
    Returns:
        list: A list of dictionaries containing the target information for W3C annotation
    """
    res = []
    for table in data:
        source = table["label"]
        for key in table.keys():
            if key == "label":
                continue
            temp = {}
            temp["type"] = "TableTextSelector"
            temp["tableID"] = source
            temp["exact"] = exact
            if key == "found_in_rows":
                temp["sourceDescription"] = "foundInRows"
                temp["foundInRows"] = table[key]
            elif key == "found_in_columns":
                temp["sourceDescription"] = "foundInColumnHeader"
                temp["foundInColumnHeader"] = table[key]
            elif key == "caption":
                temp["sourceDescription"] = key
                for i in range(len(table[key])):
                    temp["prefix"] = table[key][i]["prefix"]
                    temp["suffix"] = table[key][i]["suffix"]
                    additional = find_matches_collected(
                        table[key][i]["prefix"]
                    ) | find_matches_collected(table[key][i]["suffix"])
                    if len(additional) > 0:
                        temp["additionalInfo"] = list(additional)
                    res += [temp]
                continue
            elif key == "table_wrap_foot":
                temp["sourceDescription"] = "tableWrapFoot"
                for i in range(len(table[key])):
                    temp["prefix"] = table[key][i]["prefix"]
                    temp["suffix"] = table[key][i]["suffix"]
                    additional = find_matches_collected(
                        table[key][i]["prefix"]
                    ) | find_matches_collected(table[key][i]["suffix"])
                    if len(additional) > 0:
                        temp["additionalInfo"] = list(additional)
                    res += [temp]
                continue
            res += [temp]
    return res


def add_table_data(exact: str, sec_variant: dict, result: list):
    exact_match = sec_variant["exact_match"]
    for res in result:
        if res["variantMatch"] == exact:
            target = res["target"]["items"][0]["selector"]
            target += create_target_table(exact_match, sec_variant["tables"])
            res["target"]["items"][0]["selector"] = target
    return result


def add_target_for_supplementary(
    exact: str,
    exact_in_text: str,
    result: dict,
    supp_type: str,
    file_url: str,
    key: str,
):
    """
    Add a target for supplementary data in the result dictionary.
    Args:
        exact (str): The exact match to be added.
        exact_in_text (str): The exact match found in the text.
        result (dict): The dictionary containing the W3C annotations.
        supp_type (str): The type of supplementary data (e.g., pdf, excel, table).
        file_url (str): The URL of the file containing the data.
        key (str): The key identifier for the specific type of supplementary data (pageID, sheetID, positionID).
    Returns:
        dict: The updated result W3C annotations with updated target for the supplementary data.
    """
    flag = False
    temp = {}
    temp["type"] = "TextQuoteSelector"
    temp["exact"] = exact_in_text
    temp["sourceDescription"] = supp_type
    if key != None:
        if supp_type in ["pdf", "powerpoint", "doc"]:
            temp["pageID"] = key
        elif supp_type in ["excel"]:
            temp["sheetID"] = key
        elif supp_type in ["table"]:
            if key == "found_in_rows":
                temp["positionID"] = "foundInRows"
            elif key == "found_in_columns":
                temp["positionID"] = "foundInColumnHeader"
            else:
                temp["positionID"] = key
    for res in result:
        if res["variantMatch"] == exact:
            targets = res["target"]["items"]
            for target in targets:
                if target["source"] == file_url:
                    flag = True
                    target["selector"] += [temp]
            res["target"]["items"] = targets
            if not flag:
                temp2 = {}
                temp2["source"] = file_url
                temp2["selector"] = [temp]
                res["target"]["items"] += [temp2]
    return result


def add_document_for_supplementary(
    pmcid: str,
    exact_in_text: str,
    result: dict,
    supp_type: str,
    file_url: str,
    article_info: dict,
    key: str,
) -> dict:
    """
    Add a document for supplementary data in the result W3C annotation.
    Args:
        pmcid (str): The PMCID of the document.
        exact_in_text (str): The exact match found in the text.
        result (dict): The dictionary containing the W3C annotations.
        supp_type (str): The type of supplementary data (e.g., pdf, excel, table).
        file_url (str): The URL of the file containing the data.
        article_info (dict): Information about the article.
        key (str): The key identifier for the specific type of supplementary data (pageID, sheetID, positionID).
    Returns:
        dict: The updated result W3C annotations with the added document for the supplementary data.
    """

    temp = create_starting_part_w3c(pmcid, exact_in_text, article_info)
    temp2 = {}
    temp2["source"] = file_url
    temp2["selector"] = []
    temp3 = {}
    temp3["type"] = "TextQuoteSelector"
    temp3["exact"] = exact_in_text
    temp3["sourceDescription"] = supp_type
    if key != None:
        if supp_type in ["pdf", "powerpoint", "doc"]:
            temp3["pageID"] = key
        elif supp_type in ["excel"]:
            temp3["sheetID"] = key
        elif supp_type in ["table"]:
            if key == "found_in_rows":
                temp3["positionID"] = "foundInRows"
            elif key == "found_in_columns":
                temp3["positionID"] = "foundInColumnHeader"
            else:
                temp3["positionID"] = key
    temp2["selector"] += [temp3]
    temp["target"]["items"] = [temp2]
    result += [temp]
    return result
