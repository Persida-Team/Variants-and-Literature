import os
import re
from w3c.logger_config import setup_logger
from w3c.utilities import (
    save_json,
    load_existing_bodies,
    append_to_existing_bodies,
    create_directory,
    get_results_caid,
    get_results_rsid,
    get_results_vcf_file,
    register_new_indel,
    get_results_txt_file,
    get_results_allReg_hgvs,
    REFSEQ,
    PATTERNS_RS,
    PATTERNS_CA,
    PATTERNS_COMPLEX,
    LOGGER,
    BODY_DIRECTORY,
    EXISTING_BODIES_PATH,
)

LOGGER = setup_logger("body.log")

# REFSEQ = ["NC_000001.11", "NC_000002.12", "NC_000003.12", "NC_000004.12", "NC_000005.10", 
#           "NC_000006.12", "NC_000007.14", "NC_000008.11", "NC_000009.12", "NC_000010.11", 
#           "NC_000011.10", "NC_000012.12", "NC_000013.11", "NC_000014.9", "NC_000015.10", 
#           "NC_000016.10", "NC_000017.11", "NC_000018.10", "NC_000019.10", "NC_000020.11", 
#           "NC_000021.9", "NC_000022.11", "NC_000023.11", "NC_000024.10", "NC_012920.1"]

def remove_temp_files(pmc_id: str) -> None: 
    """
    Remove the VCF file.
    Args:
        pmc_id (str): The PMC ID of the article.
    Returns:
        None
    """
    for file_suffix in ["_variants.vcf", "_rsids.txt", "_variants_result.vcf"]:
        file_path = f"{pmc_id}{file_suffix}"
        if os.path.exists(file_path):
            os.remove(file_path)


def create_vcf_header(ch: str, pmc_id: str) -> None:
    """
    Create the VCF header for the given chromosome.
    Args:
        ch (str): The chromosome identifier.
        pmc_id (str): The PMCID used for naming the VCF file.
    Returns:
        None
    """
    with open(f"{pmc_id}_variants.vcf", "w") as vcf:
        vcf.write("##fileformat=VCFv4.1\n")
        vcf.write(f"##contig=<ID={ch},assembly=GRCh38>\n")
        vcf.write(f"#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n")


def add_row_in_vcf(chrom: str, pos: str, ref: str, alt: str, pmc_id: str) -> None:
    """
    Add a row to a VCF file with the given chromosome, position, reference, and alternate alleles.
    Args:
        chrom (str): The chromosome of the variant.
        pos (str): The position of the variant.
        ref (str): The reference allele.
        alt (str): The alternate allele.
    Returns:
        None
    """
    try:
        with open(f"{pmc_id}_variants.vcf", "a") as vcf:
            vcf.write(
                f"{chrom}\t{pos}\t.\t{ref}\t{alt}\t.\t.\t.\n"
            )
    except Exception as e:
        LOGGER.error(f"Error occurred while adding row in VCF: {e}")





def read_data_from_vcf_file(pmc_id: str) -> list:
    """
    Reads data from a VCF file and returns a list of dictionaries containing the CAID and ALT values.
    Returns:
        list: A list of dictionaries, where each dictionary represents a variant and contains the following keys:
            - 'caid' (str): The CAID value of the variant.
            - 'alt' (str): The ALT value of the variant.
    """
    res = []
    with open(f"{pmc_id}_variants_result.vcf") as f:
        for line in f:
            temp = {}
            line = line.strip()
            if line.startswith("#"):
                continue
            line1 = line.split("\t")
            if line1[2] != ".":
                temp["caid"] = line1[2]
                temp["alt"] = line1[4]
            res.append(temp)
    return res


def match_exact_matches_to_patterns(
    content: list, need_body_rs: set, need_body_ca: set, need_body_complex: set
) -> tuple[set, set, set]:
    """
    Match exact matches to predefined patterns in the given content and update the sets of rs, ca, and complex types accordingly.
    Args:
        content (list): A list of exact matches
        need_body_rs (set): A set of rs type matches
        need_body_ca (set): A set of ca type matches
        need_body_complex (set): A set of complex type matches
    Returns:
        tuple: A tuple containing the updated sets of rs, ca, and complex types after matching the exact matches to patterns.
    """
    for exact_in_text in content:
        for pattern in PATTERNS_RS:
            if pattern.fullmatch(exact_in_text):
                exact_in_text = re.sub(r"[ #,]", "", exact_in_text.lower())
                need_body_rs.add(exact_in_text)
        for pattern in PATTERNS_CA:
            if pattern.fullmatch(exact_in_text):
                need_body_ca.add(exact_in_text)
        for pattern in PATTERNS_COMPLEX:
            if pattern.fullmatch(exact_in_text):
                exact_in_text = re.sub(r"[ #,]", "", exact_in_text)
                rsid = re.match("rs[0-9]*", exact_in_text).group(0)
                alt = exact_in_text[-1]
                exact_in_text = rsid + alt
                need_body_complex.add(exact_in_text)
    return need_body_rs, need_body_ca, need_body_complex


