from utils.filesystem_utils import open_json
from typing import Union
from collections import defaultdict
from functools import reduce


def return_on_failure(value):
    def decorate(f):
        def applicator(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except:
                return value

        return applicator

    return decorate


# Define the custom object class
class ArticleObject:
    def __init__(self, **kwargs):
        # Set the attributes of the object based on the keyword arguments
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self, indent=""):
        # Create a string representation of the object by concatenating the attributes and their values
        s = ""
        for key, value in self.__dict__.items():
            if isinstance(value, ArticleObject):
                # If the value is a custom object, recursively print it
                s += f"{indent}{key}:\n"
                s += value.__str__(indent + "  ")
            elif isinstance(value, list):
                # If the value is a list, print each item in the list
                s += f"{indent}{key}:\n"
                for item in value:
                    if isinstance(item, ArticleObject):
                        # If the item is a custom object, recursively print it
                        s += item.__str__(indent + "  ")
                    else:
                        # Otherwise, just print the item
                        s += f"{indent}  {item}\n"
            else:
                # Otherwise, just print the attribute and its value
                s += f"{indent}{key}: {value}\n"

        return s


# Define a recursive function to convert JSON objects and lists into custom objects
def decode_json(obj):
    if isinstance(obj, dict):
        # If the object is a dictionary, create a custom object and recursively decode the values
        return ArticleObject(**{key: decode_json(value) for key, value in obj.items()})
    elif isinstance(obj, list):
        # If the object is a list, recursively decode the values
        return [decode_json(item) for item in obj]
    else:
        # If the object is neither a dictionary nor a list, return it as-is
        return obj


def map_article_objects(
    data: Union[dict, list[dict]]
) -> Union[ArticleObject, list[ArticleObject]]:
    """
    Map a dictionary or list of dictionaries to a custom ArticleObject or list of custom ArticleObjects.

    :param data: The dictionary or list of dictionaries to map.
    :return: A custom ArticleObject or list of custom ArticleObjects.
    """
    if isinstance(data, dict):
        return decode_json(data)
    elif isinstance(data, list):
        return [map_article_objects(item) for item in data]
    raise TypeError(f"Unexpected type: {type(data)}")


def load_article_metadata_from_json(json_file: str) -> list[ArticleObject]:
    """
    Load article metadata from a JSON file.

    :param json_file: The path to the JSON file.
    :return: A list of custom ArticleObjects.
    """
    to_return = map_article_objects(open_json(json_file))
    if isinstance(to_return, ArticleObject):
        return [to_return]
    return to_return


def parse_json_article_metadata(article: ArticleObject) -> dict:

    rs_d = defaultdict(lambda: {"caids": [], "match": None})
    for rsid_object in article.rsIDInArticle:
        l = {}
        for caid_object in rsid_object.caIDs:
            if isinstance(caid_object, str):  # No_data
                break
            l[caid_object.caID] = caid_object.communityStandardTitle
        rs_d[rsid_object.rsID]["caids"] = l

    other_var_d = {}
    for variant_object in article.variantsInArticle:
        form = variant_object.variantForm
        match = variant_object.variantTextMatch
        if form == match:
            rs_d[form]["match"] = match
        else:
            other_var_d[form] = match

    genes_d = {}
    for gene_object in article.genesInArticle:
        genes_d[gene_object.geneSymbol] = gene_object.ncbiGeneId

    return {
        "pmid": article.articleIdList.pubmedId,
        "pmcid": article.articleIdList.pmcId,
        "caid_in_allele_registry": article.caIDInAlleleRegistry,
        "rs_match": rs_d,
        "rs_other": other_var_d,
        "genes": genes_d,
    }


def label_by_pmid(article_metadata: dict) -> dict:
    """
    Label the article metadata by PMID.

    :param article_metadata: The article metadata to label.
    :return: The labeled article metadata.
    """
    return {article_metadata["pmid"]: article_metadata}


def label_by_pmcid(article_metadata: dict) -> dict:
    """
    Label the article metadata by PMCID.

    :param article_metadata: The article metadata to label.
    :return: The labeled article metadata.
    """
    return {article_metadata["pmcid"]: article_metadata}


def parse_all_article_metadata_labeled(
    articles: list[ArticleObject], label_function
) -> dict:
    """
    Parse all article metadata.

    :param articles: The list of articles to parse.
    :param label_function: The function to use to label the article metadata.
    :return: The parsed article metadata.
    """
    return reduce(
        lambda x, y: {**x, **y},
        map(label_function, map(parse_json_article_metadata, articles)),
    )

# def parse_all_article_metadata(articles: list[ArticleObject]) -> list[dict]:
#     """
#     Parse all article metadata.

#     :param articles: The list of articles to parse.
#     :return: The parsed article metadata.
#     """
#     return list(
#         map(parse_json_article_metadata, articles)
#     )  # TODO : see if this needs to be a list or a generator
