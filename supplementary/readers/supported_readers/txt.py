from supplementary.readers.reader_interface import INPUT_TYPE, FormatReader
from supplementary.utils.data_fetching import (
    get_extension,
    get_material_name,
    get_pmcid,
)
from supplementary.utils.result_saver import get_output_type, save
from utils.logging.logging_setup import supplementary_error_logger


class TXTFormatReader(FormatReader):
    def read_bytes(self, byte_contents, source: str, type=INPUT_TYPE.BYTES):
        if not byte_contents:
            return None
        txt_file = try_to_decode(byte_contents)
        if not txt_file:
            supplementary_error_logger.error("%s ", source)
            return None
        return self.read(txt_file, type, source)

    # def read_from_path(self, path, type=INPUT_TYPE.PATH):
    #     # TODO: open file and read contents
    #     return self.read(path, type)
    #     pass

    def read(self, txt_file, type: INPUT_TYPE, source: str = ""):
        # print(txt_file)

        to_save = txt_file
        if self.save:
            save(
                get_pmcid(source),
                get_material_name(source),
                to_save,
                get_output_type(get_extension(source)),
            )
        return to_save


def try_to_decode(byte_contents):
    decoded_text = None
    for encoding in AVAILABLE_TXT_ENCODINGS:
        try:
            decoded_text = byte_contents.decode(encoding)
            break
        except UnicodeDecodeError:
            # TODO: log error or just pass?
            pass
    return decoded_text


# source: https://docs.python.org/3/library/codecs.html#standard-encodings
AVAILABLE_TXT_ENCODINGS = [
    "ascii",
    "utf_8",
    "utf_16",
    "utf_32",
    "utf_7",
    "utf_8_sig",
    "utf_16_be",
    "utf_16_le",
    "utf_32_be",
    "utf_32_le",
    "big5",
    "big5hkscs",
    "cp037",
    "cp273",
    "cp424",
    "cp437",
    "cp500",
    "cp720",
    "cp737",
    "cp775",
    "cp850",
    "cp852",
    "cp855",
    "cp856",
    "cp857",
    "cp858",
    "cp860",
    "cp861",
    "cp862",
    "cp863",
    "cp864",
    "cp865866",
    "cp869",
    "cp874",
    "cp875932",
    "cp949",
    "cp950",
    "cp1006",
    "cp1026",
    "cp1125",
    "cp1140",
    "cp1250",
    "cp1251",
    "cp1252",
    "cp1253",
    "cp1254",
    "cp1255",
    "cp1256",
    "cp125",
    "cp1258",
    "euc_jp",
    "euc_jis_2004",
    "euc_jisx0213",
    "euc_kr",
    "gb2312",
    "gbk",
    "gb18030",
    "hz",
    "iso2022_jp",
    "iso2022_jp_1",
    "iso2022_jp_2",
    "iso2022_jp_2004",
    "iso2022_jp_3",
    "iso2022_jp_ext",
    "iso2022_kr",
    "latin_1",
    "iso8859_2",
    "iso8859_3",
    "iso8859_4",
    "iso8859_5",
    "iso8859_6",
    "iso8859_7",
    "iso8859_8",
    "iso8859_9",
    "iso8859_10",
    "iso8859_11",
    "iso8859_12",
    "iso8859_13",
    "iso8859_14",
    "iso8859_15",
    "iso8859_16",
    "johab",
    "koi8_r",
    "koi8_t",
    "koi8_u",
    "kz1048",
    "mac_cyrillic",
    "mac_greek",
    "mac_iceland",
    "mac_latin2",
    "mac_roman",
    "mac_turkish",
    "ptcp154",
    "shift_jis",
    "shift_jis_2004",
    "shift_jisx0213",
]


if __name__ == "__main__":
    ...
