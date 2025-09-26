from w3c.article_info import create_exact_based_on_pattern
from w3c.target import add_document_for_supplementary, add_target_for_supplementary


def count_variants_in_file(data: list) -> set:
    """
    Calculate the total number of unique variants present in the given data.
    Parameters:
    - data (list): ["searches"]["supplementary"] part of variant search result for one PMCID
    Returns:
    - all_variants (set): A set containing all the unique variants found in the data.
    """
    all_variants = set()
    for one in data:
        supp_type = one["type"]
        content = one["contents"]
        if supp_type in ["text", "image", "bed"]:
            all_variants.update(content)
        elif supp_type in ["pdf", "powerpoint", "excel", "doc", "table"]:
            for key in content:
                all_variants.update(content[key])
    return all_variants


def update_supplementary_info(result: list, file_url: str) -> list:
    """
    Update the information for supplementary material in the given result based on the file URL.
    Parameters:
    - result (list): Prepared W3C annotations for one PMCID
    - file_url (str): The URL of the supplementary material file to be updated
    Returns:
    - result (list): Updated W3C annotations file
    """
    for document in result:
        if (
            "articleData" in document
            and "supplementaryMaterial" in document["articleData"]
        ):
            items = document["articleData"]["supplementaryMaterial"].get("items", [])
            for item in items:
                if "link" in item and item["link"] == file_url:
                    item["info"] = "Supplementary material has more than 100 variants."
            document["articleData"]["supplementaryMaterial"]["items"] = items
    return result


def add_supplementary_data(
    pmcid: str, result: dict, article_info: dict, supplementaries: list
):
    local_variants = []
    for res in result:
        local_variants.append(res["variantMatch"])
    all_variants = count_variants_in_file(supplementaries)
    print("ADDING SUPPLEMENTARY DATA\n\n\n\n\n")
    print(all_variants)
    for supplementary in supplementaries:
        name = supplementary["name"]
        temp = name.split("_")
        ext = temp[-1]
        filename = "_".join(temp[:-1])
        file_url = (
            "https://www.ncbi.nlm.nih.gov/pmc/articles/"
            + pmcid
            + "/bin/"
            + filename
            + "."
            + ext
        )
        all_variants = count_variants_in_file([supplementary])
        if len(all_variants) > 100:
            result = update_supplementary_info(result, file_url)
            continue
        supp_type = supplementary["type"]
        content = supplementary["contents"]
        if supp_type in ["text", "image", "bed"]:
            for exact_match in content:
                exact = create_exact_based_on_pattern(exact_match)
                if exact in local_variants:
                    result = add_target_for_supplementary(
                        exact, exact_match, result, supp_type, file_url, key=None
                    )
                else:
                    local_variants.append(exact)
                    result = add_document_for_supplementary(
                        pmcid,
                        exact_match,
                        result,
                        supp_type,
                        file_url,
                        article_info,
                        key=None,
                    )
        elif supp_type in ["pdf", "powerpoint", "excel", "doc", "table"]:
            for key in content:
                for exact_match in content[key]:
                    exact = create_exact_based_on_pattern(exact_match)
                    if exact in local_variants:
                        result = add_target_for_supplementary(
                            exact, exact_match, result, supp_type, file_url, key
                        )
                    else:
                        local_variants.append(exact)
                        result = add_document_for_supplementary(
                            pmcid,
                            exact_match,
                            result,
                            supp_type,
                            file_url,
                            article_info,
                            key,
                        )
    return result
