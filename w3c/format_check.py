from jsonschema import ValidationError, validate

SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "event": {
            "type": "object",
            "properties": {
                "type": {"type": "string", "enum": ["cg-ldh-submission"]},
                "name": {"type": "string", "enum": ["VariantsInLiterature"]},
                "uuid": {
                    "type": "string",
                    "pattern": "^[a-fA-F0-9]{8}-([a-fA-F0-9]{4}-){3}[a-fA-F0-9]{12}$",
                },
                "sbj": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "pattern": "^PMC[0-9]{2,}$"},
                        # "id": {"type": "string", "pattern": "^PMC[0-9]{2,}_w3c$"},
                        "iri": {"type": "string"},
                    },
                    "required": ["id", "iri"],
                },
                "triggered": {
                    "type": "object",
                    "properties": {
                        "by": {
                            "type": "object",
                            "properties": {
                                "host": {"type": "string", "enum": ["persida-bio.com"]},
                                "id": {
                                    "type": "string",
                                    "enum": ["ldh_excerpt_http2pulsar"],
                                },
                                "iri": {
                                    "type": "string",
                                    "enum": [
                                        "https://github.com/BRL-BCM/ldh_excerpt_http2pulsar"
                                    ],
                                },
                            },
                            "required": ["host", "id", "iri"],
                        },
                        "at": {"type": "string", "format": "date-time"},
                    },
                    "required": ["by", "at"],
                },
            },
            "required": ["type", "name", "uuid", "sbj", "triggered"],
        },
        "content": {
            "type": "object",
            "properties": {
                "annotations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "@context": {"type": "string"},
                            "id": {
                                "type": "string",
                                "pattern": "^[a-fA-F0-9]{8}-([a-fA-F0-9]{4}-){3}[a-fA-F0-9]{12}$",
                            },
                            "created": {"type": "string", "format": "date-time"},
                            "label": {"type": "string"},
                            "publicationId": {
                                "type": "string",
                                "pattern": "^PMC[0-9]{2,}+$",
                            },
                            "variantMatch": {"type": "string"},
                            "articleData": {
                                "type": "object",
                                "properties": {
                                    "articleIDs": {
                                        "type": "object",
                                        "properties": {
                                            "PMCID": {"type": ["string", "null"]},
                                            "PMID": {"type": ["string", "null"]},
                                            "DOI": {"type": ["string", "null"]},
                                        },
                                    },
                                    "publicationType": {"type": "string"},
                                    "supplementaryMaterial": {
                                        "type": "object",
                                        "properties": {
                                            "type": {"type": "string"},
                                            "items": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "format": {"type": "string"},
                                                        "link": {"type": "string"},
                                                        "info": {"type": "string"},
                                                    },
                                                },
                                            },
                                        },
                                    },
                                    "tags": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                    },
                                },
                                "required": ["articleIDs"],
                            },
                            "body": {
                                "type": "object",
                                "properties": {
                                    "type": {"type": "string"},
                                    "items": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "type": {
                                                    "type": "string",
                                                    "enum": ["TextualBody"],
                                                },
                                                "value": {"type": "string"},
                                                "referenceAllele": {"type": "string"},
                                                "allele": {"type": "string"},
                                                "reportedSNP": {"type": "boolean"},
                                                "reportedClinVar": {"type": "boolean"},
                                                "geneSymbol": {
                                                    "type": "array",
                                                    "items": {"type": "string"},
                                                },
                                                "geneNCBI": {
                                                    "type": "array",
                                                    "items": {"type": "integer"},
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                            "target": {
                                "type": "object",
                                "properties": {
                                    "type": {"type": "string", "enum": ["List"]},
                                    "items": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "source": {"type": "string"},
                                                "selector": {
                                                    "type": "array",
                                                    "items": {
                                                        "type": "object",
                                                        "properties": {
                                                            "type": {"type": "string"},
                                                            "exact": {"type": "string"},
                                                            "prefix": {
                                                                "type": "string"
                                                            },
                                                            "suffix": {
                                                                "type": "string"
                                                            },
                                                            "sourceDescription": {
                                                                "type": "string"
                                                            },
                                                            "pageID": {
                                                                "type": "integer"
                                                            },
                                                            "tableID": {
                                                                "type": "string"
                                                            },
                                                            "sheetID": {
                                                                "type": "string"
                                                            },
                                                            "positionID": {
                                                                "type": "string"
                                                            },
                                                            "foundInRows": {
                                                                "type": "array",
                                                                "items": {
                                                                    "type": "object"
                                                                },
                                                            },
                                                            "additionalInfo": {
                                                                "type": "array",
                                                                "items": {
                                                                    "type": "string"
                                                                },
                                                            },
                                                            "foundInColumnHeader": {
                                                                "type": "object",
                                                                "items": {
                                                                    "type": "object"
                                                                },
                                                            },
                                                        },
                                                        "required": [
                                                            "type",
                                                            "exact",
                                                            "sourceDescription",
                                                        ],
                                                    },
                                                },
                                            },
                                            "required": ["source", "selector"],
                                        },
                                    },
                                },
                                "required": ["type", "items"],
                            },
                        },
                        "required": [
                            "@context",
                            "id",
                            "created",
                            "label",
                            "publicationId",
                            "variantMatch",
                            "articleData",
                            "target",
                        ],
                    },
                }
            },
            "required": ["annotations"],
        },
    },
    "required": ["event", "content"],
}


