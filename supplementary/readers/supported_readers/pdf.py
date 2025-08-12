import io
import multiprocessing
from tempfile import TemporaryDirectory

import fitz  # imports the pymupdf library
import pytesseract
from utils.logging.logging_setup import supplementary_error_logger
from fitz.fitz import FileDataError
from PIL import Image
from supplementary.readers.reader_interface import INPUT_TYPE, FormatReader
from supplementary.utils.data_fetching import (
    get_extension,
    get_material_name,
    get_pmcid,
)
from supplementary.utils.result_saver import get_output_type, save


class PDFFormatReader(FormatReader):
    def read_bytes(
        self,
        byte_contents,
        source: str,
        input_type=INPUT_TYPE.BYTES,
    ):
        if not byte_contents:
            return
        bytes = io.BytesIO(byte_contents)
        try:
            doc = fitz.open(stream=bytes, filetype="pdf")
        except FileDataError as e:
            supplementary_error_logger.error("%s | %s", source, str(e), exc_info=True)
            return None
        except Exception as e:
            supplementary_error_logger.error("%s | %s", source, str(e), exc_info=True)
            return None
        return self.process(doc, input_type, source)

    # def read_from_path(self, path, type=INPUT_TYPE.PATH):
    #     doc = fitz.open(path, filetype="pdf")
    #     return self.process(doc, type)
    #     pass

    def process(self, pdf_file, type: INPUT_TYPE, source: str = ""):
        to_save = process_pdf(pdf_file, source)

        if self.save:
            save(
                get_pmcid(source),
                get_material_name(source),
                to_save,
                get_output_type(get_extension(source)),
            )
        return to_save


def extract_text(page):
    return page.get_text()


def process_pdf(doc: fitz.fitz.Document, source: str):
    num_pages = doc.page_count
    pages = doc
    output = {}
    timeout_seconds = 15

    for i in range(num_pages):
        page = doc.load_page(i)
        text = apply_function_with_timeout(
            extract_text, page, timeout=timeout_seconds, source=source
        )
        output[i] = text
    if pages_with_images := list(filter(lambda page: page.get_images(), pages)):
        # print("Pages with images: ", pages_with_images)
        with TemporaryDirectory() as tempdir:
            for page in pages_with_images:
                image_file = f"{tempdir}/page-{page.number}.png"
                page.get_pixmap().save(image_file)
                text = str(pytesseract.image_to_string(Image.open(image_file)))
                text = text.replace("-\n", "")
                output[page.number] += "\n" + text
    return output


def apply_function_with_timeout(func, page, timeout, source):
    def target(queue, page):
        queue.put(func(page))

    queue = multiprocessing.Queue()
    process = multiprocessing.Process(target=target, args=(queue, page))
    process.start()

    process.join(timeout)
    if process.is_alive():
        process.terminate()
        process.join()
        supplementary_error_logger.error(
            f"PDF - {source} | Function - {func.__name__} | Timeout occurred for page {page.number} after {timeout} seconds"
        )
        # print(
        #     f"PDF - {source} | Function - {func.__name__} | Timeout occurred for page {page.number} after {timeout} seconds"
        # )
        return "ERROR - TIMEOUT"
    return queue.get()


if __name__ == "__main__":
    ...
