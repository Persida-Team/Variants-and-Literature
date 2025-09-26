import json
import utils.logging.error_templates as error_templates
from .test_interface import Test
from utils.logging.logging_setup import (
    supplementary_error_logger,
    supplementary_info_logger,
)
from .tests import (
    CSVTest,
    DOCTest,
    DOCXTest,
    JPEGTest,
    JPGTest,
    PDFTest,
    PNGTest,
    PPTTest,
    PPTXTest,
    TIFFTest,
    TIFTest,
    TXTTest,
    XLSTest,
    XLSXTest,
)

# skip
# from zip_test import ZIPTest


def SUPPORTED_TESTS():
    return {
        "CSV": CSVTest,
        "XLS": XLSTest,
        "XLSX": XLSXTest,
        "JPEG": JPEGTest,
        "JPG": JPGTest,
        "PDF": PDFTest,
        "PNG": PNGTest,
        "PPT": PPTTest,
        "PPTX": PPTXTest,
        "TIF": TIFTest,
        "TIFF": TIFFTest,
        "TXT": TXTTest,
        "DOC": DOCTest,
        "DOCX": DOCXTest,
    }


def run_on_all_from_dict(pmc_id: str, pmc_dict: dict[str, list[str]], output_dir: str):
    info_message = error_templates.started_info(pmc_id)
    supplementary_info_logger.info(info_message)
    # filter out the keys that are not supported
    pmc_dict = {
        k: v for k, v in pmc_dict.items() if k.upper() in SUPPORTED_TESTS().keys()
    }
    saved_files = []
    not_saved_files = []
    for extension, files in pmc_dict.items():
        current_test = Test(
            f"{pmc_id}_{extension}",
            extension=extension,
            is_pipeline_preprocessing=True,
        )
        for file in files:
            filename = file.split("/")[-1][: -len(extension) - 1]
            # print("Running test on\t", filename)
            try:
                result = current_test.run_test([file])
            except Exception as e:
                source = f"{pmc_id}_{filename}_{extension}"
                supplementary_error_logger.error(
                    "%s | %s", source, str(e), exc_info=True
                )
            if result:
                saved_files.append(f"{pmc_id}_{filename}_{extension}")
                with open(
                    f"{output_dir}/{pmc_id}_{filename}_{extension}.json", "w"
                ) as f:
                    json.dump(result, f)
            else:
                not_saved_files.append(f"{pmc_id}_{filename}_{extension}")
    info_message = error_templates.ended_info(pmc_id)
    supplementary_info_logger.info(info_message)
    info_message = error_templates.saved_vs_not_saved_info(
        pmc_id, saved_files, not_saved_files
    )
    supplementary_info_logger.info(info_message)


def run_on_all_from_dict_and_return(
    pmc_id: str, pmc_dict: dict[str, list[str]], output_dir: str | None = None
) -> dict[str, dict[str, str | list[str]]]:
    info_message = error_templates.started_info(pmc_id)
    supplementary_info_logger.info(info_message)
    # filter out the keys that are not supported
    pmc_dict = {
        k: v for k, v in pmc_dict.items() if k.upper() in SUPPORTED_TESTS().keys()
    }
    saved_files = []
    not_saved_files = []
    result_dict = {}
    for extension, files in pmc_dict.items():
        current_test = Test(
            f"{pmc_id}_{extension}",
            extension=extension,
            is_pipeline_preprocessing=True,
        )
        for file in files:
            filename = file.split("/")[-1][: -len(extension) - 1]
            # print("Running test on\t", filename)
            try:
                result = current_test.run_test([file])
            except Exception as e:
                source = f"{pmc_id}_{filename}_{extension}"
                supplementary_error_logger.error(
                    "%s | %s", source, str(e), exc_info=True
                )
            if result:
                result_dict[f"{pmc_id}_{filename}_{extension}"] = result
                saved_files.append(f"{pmc_id}_{filename}_{extension}")
                if output_dir:
                    with open(
                        f"{output_dir}/{pmc_id}_{filename}_{extension}.json", "w"
                    ) as f:
                        json.dump(result, f)
            else:
                not_saved_files.append(f"{pmc_id}_{filename}_{extension}")
    info_message = error_templates.ended_info(pmc_id)
    supplementary_info_logger.info(info_message)
    info_message = error_templates.saved_vs_not_saved_info(
        pmc_id, saved_files, not_saved_files
    )
    supplementary_info_logger.info(info_message)
    return result_dict


# run_on_all_from_dict("TEST_PMC_ID", {"pdf": test_over}, "test_files", save=True)
