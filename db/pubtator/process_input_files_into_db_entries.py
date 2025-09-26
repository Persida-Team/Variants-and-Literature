import re

import VARIABLES as var


def validate_variant(data: str) -> bool:
    """
    Validate a variant based on certain patterns.
    Args:
        data (str): The variant data to be validated.
    Returns:
        bool: True if the data is a valid variant, False otherwise.
    """
    patterns = [
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


def get_pm_ids():
    # return set([x["pm_id"] for x in get_human_pm_ids()])
    print("Loading pm_ids from file...")
    with open(var.HUMAN_PM_IDS, "r") as file:
        for line in file:
            yield line.strip()
        # pm_ids = set(line.strip() for line in file)
    # return pm_ids


def get_human_pm_ids():
    ids = get_pm_ids()
    for pm_id in ids:
        yield {"pm_id": pm_id}
    return
    HUMAN_ID = "9606"
    with open(var.SPECIES, "r") as file:
        for line in file:
            columns = line.strip().split("\t")
            if columns[2] == HUMAN_ID:
                yield {"pm_id": columns[0]}


def get_gene_ncbi_ids(skip=None):
    # human genes file is around 40 MB
    import pandas as pd

    GENE_SYMBOL_COLUMN = "Symbol_from_nomenclature_authority"
    hg_df = pd.read_csv(var.HUMAN_GENES, sep="\t")
    hg_df = hg_df[hg_df["#tax_id"] == 9606][["#tax_id", "GeneID", GENE_SYMBOL_COLUMN]]
    # print(len(hg_df), len(hg_df[GENE_SYMBOL_COLUMN].unique()))
    # print(
    #     len(hg_df[hg_df[GENE_SYMBOL_COLUMN] != "-"])
    #     - len(hg_df[GENE_SYMBOL_COLUMN].unique())
    # )
    # print(len(hg_df) == len(hg_df[GENE_SYMBOL_COLUMN].unique()))

    # print(hg_df[hg_df[GENE_SYMBOL_COLUMN] == "MT-RNR1"])

    # get duplicate symbols
    # non_unique_symbols = hg_df[hg_df[GENE_SYMBOL_COLUMN].duplicated(keep=False)]
    # print(non_unique_symbols)
    # non_unique_symbols.to_csv("non_unique_symbols.csv", index=False)
    pm_ids = set(get_pm_ids())
    valid_gene_ids = set(hg_df["GeneID"].astype(str))
    print("Skip to:", skip)
    with open(var.GENES, "r") as file:
        for i, line in enumerate(file):
            if skip and i < skip:
                print(f"Skipping line {i}", end="\r")
                continue
            columns = line.strip().split("\t")
            pm_id, ncbi_id = columns[0], columns[2]
            if pm_id in pm_ids and ncbi_id in valid_gene_ids:
                symbol_row = hg_df[hg_df["GeneID"].astype(str) == ncbi_id]
                hgnc_symbol = (
                    symbol_row[GENE_SYMBOL_COLUMN].values[0]
                    if not symbol_row.empty
                    else None
                )
                if not hgnc_symbol or hgnc_symbol == "-":
                    continue
                yield {"pm_id": pm_id, "ncbi_id": ncbi_id, "hgnc_symbol": hgnc_symbol}


def get_disease_original_ontology():
    pm_ids = set(get_pm_ids())
    with open(var.DISEASE, "r") as file:
        for line in file:
            columns = line.strip().split("\t")
            if columns[0] in pm_ids:
                yield {"pm_id": columns[0], "original_ontology": columns[2]}


def get_variants_data():
    pm_ids = set(get_pm_ids())
    with open(var.VARIANTS, "r") as file:
        for line in file:
            columns = line.strip().split("\t")
            if columns[0] in pm_ids and validate_variant(columns[3]):
                yield {"pm_id": columns[0], "variant_data": (columns[2], columns[3])}


# species_generator = get_human_pm_ids()
# print(len(list(species_generator)))
