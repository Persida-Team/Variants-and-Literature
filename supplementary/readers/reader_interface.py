from enum import Enum


class INPUT_TYPE(Enum):
    """
    Enum for input type
    """

    BYTES = "bytes"
    PATH = "str"


class FormatReader:
    """
    Interface for format readers

    Parameters
    ----------
    save : bool, optional
        Whether to save the output, by default False
    """

    def __init__(self, save=False):
        self.save = save

    def read_bytes(
        self,
        byte_contents: bytes | None,
        source: str,
        type: INPUT_TYPE = INPUT_TYPE.BYTES,
    ):
        """
        Reads the data contents in bytes format, and transforms it into a
        format that is suitable for further analysis.

        Parameters
        ----------
        byte_contents : bytes | None
            The bytes contents to be read
        source : str
            The source of the bytes contents, a URL

        Returns
        -------
        data suitable for further analysis
        """
        raise NotImplementedError

    def read_from_path(
        self,
        path: str,
        type: INPUT_TYPE = INPUT_TYPE.PATH,
    ):
        """
        Reads the data contents from a path, and transforms it into a
        format that is suitable for further analysis.

        Parameters
        ----------
        path : str
            The path to the file to be read

        Returns
        -------
        data suitable for further analysis
        """
        with open(path, "rb") as file:
            bytes = file.read()
        return self.read_bytes(bytes, path)


if __name__ == "__main__":
    ...