def format_check(data: dict):
    try:
        validate(instance=data, schema=SCHEMA)
        return True
    except ValidationError as e:
        # print(f"Validation error: {e.message}")
        with open("format_check_errors.txt", "a") as f:
            f.write(f"Validation error: {e.message}\n")
            f.write(f"Error details: {e}\n")
        return False


"""
Testing format check on previous results code below!
"""
import json
import os
from concurrent.futures import ProcessPoolExecutor, as_completed

from tqdm import tqdm


def process_batch(file_paths):
    good = 0
    bad = 0
    good_files = []

    for path in file_paths:
        try:
            with open(path, "r", encoding="utf-8") as fp:
                data = json.load(fp)
            if format_check(data):
                good += 1
                good_files.append(path)
            else:
                with open("bad_files.txt", "a") as bf:
                    bf.write(f"{path}\n\n{data}\n\n")
                bad += 1
        except Exception:
            bad += 1

    return good, bad, good_files


def chunk_list(lst, chunk_size):
    for i in range(0, len(lst), chunk_size):
        yield lst[i : i + chunk_size]


def testing_the_function():
    input_w3c_documents_path = (
        "/home/novak/Clingen/pipeline/w3c/results/" + "300k_w3c_submitted/"
    )
    file_paths = []

    for subfolder in os.listdir(input_w3c_documents_path):
        subfolder_path = os.path.join(input_w3c_documents_path, subfolder)
        if os.path.isdir(subfolder_path):
            for filename in os.listdir(subfolder_path):
                if filename.endswith("response.json"):
                    continue
                full_path = os.path.join(subfolder_path, filename)
                if os.path.isfile(full_path):
                    file_paths.append(full_path)

    # for file in file_paths:
    #     with open(file, "r", encoding="utf-8") as fp:
    #         data = json.load(fp)
    #     format_check(data)
    # quit()
    max_workers = 20
    batch_size = 100

    total_good = 0
    total_bad = 0
    all_good_filenames = []

    print(f"Processing {len(file_paths)} files using {max_workers} processes...")

    batches = list(chunk_list(file_paths, batch_size))

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_batch, batch) for batch in batches]

        for future in tqdm(as_completed(futures), total=len(futures)):
            good, bad, good_files = future.result()
            total_good += good
            total_bad += bad
            all_good_filenames.extend(good_files)

    with open("good_filenames.txt", "w", encoding="utf-8") as fp:
        fp.write("\n".join(all_good_filenames))

    total = total_good + total_bad
    percent_good = 100 * total_good / total if total else 0
    print(
        f"\nFinished checking. Good: {total_good}, Bad: {total_bad}, %good: {percent_good:.2f}"
    )


if __name__ == "__main__":
    testing_the_function()
