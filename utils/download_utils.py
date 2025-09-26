from functools import partial

import requests
from bs4 import BeautifulSoup

from utils.filesystem_utils import save_file, save_tar_gz
from utils.logging import log_download_tar_gz_failed, log_download_xml_failed


def get_links(url: str) -> list[str]:
    """
    Get all links from a given url

    :param url: url to get links from
    :return: list of links
    """
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    links = []
    for link in soup.find_all("a"):
        links.append(link.get("href"))
    return links


def fetch_tar_gz(url: str, file_name: str, pwd: str) -> None:
    """
    Fetch a tar.gz file from a given url

    :param url: url to fetch file from
    :param file_name: name of the file to be saved
    :param pwd: save directory path
    :return: None
    """
    res = requests.get(url + "/" + file_name, stream=True)
    if res.status_code == 200:
        save_tar_gz(res, file_name, pwd)
    else:
        print("Error: " + str(res.status_code) + " " + res.reason)
        log_download_tar_gz_failed(file_name)


def fetch_xml_article_by_pmcid(id: str, save_dir: str) -> None:
    """
    downloads a full text article by pmcid and saves it to a directory in xml format

    :param id: pmcid
    :param save_dir: path to directory to save the article
    """
    # https://www.ebi.ac.uk/europepmc/webservices/rest/PMC3650725/fullTextXML
    with requests.get(
        url=f"https://www.ebi.ac.uk/europepmc/webservices/rest/{id}/fullTextXML"
    ) as r:
        if r.text != "":
            save_file(r, f"{id}.xml", save_dir)
        else:
            log_download_xml_failed(id)


def fetch_file(url: str, file_name: str, pwd: str) -> None:
    """
    Fetch a file from a given url

    :param url: url to fetch file from
    :param file_name: name of the file to be saved
    :param pwd: save directory path
    :return: None
    """
    res = requests.get(url)
    save_file(res, file_name, pwd)


def get_filtered_links(url: str, ends_with: str) -> filter:
    """
    Get all links from a given url that ends with a given string

    :param url: url to get links from
    :param ends_with: string to filter links
    :return: an iterable object containing links
    """
    return filter(partial(lambda x, y: x.endswith(y), y=ends_with), get_links(url))


def only_incr_links(url: str, ends_with: str) -> filter:
    """
    Get all links from a given url that ends with a given string and contains ".incr."

    :param url: url to get links from
    :param ends_with: string to filter links
    :return: an iterable object containing links
    """
    return filter(
        partial(lambda x, y: y in x, y=".incr."), get_filtered_links(url, ends_with)
    )


def only_baseline_links(url: str, ends_with: str) -> filter:
    """
    Get all links from a given url that ends with a given string and contains ".baseline."

    :param url: url to get links from
    :param ends_with: string to filter links
    :return: an iterable object containing links
    """
    return filter(
        partial(lambda x, y: y in x, y=".baseline."), get_filtered_links(url, ends_with)
    )


def main():
    BASE_URL = "https://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_bulk/"
    OA_OTHER_URL = BASE_URL + "oa_other/txt/"
    y = only_incr_links(OA_OTHER_URL, ".tar.gz")

    my_tar_gz = list(y)[:3]


if __name__ == "__main__":
    # main()
    pass
