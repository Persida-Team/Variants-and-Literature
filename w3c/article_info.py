import os
import re
from datetime import datetime, timezone

from dotenv import load_dotenv
from w3c.utilities import (
    CONTEXT_URL,
    PATTERNS_COMPLEX,
    PATTERNS_RS,
    create_document_id,
    load_json,
)

load_dotenv()

BODY_DIRECTORY = os.getenv("BODY_DIRECTORY", "")
if not BODY_DIRECTORY:
    raise Exception("No bodies directory specified in .env")


def reformat_article_info_data(data: dict) -> dict:
    """
    Reformat the given data dictionary.
    Args:
        data (dict): The dictionary to be reformatted.
    Returns:
        dict: The reformatted dictionary.
    """
    reformatted = {}
    if "ids" in data:
        reformatted["articleIDs"] = {
            key.upper(): data["ids"].get(key) for key in ["pmc", "pmid", "doi"]
        }
    if "type" in data:
        reformatted["publicationType"] = data["type"]
    if "supplementary_material" in data:
        reformatted["supplementaryMaterial"] = {
            "type": "List",
            "items": [
                {"format": supp.split(".")[-1].upper(), "link": supp}
                for supp in data["supplementary_material"]
            ],
        }
    data_to_add = []
    if "disease" in data:
        disease_list = data["disease"]
        data_to_add.extend(
            "DiseaseEntity:" + entity for disease in disease_list for entity in disease
        )
    if "gene" in data:
        gene_list = data["gene"]
        for ncbi, hgnc in gene_list:
            data_to_add.append(f"GeneEntity:NCBI:{ncbi}")
            data_to_add.append(f"GeneEntity:HGNC:{hgnc}")
        # data_to_add.extend(
        #     [f"GeneEntity:NCBI:{gene[0]}", f"GeneEntity:HGNC:{gene[1]}"]
        #     for gene in gene_list
        # )
    if len(data_to_add) > 0:
        reformatted["tags"] = data_to_add
    return reformatted


def create_exact_based_on_pattern(exact_in_text: str) -> str:
    """
    Create an exact match based on the input pattern corresponding to rsid and complex variants.
    Args:
        exact_in_text (str): The input match to create an exact match from.
    Returns:
        str: The exact match based on the pattern.
    """
    if any(pattern.fullmatch(exact_in_text) for pattern in PATTERNS_RS):
        return re.sub(r"[ #,]", "", exact_in_text.lower())
    if any(pattern.fullmatch(exact_in_text) for pattern in PATTERNS_COMPLEX):
        exact_in_text = re.sub(r"[ #,]", "", exact_in_text)
        rsid = re.match("rs[0-9]*", exact_in_text).group(0)
        alt = exact_in_text[-1]
        return rsid + alt
    return exact_in_text


def create_starting_part_w3c(
    pmcid: str, exact_in_text: str, article_info: dict
) -> dict:
    """
    Create the starting part of a W3C document for a given PMCID, exact match, and article information.
    Args:
        pmcid (str): The PMCID of the publication.
        exact_in_text (str): The input match to create an exact match from
        article_info (dict): A dictionary containing information about the article
    Returns:
        dict: A dictionary representing the starting part of the W3C document
    """
    body = []
    exact = create_exact_based_on_pattern(exact_in_text)
    if os.path.exists(BODY_DIRECTORY + "/" + exact + ".json"):
        body = load_json(
            BODY_DIRECTORY + "/" + exact + ".json"
        )  # preraditi body u bazu i izmeniti pakovanje bodyja u fajl
    temp = {
        "@context": CONTEXT_URL,
        "id": create_document_id(pmcid, exact),
        "created": datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z"),
        "label": f"Annotation for {exact} in publication {pmcid}",
        "publicationId": pmcid,
        "variantMatch": exact,
        "articleData": article_info,
    }
    if len(body) > 0:
        temp["body"] = {"type": "List", "items": body}
    temp["target"] = {"type": "List", "items": []}
    return temp
