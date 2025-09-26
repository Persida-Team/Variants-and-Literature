import os
import sys
import time

# used to import readers.readers.READERS_DICT
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import json
from dataclasses import dataclass, field

import numpy as np

from ..readers.reader_interface import FormatReader
from ..readers.readers import get_reader

# from readers.readers import READERS_DICT, READERS_DICT_SAVE
from ..utils.data_fetching import fetch_file, get_material_name, get_pmcid
from ..utils.result_saver import OUTPUT_TYPE, save
from .. import variants_from_supplementary as vfs
from ..utils.data_fetching import get_extension
from ..utils.result_saver import get_output_type


def read_all_documents(input_path: str, extension: str) -> list[str]:
    """
    Reads all documents (URLs, paths, or both) from the supplementary_format.json file
    and returns a list of all documents with the given extension.

    Parameters
    ----------
    input_path : str
        The path to the supplementary_format.json file
    extension : str
        The extension to filter by

    Returns
    -------
    list[str]
        List of all documents with the given extension
    """
    with open(input_path, "r") as f:
        return json.load(f)[extension.upper()]


def check_if_url(input: str) -> bool:
    """
    Checks if the input is a URL

    Parameters
    ----------
    input : str
        The input to check

    Returns
    -------
    bool
        Whether the input is a URL
    """
    if "http" in input:
        return True
    return False


@dataclass
class Test:
    """
    Class for testing the readers

    Parameters
    ----------
    name : str
        The name of the test
    extension : str
        The extension of the files to test
    input_document_path : str, optional
        The path to the supplementary_format.json file, by default "supplementary_format.json"
    to_save : bool, optional
        Whether to save the output, by default False

    """

    name: str
    extension: str
    input_document_path: str = "supplementary_format.json"
    # input_document_path: str = (
    #     "/mnt/d/Storage/WORK/P/Clingen/PubMedCentral/50k_articles/supplementary_format.json"
    # )
    to_save: bool = False
    is_pipeline_preprocessing: bool = False
    all_documents: list[str] = field(init=False)
    reader: FormatReader | None = field(init=False)

    def __post_init__(self):
        if not self.is_pipeline_preprocessing:
            self.all_documents = read_all_documents(
                self.input_document_path, self.extension
            )
        if self.to_save:
            self.reader = get_reader(self.extension, save=True)
        else:
            self.reader = get_reader(self.extension)

    def run_test(self, iterable: iter, return_result: bool = False) -> list:
        """
        Runs the test on the given iterable

        Parameters
        ----------
        iterable : iter
            The iterable to run the test on

        Returns
        -------
        list
            The results of the test
        """
        all_results = []

        if self.is_pipeline_preprocessing:
            return run_pipeline_preprocessing(iterable, self.reader, self.extension)
        for i, document in enumerate(iterable):
            print(f"{i+1}/{len(iterable)}: {document}")
            if check_if_url(document):
                result = self.reader.read_bytes(fetch_file(document), document)
            else:
                result = self.reader.read_from_path(document)
            # TODO implement this better
            if result:
                type = get_output_type(get_extension(document)).value
                filename = get_material_name(document)
                # OUTPUT_FOLDER = "./var_supp_outputs/"
                OUTPUT_FOLDER = "./find_variants_from_supplementary_results"
                # print(result)
                print("Processing variants\t", type, filename, OUTPUT_FOLDER)
                metadata = {
                    get_pmcid(document): {
                        get_material_name(document): {
                            "type": type,
                        }
                    },
                }
                data_processor = vfs.DataProcessor(
                    type, result, "", filename, OUTPUT_FOLDER, metadata
                )
                data_processor.process_data()
                print("Processed variants")
                # if return_result:
                # all_results.append(result)
                ...
        return all_results

    def run_on_all_documents(self, start_from: str = "") -> list:
        """
        Runs the test on all documents

        Parameters
        ----------
        start_from : str, optional
            The document to start from/continue from, by default ""
        Returns
        -------
        list
            The results of the test
        """

        if not start_from:
            return self.run_test(self.all_documents)
        else:
            print(f"Starting from {start_from}")
            return self.run_test(
                self.all_documents[self.all_documents.index(start_from) :]
            )

    def run_on_subsample(self, n: int) -> list:
        """
        Runs the test on a subsample of the documents

        Parameters
        ----------
        n : int
            The number of documents to test

        Returns
        -------
        list

        """
        try:
            return self.run_test(np.random.choice(self.all_documents, n, replace=False))
        except Exception as e:
            # TODO implement this better
            pass

    def catch_errors_only(self):
        """
        Runs the test on all documents, but only catches errors and prints them out.

        Outputs
        -------
        documents URL or path that caused the error
        error message

        """
        for document in self.all_documents:
            try:
                self.run_test([document])
            except Exception as e:
                print(f"{document}\n{e}")
                with open(f"errors_{self.extension}.txt", "a") as f:
                    f.write(f"{document}\n{e}\n")


def run_pipeline_preprocessing(
    iterable: iter,
    reader: FormatReader,
    extension: str,
):
    """
    Runs the pipeline preprocessing on the given iterable

    Parameters
    ----------
    iterable : iter
        The iterable to run the pipeline preprocessing on
    reader : FormatReader
        The reader to use
    extension : str
        The extension of the files to test
    """

    for i, document in enumerate(iterable):
        # read bytes from the document using built in python
        print(document)
        result = reader.read_from_path(document)
        # NOTE: this is fine, cuz we pass items 1 by 1 and not multiple items in a list
        return result


if __name__ == "__main__":
    ...
