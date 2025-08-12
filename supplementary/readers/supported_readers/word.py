import io
import subprocess

# Specify the maximum file size (in bytes) for conversion
from tempfile import TemporaryDirectory

import fitz  # imports the pymupdf library
import pandas as pd
import supplementary.utils.logging.error_templates as error_templates
from supplementary.readers.reader_interface import INPUT_TYPE, FormatReader
from supplementary.readers.supported_readers.pdf import process_pdf
from supplementary.utils.data_fetching import get_extension, get_material_name, get_pmcid
from supplementary.utils.logging.logger_setup import setup_logging
from supplementary.utils.result_saver import get_output_type, save
from utils.logging.logging_setup import supplementary_error_logger, supplementary_info_logger


MAX_FILE_SIZE = 25000000  # 25 MB
LIBREOFFICE_TIMEOUT = 60 * 5  # 5 minutes


class WORDFormatReader(FormatReader):
    def read_bytes(
        self,
        byte_contents,
        source: str,
        input_type=INPUT_TYPE.BYTES,
    ):
        if not byte_contents:
            return  # if file wasn't fetched or something
        # Note: This is a workaround for the fact that docx and doc doesn't support paging
        # so converting to pdf will allow for the same readability, but with paging
        word_file = io.BytesIO(byte_contents)
        # Check the file size
        file_size = len(byte_contents)
        if file_size > MAX_FILE_SIZE:
            error_message = f"FILE TO LARGE -> {file_size=:_}\t {MAX_FILE_SIZE=:_}"
            supplementary_error_logger.error("%s | %s", source, error_message)

            return None

        file_name = "_".join(source.split("/")[-2:])  # PMCid_materialName
        with TemporaryDirectory() as tempdir:
            word_file = f"{tempdir}/{file_name}"
            # remove extension from file_name
            file_name_no_extension = file_name.split(".")[0]
            pdf_file = f"{tempdir}/{file_name_no_extension}.pdf"
            with open(word_file, "wb") as f:
                f.write(byte_contents)
            try:
                # Convert to PDF using LibreOffice
                subprocess.run(
                    ["libreoffice", "--headless", "--convert-to", "pdf", file_name],
                    cwd=tempdir,
                    check=True,
                    timeout=LIBREOFFICE_TIMEOUT,
                )
                with open(pdf_file, "rb") as f:
                    pdf_file = io.BytesIO(f.read())
            except subprocess.CalledProcessError as e:
                supplementary_error_logger.error(error_templates.libreoffice_conversion_error(source))
                return None
            except subprocess.TimeoutExpired as e:
                supplementary_error_logger.error(error_templates.libreoffice_conversion_timeout(source))
                return None
            except Exception as e:
                supplementary_error_logger.error("%s | %s", source, str(e), exc_info=True)
                return
        return self.process(pdf_file, input_type, source)

    # def read_from_path(self, path, type=INPUT_TYPE.PATH):
    #     # TODO: Implement
    #     # return self.process(path, type)
    #     pass

    def process(self, pdf_file, type: INPUT_TYPE, source: str = ""):
        pdf_doc = fitz.open(stream=pdf_file, filetype="pdf")
        to_save = process_pdf(pdf_doc, source)
        if self.save:
            save(
                get_pmcid(source),
                get_material_name(source),
                to_save,
                get_output_type(get_extension(source)),
            )
        return to_save


if __name__ == "__main__":
    ...