def calculate_length(content) -> int:
    """
    Calculate the total length of content based on the supplementary type.
    Args:
        content: The content to calculate the length of.
    Returns:
        int: The total length of the content.
    """
    length = 0
    if isinstance(content, dict):
        for key in content:
            length += len(content[key])
    elif isinstance(content, list):
        length = len(content)
    return length


def collect_body_variants_from_supplementary(data: list) -> tuple[list, list, list]:
    """
    Collect body variants from the supplementary data based on the type and contents provided.
    Args:
        data (list): A list of dictionaries containing supplementary data.
    Returns:
        tuple: A tuple containing lists of rs, ca, and complex body variants extracted from the supplementary data.
    """
    THRESHOLD = 100
    need_body_rs = set()
    need_body_ca = set()
    need_body_complex = set()
    for one in data:
        if "type" not in one or "contents" not in one:
            continue
        supp_type = one["type"]
        content = one["contents"]
        if calculate_length(content) > THRESHOLD:
            continue
        if supp_type in ["text", "image", "bed"]:
            need_body_rs, need_body_ca, need_body_complex = (
                match_exact_matches_to_patterns(
                    content, need_body_rs, need_body_ca, need_body_complex
                )
            )
        elif supp_type in ["pdf", "powerpoint", "excel", "doc", "table"]:
            for key in content:
                need_body_rs, need_body_ca, need_body_complex = (
                    match_exact_matches_to_patterns(
                        content[key], need_body_rs, need_body_ca, need_body_complex
                    )
                )
    return list(need_body_rs), list(need_body_ca), list(need_body_complex)


def find_exact_matches_of_rsid_caid_complex_type(data: dict):
    """
    Find exact matches of rsid type in the given data.
    Args:
        data (dict): The input data.
    Returns:
        lists: The list of exact matches of rsid type, CAid type and complex type.
    """
    textuals = data["searches"]["textual"]
    tabulars = data["searches"]["tabular"]
    matches = {first_find["exact_match"] for first_find in textuals} | {
        second_find["exact_match"] for second_find in tabulars
    }
    need_body_rs = set()
    need_body_ca = set()
    need_body_complex = set()
    need_body_rs, need_body_ca, need_body_complex = match_exact_matches_to_patterns(
        matches, need_body_rs, need_body_ca, need_body_complex
    )
    additional_rs, additional_ca, additional_complex = (
        collect_body_variants_from_supplementary(data["searches"]["supplementary"])
    )
    need_body_rs.update(additional_rs)
    need_body_ca.update(additional_ca)
    need_body_complex.update(additional_complex)
    return list(need_body_rs), list(need_body_ca), list(need_body_complex)


def prepare_text_for_query(rsids: list, pmc_id: str) -> None:
    """
    Prepare the text for query and write it to a file.
    Args:
        rsids: A list of rsids.
    """
    text = "\n".join(rsids)
    with open(f"{pmc_id}_rsids.txt", "w") as f:
        f.write(text)


