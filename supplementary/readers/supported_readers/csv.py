import io

import pandas as pd

from supplementary.output_formatters.pandas_formatter import transform_table
from supplementary.readers.reader_interface import INPUT_TYPE, FormatReader
from supplementary.utils.data_fetching import (
    get_material_name,
    get_pmcid,
    get_extension,
)
from supplementary.utils.result_saver import get_output_type, save

from utils.logging.logging_setup import supplementary_error_logger


class CSVFormatReader(FormatReader):
    def read_bytes(
        self,
        byte_contents,
        source: str,
        type=INPUT_TYPE.BYTES,
    ):
        if not byte_contents:
            return
        csv_file = io.BytesIO(byte_contents)
        return self.read(csv_file, type, source)

    # def read_from_path(self, path, type=INPUT_TYPE.PATH):
    #     return self.read(path, type)
    #     pass

    def read(self, csv_file, type: INPUT_TYPE, source: str = ""):
        try:
            df = pd.read_csv(csv_file)
        # TODO transform data into a desirable output
        except UnicodeDecodeError as e:
            supplementary_error_logger.error("%s | %s", source, str(e), exc_info=True)
            return None
        except pd.errors.ParserError as e:
            if "Buffer overflow caught" in str(e):
                supplementary_error_logger.error(
                    "%s | %s", source, str(e), exc_info=True
                )
                return None
            # if not Buffer overflow error, then try to use a different separator
            if type == INPUT_TYPE.BYTES:
                separator = infer_csv_separator_bytes(csv_file)
                print(e, f"\n{separator=}")
                try:
                    df = pd.read_csv(csv_file, sep=separator)
                except pd.errors.EmptyDataError as e:
                    supplementary_error_logger.error(
                        "%s | %s", source, str(e), exc_info=True
                    )
                    return None
                # TODO
                # what happens if we try read_csv(csv_file, sep = separator)?
                # catch pandas.errors.EmptyDataError: No columns to parse from file
            else:
                supplementary_error_logger.error(
                    "%s | %s", source, str(e), exc_info=True
                )
                return None

        to_save = transform_table(df)
        if self.save:
            save(
                get_pmcid(source),
                get_material_name(source),
                to_save,
                get_output_type(get_extension(source)),
            )
        return to_save


def infer_csv_separator_bytes(bytes_contents):
    CSV_SEPARATORS = [",", "\t", ";", "|"]

    # Convert the io.BytesIO object to bytes data
    bytes_data = bytes_contents.getvalue()

    separator_counts = {
        sep: bytes_data[:2024].count(sep.encode()) for sep in CSV_SEPARATORS
    }
    return max(separator_counts, key=separator_counts.get)


if __name__ == "__main__":
    ...
