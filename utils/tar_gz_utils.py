from utils.download_utils import fetch_tar_gz
from utils.filesystem_utils import (
    remove_file,
    tar_ungzip,
    create_dir,
    remove_files,
    open_json,
)
import time


def fetch_tar_gz_and_extract(url: str, file_name: str, pwd: str) -> None:
    """
    Fetch a tar.gz file from a given url and extract it, remove the tar.gz file

    :param url: url to fetch file from
    :param file_name: name of the file
    :param pwd: save directory path
    :return: None
    """
    fetch_tar_gz(url, file_name, pwd)
    tar_ungzip(file_name, pwd)
    remove_file(pwd + "/" + file_name)


def compute_tar_gz(url: str, files: iter, pwd: str) -> None:
    """
    Iterate over files, fetch and extract them, remove the tar.gz file

    :param url: url to fetch files from
    :param files: an iterable of files
    :param pwd: save directory path
    """
    create_dir(pwd)
    start = time.time()
    for file in files:
        start1 = time.time()
        print("Processing ", file)
        if file in [
            "oa_comm_txt.PMC000xxxxxx.baseline.2022-12-17.tar.gz",
            "oa_comm_txt.PMC001xxxxxx.baseline.2022-12-17.tar.gz",
            "oa_comm_txt.PMC002xxxxxx.baseline.2022-12-17.tar.gz",
        ]:
            return
        fetch_tar_gz_and_extract(url, file, pwd)
        print("Done!\nExtracted in ", time.time() - start1, " seconds\n")
    print(f"Done!\nExtracted all files in {time.time() - start} seconds\n")


def compute_tar_gz_and_cleanup(
    url: str, files: iter, pwd: str, locations_file_path: str
):
    locations = open_json(locations_file_path)
    for file in files:
        compute_tar_gz(url=url, files=[file], pwd=pwd)
        key = ".".join(file.split(".")[:-3])
        pmc00_xxxxxx = key.split(".")[1]
        files_to_preserve = [entity["file"].split("/")[1] for entity in locations[key]]
        remove_files(
            path=f"{pwd}/{pmc00_xxxxxx}",
            condition=lambda x: True,
            skip=files_to_preserve,
        )


def main():
    pass


if __name__ == "__main__":
    # main()
    pass
