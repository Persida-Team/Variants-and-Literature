from dataclasses import dataclass

from .test_interface import Test


@dataclass
class TXTTest(Test):
    extension: str = "txt"


@dataclass
class ZIPTest(Test):
    extension: str = "zip"


@dataclass
class DOCTest(Test):
    extension: str = "doc"


@dataclass
class DOCXTest(Test):
    extension: str = "docx"


@dataclass
class TIFFTest(Test):
    extension: str = "tiff"


@dataclass
class TIFTest(Test):
    extension: str = "tif"


@dataclass
class PPTXTest(Test):
    extension: str = "pptx"


@dataclass
class PPTTest(Test):
    extension: str = "ppt"


@dataclass
class PNGTest(Test):
    extension: str = "png"


@dataclass
class PDFTest(Test):
    extension: str = "pdf"


@dataclass
class JPGTest(Test):
    extension: str = "jpg"


@dataclass
class JPEGTest(Test):
    extension: str = "jpeg"


@dataclass
class XLSTest(Test):
    extension: str = "xls"


@dataclass
class XLSXTest(Test):
    extension: str = "xlsx"


@dataclass
class CSVTest(Test):
    extension: str = "csv"