def reformat_data_for_body(data: dict) -> dict:
    """
    Reformat the one response from Allele Registry corresponding to one CAID.
    Args:
        data (dict): The input data dictionary - response from Allele Registry.
    Returns:
        dict: The reformatted data dictionary.
    """
    if not data:
        return {}
    temp = {}
    caid = data["@id"].split("/")[-1]
    temp["caid"] = caid
    if "genomicAlleles" in data:
        genomicAlleles = data["genomicAlleles"]
        for i in range(len(genomicAlleles)):
            if "referenceGenome" in genomicAlleles[i]:
                if genomicAlleles[i]["referenceGenome"] == "GRCh38":
                    if "chromosome" in genomicAlleles[i]:
                        temp["chrom"] = genomicAlleles[i]["chromosome"]
                    if "coordinates" in genomicAlleles[i]:
                        temp["pos"] = genomicAlleles[i]["coordinates"][0]["end"]
                        temp["ref"] = genomicAlleles[i]["coordinates"][0][
                            "referenceAllele"
                        ]
                        temp["alt"] = genomicAlleles[i]["coordinates"][0]["allele"]
                    if "hgvs" in genomicAlleles[i]:
                        for hgvs in genomicAlleles[i]["hgvs"]:
                            if hgvs.split(":")[0] in REFSEQ:
                                temp["hgvs"] = hgvs
                                break
    if "externalRecords" in data:
        if "dbSNP" in data["externalRecords"]:
            dbsnp = "rs" + str(data["externalRecords"]["dbSNP"][0]["rs"])
            temp["dbsnp"] = dbsnp
            temp["reportedSNP"] = True
        else:
            temp["reportedSNP"] = False
        if "ClinVarAlleles" in data["externalRecords"]:
            temp["reportedClinVar"] = True
        else:
            temp["reportedClinVar"] = False
    else:
        temp["reportedSNP"] = False
        temp["reportedClinVar"] = False
    if "transcriptAlleles" in data:
        transcript = data["transcriptAlleles"]
        temp_gene = set()
        temp_id = set()
        for j in range(len(transcript)):
            if "geneNCBI_id" in transcript[j]:
                temp_id.add(transcript[j]["geneNCBI_id"])
            if "geneSymbol" in transcript[j]:
                temp_gene.add(transcript[j]["geneSymbol"])
        temp["genes_ncbi"] = list(temp_id)
        temp["genes_symbol"] = list(temp_gene)
    return temp

def collect_rsid_from_dbsnp(rsid:str):
    dbsnp_rsid = get_results_rsid(rsid[2:])
    # time.sleep(1)
    res = []
    if "primary_snapshot_data" not in dbsnp_rsid:
        return res
    if "placements_with_allele" not in dbsnp_rsid["primary_snapshot_data"]:
        return res
    data = dbsnp_rsid["primary_snapshot_data"]["placements_with_allele"]
    for one in data:
        if one["seq_id"] not in REFSEQ:
            continue
        if "alleles" not in one:
            continue
        alleles = one["alleles"]
        for allele in alleles:
            if "hgvs" not in allele:
                continue
            res.append(allele["hgvs"])
    return res


def collect_hgvs_from_allreg(hgvs: str) -> dict:
    res = []
    data = get_results_allReg_hgvs(hgvs)
    if "errorType" in data:
        with open("skipped_hgvs.txt", "a") as f:
            f.writelines(hgvs + "\n")
        return res
    caid = data["@id"]
    if caid.startswith("_"):
        data = register_new_indel(hgvs)
    return reformat_data_for_body(data)



def check_new_indels(data: list) -> list:
    """
    Collect missing CAIDs from the given data that are indels.
    Args:
        data (list): A list of dictionaries representing variant data.
    Returns:
        list: A list of dictionaries representing the missing CAIDs.
    """
    hgvs = []
    caids = []
    res = []
    for one in data:
        if "dbsnp" in one:
            dbsnp = one["dbsnp"]
            break
    for one in data:
        if "hgvs" in one:
            hgvs.append(one["hgvs"])
        if "caid" in one:
            caids.append(one["caid"])
    hgvs_dbsnp = collect_rsid_from_dbsnp(dbsnp)
    diffs = [item for item in hgvs_dbsnp if item not in hgvs]
    for item in diffs:
        if item.endswith("="):
            continue
        if "N" in item[1:]:
            continue
        if item.count("[") > 1 or item.count("]") > 1:
            with open("skipped_hgvs.txt", "a") as f:
                f.writelines(item + "\n")
            continue
        temp = collect_hgvs_from_allreg(item)
        if "caid" in temp:
            if temp["caid"] not in caids:
                res.append(temp)
    return res

    

def collect_missing_caids(data: list, pmc_id: str) -> list:
    """
    Collect missing CAIDs from the given data.
    Args:
        data (list): A list of dictionaries representing variant data.
    Returns:
        list: A list of dictionaries representing the missing CAIDs.
    """
    res = []
    alts = set()
    valid_bases = {"A", "C", "G", "T"}
    refs = set()
    for one in data:
        refs.add(one["ref"])
        alts.add(one["alt"])
    if any(ref not in valid_bases for ref in refs):
        indels = check_new_indels(data)
        if len(indels) > 0:
            res = indels
        return res 
    if any(alt not in valid_bases for alt in alts):
        indels = check_new_indels(data)
        if len(indels) > 0:
            res = indels
        return res 
    pos = data[0]["pos"]
    chrom = data[0]["chrom"]
    ref = data[0]["ref"]
    dbsnp = data[0]["dbsnp"]
    hgvs = data[0]["hgvs"]
    if "genes_ncbi" in data[0]:
        genes = data[0]["genes_ncbi"]
        symbols = data[0]["genes_symbol"]
    else:
        genes = []
        symbols = []
    create_vcf_header(chrom, pmc_id)
    for alt in valid_bases:
        if alt not in alts:
            add_row_in_vcf(chrom, str(pos), ref, alt, pmc_id)
    get_results_vcf_file(pmc_id)
    new_caids = read_data_from_vcf_file(pmc_id)
    for new_caid in new_caids:
        temp = {}
        temp["caid"] = new_caid["caid"]
        temp["chrom"] = chrom
        temp["pos"] = pos
        temp["ref"] = ref
        temp["alt"] = new_caid["alt"]
        temp["hgvs"] = hgvs[:-1] + new_caid["alt"]
        temp["dbsnp"] = dbsnp
        temp["reportedSNP"] = False
        temp["reportedClinVar"] = False
        temp["genes_ncbi"] = genes
        temp["genes_symbol"] = symbols
        res.append(temp)
    return res


