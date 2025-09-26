import io
import zipfile
from supplementary.readers.reader_interface import INPUT_TYPE, FormatReader
from supplementary.readers.readers import SUPPORTED_EXTENSIONS, get_reader
from supplementary.utils.data_fetching import (
    get_extension,
    get_material_name,
    get_pmcid,
)
from supplementary.utils.result_saver import get_output_type, pack_result, save
from utils.logging.logging_setup import supplementary_error_logger


class ZIPFormatReader(FormatReader):
    def read_bytes(self, byte_contents, source: str, input_type=INPUT_TYPE.BYTES):
        if not byte_contents:
            return
        bytes = io.BytesIO(byte_contents)
        return self.process(bytes, input_type, source)

    # def read_from_path(self, path, type=INPUT_TYPE.PATH):
    #     # TODO: Implement
    #     # return self.process(doc, type)
    #     pass

    def process(self, zip_file, type: INPUT_TYPE, source: str = ""):
        to_save = {}

        with zipfile.ZipFile(zip_file, "r") as z:
            files_to_extract = list(
                filter(
                    lambda x: x.split(".")[-1].lower() in SUPPORTED_EXTENSIONS,
                    map(lambda x: x.filename, z.infolist()),
                )
            )
            for file in files_to_extract:
                reader = get_reader(extension := file.split(".")[-1].lower())
                try:
                    read_data = z.read(file)

                except zipfile.BadZipFile as e:
                    supplementary_error_logger.error(
                        "%s | %s", source, str(e), exc_info=True
                    )
                    continue
                result = reader.read_bytes(read_data, source)
                to_save = pack_result(to_save, file, result, extension)
                # print(result)
            # print(to_save)
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
