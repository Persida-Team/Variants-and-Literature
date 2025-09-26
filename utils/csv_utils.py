import pandas as pd
from functools import reduce
from itertools import repeat
import time
from utils.download_utils import fetch_file, only_baseline_links, only_incr_links
from utils.filesystem_utils import create_dir, remove_dir, save_csv
from utils.logging import log_pmcid_not_in_csv, log_pmid_not_in_csv


def format_csv(url: str, link: str, pwd: str = "tmp") -> pd.DataFrame:
    """
    Format a csv file from a given url and add a column with the link name.
    This function calls fetch_file to download the csv file and save in the current directory.

    :param url: url to get csv file from
    :param link: link name
    :return: a pandas DataFrame
    """
    fetch_file(url + link, link, pwd=pwd)
    df = pd.read_csv(pwd + "/" + link, sep=",")
    df["from_link"] = link.removesuffix(".filelist.csv") + ".tar.gz"
    return df  # .head(1)


def concat_csv(acc: pd.DataFrame, x: tuple[str, str]) -> pd.DataFrame:
    """
    Concatenate two csv files

    :param acc: an accumulator pandas DataFrame
    :param x: tuple with url and link
    :return: a pandas DataFrame
    """
    return pd.concat([acc, format_csv(x[0], x[1])])


def concat_formatted_csvs(url: str, links: filter) -> pd.DataFrame:
    """
    Concatenate all csv files from a given url and links

    :param url: base url to get csv files from
    :param links: links corresponding to individual files
    :return: a pandas DataFrame
    """
    return reduce(concat_csv, zip(repeat(url), links), pd.DataFrame())


def compute_final_csv(url: str, function: callable) -> pd.DataFrame:
    """
    Concatenate all csv files from a given url and save to a csv file

    :param url: base url to get csv files from
    :param function: function to get links
    :return: a pandas DataFrame
    """
    return concat_formatted_csvs(url, function(url, ".filelist.csv"))


def download_csv(oa_dirs: list, output_dir: str, function: callable):
    """
    Download all csv files from a list of urls and save to a csv file

    :param oa_dirs: list of urls
    :param output_dir: directory to save the final csv file
    :param function: function to compute final csv
    """
    create_dir("tmp")
    create_dir(output_dir)

    for url in oa_dirs:
        start = time.time()
        print(f"Processing {url}\n")
        df = compute_final_csv(url, function)
        save_as = url.split("/")[-3] + ".csv"
        save_csv(df, output_dir + "/" + save_as)
        # save_csv(df, save_as)
        print(f"Done!\nSaved {save_as} in {time.time() - start} seconds\n")

    remove_dir("tmp")
    # remove_files(".", is_non_essential)


def download_incr_csv(oa_dirs: list):
    """
    Download incremental csv files from a list of urls and save to a designated directory

    :param oa_dirs: list of urls
    """
    download_csv(
        oa_dirs=oa_dirs,
        output_dir="incremental_csv",
        function=only_incr_links,
    )


def download_baseline_csv(oa_dirs: list):
    """
    Download baseline csv files from a list of urls and save to a designated directory

    :param oa_dirs: list of urls
    """
    download_csv(
        oa_dirs=oa_dirs,
        output_dir="baseline_csv",
        function=only_baseline_links,
    )


def search_for_article_by_pmid(df: pd.DataFrame, pmid: str) -> dict:
    """
    Search for a given pmid in a pandas DataFrame

    :param df: a pandas DataFrame
    :param pmid: pmid to search for
    :return: a tuple with the pmid, pmcid and the location of the article
    """
    # TODO - check if pmid is in df and handle exception
    match = df[df["PMID"] == int(pmid)]
    if match.empty:
        log_pmid_not_in_csv(pmid)
        return None
    try:
        return {
            "pmid": pmid,
            "pmcid": match["AccessionID"].values[0],
            "location": match["from_link"].values[0],
            "file": match["Article File"].values[0],
        }
    except IndexError as e:  # TODO - check if this is needed, cuz match.empty should handle it
        print(f"Could not find {pmid} in {df}")
        # raise e
        return None


def search_for_article_by_pmcid(df: pd.DataFrame, pmcid: str) -> dict:
    """
    Search for a given pmcid in a pandas DataFrame

    :param df: a pandas DataFrame
    :param pmcid: pmcid to search for
    :return: a tuple with the pmid, pmcid and the location of the article
    """
    # TODO - check if pmcid is in df and handle exception
    match = df[df["AccessionID"] == pmcid]
    # if match is empty, log it and return empty dict
    if match.empty:
        # log_pmcid_not_in_csv(pmcid)
        return None
    try:
        return {
            "pmid": match["PMID"].values[0],
            "pmcid": pmcid,
            "location": match["from_link"].values[0],
            "file": match["Article File"].values[0],
        }
    except IndexError as e:  # TODO - check if this is needed, cuz match.empty should handle it
        print(f"Could not find {pmcid} in {df}")
        # raise e
        return None


def search_for_articles_by_pmid(df: pd.DataFrame, pmids: list[str]) -> list:
    """
    Search for a list of pmids in a pandas DataFrame

    :param df: a pandas DataFrame
    :param pmids: list of pmids to search for
    :return: a list of tuples with the pmid, pmcid and the location of the article
    """
    return search_for_articles_by(df, pmids, search_for_article_by_pmid)

def search_for_articles_by_pmcid(df: pd.DataFrame, pmcids: list[str]) -> list:
    """
    Search for a list of pmcids in a pandas DataFrame

    :param df: a pandas DataFrame
    :param pmcids: list of pmcids to search for
    :return: a list of tuples with the pmid, pmcid and the location of the article
    """
    return search_for_articles_by(df, pmcids, search_for_article_by_pmcid)

    
def search_for_articles_by(df: pd.DataFrame, pmids: list[str], by_function: callable) -> filter: # pmids can be an iter
    return filter(lambda x: x is not None, map(lambda pmid: by_function(df, pmid), pmids))




def main():
    pass


if __name__ == "__main__":
    # main()
    pass
