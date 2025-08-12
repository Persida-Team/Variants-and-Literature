from supplementary.readers.reader_interface import INPUT_TYPE, FormatReader
from supplementary.utils.data_fetching import (
    get_extension,
    get_material_name,
    get_pmcid,
)
from supplementary.utils.image_handler import ocr_extract_text
from supplementary.utils.result_saver import get_output_type, save
from utils.logging.logging_setup import supplementary_error_logger



class IMAGEFormatReader(FormatReader):
    def read_bytes(
        self,
        byte_contents,
        source: str,
        input_type=INPUT_TYPE.BYTES,
    ):
        if not byte_contents:
            return
        # bytes = io.BytesIO(byte_contents)
        try:
            return self.process(byte_contents, input_type, source)
        except Exception as e:
            supplementary_error_logger.error("%s | %s", source, str(e), exc_info=True)
            return None

    # def read_from_path(self, path, type=INPUT_TYPE.PATH):
    #     # TODO: Implement
    #     # return self.process(doc, type)
    #     pass

    def process(self, image_file, type: INPUT_TYPE, source: str = ""):
        try:
            to_save = ocr_extract_text(image_file, source)
        except Exception as e:
            supplementary_error_logger.error("%s | %s", source, str(e), exc_info=True)
            return None
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