def reformat_body_variant_part(in_data: dict) -> dict:
    """
    Reformat the variant part of the body data.
    Args:
        in_data (dict): Dictionary containing variant information from response.
    Returns:
        dict: The reformatted variant part of the body data.
    """
    if not in_data:
        return {}
    temp = {}
    temp["type"] = "TextualBody"
    temp["value"] = in_data["caid"]
    temp["referenceAllele"] = in_data["ref"]
    temp["allele"] = in_data["alt"]
    temp["reportedSNP"] = in_data["reportedSNP"]
    temp["reportedClinVar"] = in_data["reportedClinVar"]
    return temp


def reformat_body_gene_part(in_data: dict) -> dict:
    """
    Reformat the gene part of the body data.
    Args:
        in_data (dict): Dictionary containing gene information from response.
    Returns:
        dict: The reformatted gene part of the body data.
    """
    if not in_data:
        return {}
    try:
        temp = {}
        temp["type"] = "TextualBody"
        temp["value"] = "GeneData"
        temp["geneSymbol"] = in_data["genes_symbol"]
        temp["geneNCBI"] = in_data["genes_ncbi"]
    except KeyError:
        LOGGER.error(
            f"Error occurred while reformatting gene part of body data. GENE SYMBOL or GENE NCBI not found. for {in_data}"
        )
        return {}
    return temp


def prepare_body_rs(need_body_new: list, pmc_id: str) -> None:
    """
    Prepare the body for a given list of IDs.
    Args:
        need_body_new (list): A list of IDs for which the body needs to be prepared.
    Returns:
        None
    """
    response = get_results_txt_file(f"{pmc_id}_rsids.txt")
    res = {}
    for data in response:
        temp = reformat_data_for_body(data)
        if "dbsnp" in temp:
            dbsnp = temp["dbsnp"]
            if dbsnp not in res:
                res[dbsnp] = [temp]
            else:
                res[dbsnp].append(temp)
    for snp in res:
        temp2 = collect_missing_caids(res[snp], pmc_id)
        if len(temp2) > 0:
            res[snp].extend(temp2)
    for id in need_body_new:
        body = []
        if id[2] == "0":
            id_non_zero = id[0:2] + id[3:]
        else:
            id_non_zero = id
        if id_non_zero in res:
            for j in range(len(res[id_non_zero])):
                body.append(reformat_body_variant_part(res[id_non_zero][j]))
            if (
                "genes_ncbi" in res[id_non_zero][0]
                and len(res[id_non_zero][0]["genes_ncbi"]) > 0
            ):
                body.append(reformat_body_gene_part(res[id_non_zero][0]))
        # check if the body is a list containing empty dictionaries
        if not any(body):
            body = []
        save_json(body, BODY_DIRECTORY + id + ".json")


def prepare_body_caid(caid: str) -> None:
    """
    Prepare the body data for a given CAID by fetching results, reformatting the data, and saving it as a JSON file.
    Args:
        caid (str): The CAID for which the body data needs to be prepared.
    Returns:
        None
    """
    response = get_results_caid(caid)
    res = reformat_data_for_body(response)
    body = [reformat_body_variant_part(res)]
    if ("genes_ncbi" in res and len(res["genes_ncbi"]) > 0):
        body.append(reformat_body_gene_part(res))
    if not any(body):
        body = []
    save_json(body, BODY_DIRECTORY + caid + ".json")


