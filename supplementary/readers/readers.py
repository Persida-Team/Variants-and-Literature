# from readers.reader_interface import FormatReader
# from readers.supported_readers.csv import CSVFormatReader
# from readers.supported_readers.excel import EXCELFormatReader
# from readers.supported_readers.pdf import PDFFormatReader
# from readers.supported_readers.powerpoint import PPTXFormatReader
# from readers.supported_readers.txt import TXTFormatReader
# from readers.supported_readers.image import IMAGEFormatReader
# from readers.supported_readers.zip import ZIPFormatReader

"""

ALL AVAILABLE EXTENSIONS

'TIFF', 'XLS', 'PDF', 'TXT', 'DOC', 'DOCX', 'JPEG',
'TIF', 'XLSX', 'PNG', 'JPG', 'ZIP', 'TIFFF', 'HTML',
'PPTX', 'PPT', 'EPS', 'FA', 'TREE', 'BMP', 'GZ', 'BED',
'GFF', 'HTM', 'CSV', 'MPEG', 'AVI', 'RDA', 'TGZ', 'MOV',
'RAR', 'WMV', 'MP4', 'RM5', 'XML', 'TFIF', 'RTF', 'AB1',
'R', 'RDATA', 'SAV', 'GIF'

"""
READERS = {
    "csv": "supplementary.readers.supported_readers.csv.CSVFormatReader",
    "xls": "supplementary.readers.supported_readers.excel.EXCELFormatReader",
    "xlsx": "supplementary.readers.supported_readers.excel.EXCELFormatReader",
    "pdf": "supplementary.readers.supported_readers.pdf.PDFFormatReader",
    "ppt": "supplementary.readers.supported_readers.powerpoint.PPTXFormatReader",
    "pptx": "supplementary.readers.supported_readers.powerpoint.PPTXFormatReader",
    "txt": "supplementary.readers.supported_readers.txt.TXTFormatReader",
    "png": "supplementary.readers.supported_readers.image.IMAGEFormatReader",
    "jpg": "supplementary.readers.supported_readers.image.IMAGEFormatReader",
    "jpeg": "supplementary.readers.supported_readers.image.IMAGEFormatReader",
    "tif": "supplementary.readers.supported_readers.image.IMAGEFormatReader",
    "tiff": "supplementary.readers.supported_readers.image.IMAGEFormatReader",
    "zip": "supplementary.readers.supported_readers.zip.ZIPFormatReader",
    "doc": "supplementary.readers.supported_readers.word.WORDFormatReader",
    "docx": "supplementary.readers.supported_readers.word.WORDFormatReader",
}

# # Add new readers here
# READERS_DICT: dict[str, FormatReader] = {
#     "csv": CSVFormatReader(),
#     "txt": TXTFormatReader(),
#     "xls": EXCELFormatReader(),
#     "pdf": PDFFormatReader(),
#     "pptx": PPTXFormatReader(),
#     "ppt": PPTXFormatReader(),
#     "png": IMAGEFormatReader(),
#     "jpeg": IMAGEFormatReader(),
#     "jpg": IMAGEFormatReader(),
#     "tiff": IMAGEFormatReader(),
#     "tif": IMAGEFormatReader(),
#     "zip" : ZIPFormatReader(),
# }


# # Add new readers here
# READERS_DICT_SAVE: dict[str, FormatReader] = {
#     "csv": CSVFormatReader(save=True),
#     "txt": TXTFormatReader(save=True),
#     "xls": EXCELFormatReader(save=True),
#     "pdf": PDFFormatReader(save=True),
#     "pptx": PPTXFormatReader(save=True),
#     "ppt": PPTXFormatReader(save=True),
#     "png": IMAGEFormatReader(save=True),
#     "jpeg": IMAGEFormatReader(save=True),
#     "jpg": IMAGEFormatReader(save=True),
#     "tiff": IMAGEFormatReader(save=True),
#     "tif": IMAGEFormatReader(save=True),
#     "zip" : ZIPFormatReader(save=True),

# }


def get_reader(file_extension, save=False):
    if reader_class_reference := READERS.get(file_extension):
        module_name, class_name = reader_class_reference.rsplit(".", 1)
        # module_name = "." + module_name.split(".", 1)[-1]
        module = __import__(module_name, fromlist=[class_name])
        reader_class = getattr(module, class_name)
        return reader_class(save=save)
    else:
        return None


SUPPORTED_EXTENSIONS = [
    "csv",
    "txt",
    "xls",
    "xlsx",
    "pdf",
    "pptx",
    "ppt",
    "png",
    "jpeg",
    "jpg",
    "tiff",
    "tif",
    "doc",
    "docx",
]
