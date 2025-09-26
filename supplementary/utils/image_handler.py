import io
import re

import pytesseract
from PIL import Image
from utils.logging.logging_setup import supplementary_error_logger
import supplementary.utils.data_fetching as data_fetching

Image.MAX_IMAGE_PIXELS = 933_120_000
MAX_IMAGE_SIZE = 50_000_000  # 50 MB


def ocr_extract_text(image_file, source: str):
    if (file_size := len(image_file)) > MAX_IMAGE_SIZE:
        error_message = f"FILE TO LARGE -> {file_size=:_}\t {MAX_IMAGE_SIZE=:_}"
        supplementary_error_logger.error("%s | %s", source, error_message)

        return None
    text = str(
        pytesseract.image_to_string(Image.open(io.BytesIO(image_file)).convert("L"))
    )
    text = text.replace("\n", " ")
    text = re.sub(" +", " ", text)
    return text


def test_example():
    link = "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3420921/bin/pgen.1002907.s001.tiff"
    link = (
        "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC514612/bin/1472-6750-4-15-S1.TIFF"
    )
    link = "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3403905/bin/1471-2164-13-147-S7.png"
    link = (
        "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4133265/bin/pone.0104919.s001.tif"
    )
    link = "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3446521/bin/ar3871-S2.JPEG"
    link = "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3479429/bin/1471-2164-13-411-S2.jpeg"
    link = "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3404285/bin/11033_2012_1752_MOESM3_ESM.jpg"

    extension = data_fetching.get_extension(link)
    name = data_fetching.get_material_name(link)
    byte_contents = data_fetching.fetch_file(link)

    text = ocr_extract_text(byte_contents, extension)
    print(text)


if __name__ == "__main__":
    test_example()
    ...