def prepare_body_complex(id: str, pmc_id: str) -> None:
    """
    Prepare the body data for a complex variant.
    Args:
        id (str): The identifier used to retrieve data for preparing the body.
    Returns:
        None
    """
    body = []
    rsid = re.match("rs[0-9]*", id).group(0)
    alt = id[-1]
    flag = False
    if rsid:
        response = get_results_rsid(rsid)
        ERROR_RESPOSNES = [
            {
                "description": "Internal error occurred. Please, report it as an error.",
                "errorType": "InternalServerError",
                "message": "bad lexical cast: source type value could not be interpreted as target",
            },
        ]
        if not response or response in ERROR_RESPOSNES:
            return []
        for data in response:
            res = reformat_data_for_body(data)
            pos = res["pos"]
            ref = res["ref"]
            chrom = res["chrom"]
            if "genes_ncbi" in res:
                genes = res["genes_ncbi"]
                symbols = res["genes_symbol"]
            else:
                genes = []
                symbols = []
            if res["alt"] == alt:
                flag = True
                body.append(reformat_body_variant_part(res))
                if ("genes_ncbi" in res and len(res["genes_ncbi"]) > 0):
                    body.append(reformat_body_gene_part(res))
                break
        if not flag:
            pos = res["pos"]
            ref = res["ref"]
            chrom = res["chrom"]
            create_vcf_header(chrom, pmc_id)
            add_row_in_vcf(chrom, str(pos), ref, alt, pmc_id)
            get_results_vcf_file(pmc_id)
            new_caids = read_data_from_vcf_file(pmc_id)
            for new_caid in new_caids:
                if new_caid.get("alt", None) == alt:
                    temp = {}
                    temp["caid"] = new_caid["caid"]
                    temp["chrom"] = chrom
                    temp["pos"] = pos
                    temp["ref"] = ref
                    temp["alt"] = new_caid["alt"]
                    temp["dbsnp"] = rsid
                    temp["reportedSNP"] = False
                    temp["reportedClinVar"] = False
                    temp["genes_ncbi"] = genes
                    temp["genes_symbol"] = symbols
                    body.append(reformat_body_variant_part(temp))
                    if (
                        len(temp["genes_ncbi"]) > 0
                    ):  # izmena - ne dodaje gene deo body-ja ukoliko nema podataka
                        body.append(reformat_body_gene_part(temp))
                    break
    if not any(body):
        body = []
    save_json(body, BODY_DIRECTORY + id + ".json")


def collect_w3c_body_per_pmcid_in_temp_dir(data: dict, pmc_id: str) -> None:
    import tempfile
    with tempfile.TemporaryDirectory() as temp_dir:
        collect_w3c_body_per_pmcid(data, pmc_id)
        
def collect_w3c_body_per_pmcid(data: dict, pmc_id: str) -> None:
    """
    Collects and prepares body data for each PMCID based on the results of variant search.
    Args:
        data (dict): Variant search result for PMCIDs.
    Returns:
        None
    """
    if os.path.isfile(EXISTING_BODIES_PATH):
        # global_variants = set(load_json(EXISTING_BODIES_PATH))
        global_variants = set(load_existing_bodies(EXISTING_BODIES_PATH))
        global_variants_raw = global_variants.copy()
    else:
        global_variants = set()
        global_variants_raw = set()
        # create a new file for existing bodies
        save_json(list(global_variants), EXISTING_BODIES_PATH)
        
    create_directory(BODY_DIRECTORY)
    need_body_rs, need_body_ca, need_body_complex = (
        find_exact_matches_of_rsid_caid_complex_type(data)
    )
    need_body_new_rs = [item for item in need_body_rs if item not in global_variants]
    if len(need_body_new_rs) > 0:
        prepare_text_for_query(need_body_new_rs, pmc_id)
        prepare_body_rs(need_body_new_rs, pmc_id)
    global_variants.update(need_body_new_rs)
    need_body_new_ca = [item for item in need_body_ca if item not in global_variants]
    if len(need_body_new_ca) > 0:
        for caid in need_body_new_ca:
            prepare_body_caid(caid)
    global_variants.update(need_body_new_ca)
    need_body_new_complex = [
        item for item in need_body_complex if item not in global_variants
    ]
    if len(need_body_new_complex) > 0:
        for id in need_body_new_complex:
            prepare_body_complex(id, pmc_id)
    global_variants.update(need_body_new_complex)
    # save_json(list(global_variants), EXISTING_BODIES_PATH)
    variants_diff = global_variants - global_variants_raw
    if variants_diff:
        for variant in variants_diff:
            append_to_existing_bodies(EXISTING_BODIES_PATH, variant)
    
    remove_temp_files(pmc_id)
    # save_json(list(global_variants), EXISTING_BODIES_PATH)


# prepare_text_for_query(["rs57275132"], "PMC123")
# prepare_body_rs(["rs57275132"], "PMC123")