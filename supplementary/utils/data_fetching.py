import os
import time
import requests
from utils.env_utils import get_env_or_fail


def create_filename(url: str) -> str:
    """
    Extracts the filename from a URL, where the filename is
    created as a PMCXXXXXXX_supplementary_file_name.extension

    Parameters
    ----------
    url : str
        The URL to extract the filename from

    Returns
    -------
    str
        The filename

    Example
    --------
    input
        "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3430663/bin/pone.0044154.s001.xls"
    output
        "PMC3430663_pone.0044154.s001.xls"
    """
    pmcid, name = url.split("articles/")[1].split("/bin/")
    # return pmcid, name
    return pmcid + "_" + name


def get_pmcid(url: str) -> str:
    """
    Extracts the PMC ID from a URL.
    Note: The PMC ID contains the PMC prefix

    Parameters
    ----------
    url : str
        The URL to extract the PMC ID from

    Returns
    -------
    str
        The PMC ID

    """
    # "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3531492/bin/pgen.1003150.s001.csv",
    pmcid = url.split("pmc/articles/")[1].split("/bin/")[0]
    return pmcid


def get_material_name(url: str) -> str:
    """
    Extracts the material name from a URL by concatenating the
    file name and the file extension with an underscore

    Parameters
    ----------
    url : str
        The URL to extract the material name from

    Returns
    -------
    str
        The material name

    Example
    --------
    input
        "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3430663/bin/pone.0044154.s001.xls"
    output
        "pone.0044154.s001_xls"
    """
    # "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3531492/bin/pgen.1003150.s001.csv",
    name, extension = os.path.splitext(url.split("/bin/")[1])

    return name + "_" + extension[1:]


def get_extension(url: str) -> str:
    """
    Extracts the extension from a URL

    Parameters
    ----------
    url : str
        The URL to extract the extension from

    Returns
    -------
    str
        The extension
    """
    extension = url.split(".")[-1]
    return extension


def create_directory(path: str) -> None:
    """
    Creates a directory if it does not exist

    Parameters
    ----------
    path : str
        The path to the directory to create

    Returns
    -------
    None

    """
    try:
        os.makedirs(path)
    except OSError as e:
        number = e.errno
        if number == 17:  # path exists
            return
        if number == 13:  # permission
            print("data_fetching.py -> create_directory -> permission denied: ", path)
            return


def save_file_to_disc(destination_directory: str, url: str, byte_content) -> None:
    """
    Saves a file fetched by the URL to disc

    Parameters
    ----------
    destination_directory : str
        The directory to save the file to
    url : str
        The URL to fetch the file from
    byte_content : bytes
        The content of the file as bytes

    Returns
    -------
    None

    """
    file_name = create_filename(url)
    extension = get_extension(url)
    directory = os.path.join(destination_directory, extension)
    file_path = os.path.join(directory, file_name)
    create_directory(directory)
    with open(file_path, "wb") as file:
        file.write(byte_content)


def fetch_file(
    url,
    destination_directory=get_env_or_fail("DOWNLOAD_DESTINATION_DIRECTORY"),
    save_to_disc=False,
) -> bytes | None:
    """
    Fetches a file from a URL and returns the content as bytes.
    If save_to_disc is True, the file is saved to disc

    Parameters
    ----------
    url : str
        The URL to fetch the file from
    destination_directory : str, optional
        The directory to save the file to, by default DOWNLOAD_DESTINATION_DIRECTORY
    save_to_disc : bool, optional
        Whether to save the file to disc, by default False

    Returns
    -------
    bytes | None
        The content of the file as bytes or None if the status code is not 200
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    RETRY_ATTEMPTS = 3
    RETRY_DELAY = 15
    for attempt in range(RETRY_ATTEMPTS):
        try:
            response = requests.get(url, headers=headers, timeout=60)
            break
        except requests.exceptions.ReadTimeout:
            print(
                f"ReadTimeout {attempt} and sleeping for {RETRY_DELAY} seconds url: {url}"
            )
            time.sleep(RETRY_DELAY)
    else:
        print("Failed to fetch file from ", url)
        return None

    # response = requests.get(url)
    if response.status_code == 200:
        byte_content = response.content
        if save_to_disc:
            save_file_to_disc(destination_directory, url, byte_content)
        return byte_content
    else:
        print(f"Status {response.status_code} for {url}")
        return None


if __name__ == "__main__":
    # file = "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3430663/bin/pone.0044154.s001.xls"
    # print(create_filename(file))
    ...
    file_url = (
        "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3430663/bin/pone.0044154.s001.xls"
    )
    file_url = (
        "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3531492/bin/pgen.1003150.s001.csv"
    )
    # destination_dir = '/path/to/your/directory'
    # file = fetch_file(file_url, save_to_disc=False)

    # scv_file = io.BytesIO(file)
    # df = pd.read_csv(scv_file)

    # print(df.head())
