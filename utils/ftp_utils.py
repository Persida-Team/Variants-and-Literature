import csv
import ftplib
import io
import os
import re
import tarfile
from contextlib import contextmanager


class FtpClient:
    def __init__(self, host):
        self.host = host

    @contextmanager
    def connection(self):
        ftp = ftplib.FTP(self.host)
        ftp.login()
        try:
            yield ftp
        finally:
            ftp.quit()

    def list_ftp_directory(self, path):
        with self.connection() as ftp:
            ftp.cwd(path)
            files = ftp.nlst()
        return files
    
    def list_files_detailed(self, path):
        files = []

        def parse_line(line):
            parts = line.split(maxsplit=8)
            if len(parts) >= 9:
                files.append({
                    "permissions": parts[0],
                    "size": parts[4],
                    "last_modified": f"{parts[5]} {parts[6]} {parts[7]}",
                    "name": parts[8],
                })

        with self.connection() as ftp:
            ftp.cwd(path)
            ftp.retrlines("LIST", parse_line)

        return files

    def filter_files_detailed(self, files, keywords):
        if not keywords:
            return files
        return [
            f for f in files
            if all(re.search(kw, f["name"], re.IGNORECASE) for kw in keywords)
        ]
    
    def filter_files(self, files, keywords, and_or="and"):
        if not keywords:
            return files
        if and_or == "and":
            return [
                f for f in files
                if all(re.search(kw, f, re.IGNORECASE) for kw in keywords)
            ]
        elif and_or == "or":
            return [
                f for f in files
                if any(re.search(kw, f, re.IGNORECASE) for kw in keywords)
            ]
        else:
            raise ValueError("and_or must be 'and' or 'or'")
        
    def download_file(self, remote_path, local_path):
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with self.connection() as ftp, open(local_path, "wb") as out_file:
            print(f"Downloading {remote_path}...")
            ftp.retrbinary(f"RETR {remote_path}", out_file.write)
            print(f"Saved to {local_path}.")

    def extract_tar_gz(self, file_path, extract_to):
        os.makedirs(extract_to, exist_ok=True)
        print(f"Extracting {file_path}...")
        with tarfile.open(file_path, "r:gz") as tar:
            tar.extractall(path=extract_to)
        print(f"Extraction completed at {extract_to}.")

    def download_and_extract(self, remote_path, local_path, extract_to):
        self.download_file(remote_path, local_path)
        self.extract_tar_gz(local_path, extract_to)

    def download_csv(self, path):
        with self.connection() as ftp:
            csv_file = io.StringIO()
            ftp.retrlines(f"RETR {path}", lambda line: csv_file.write(f"{line}\n"))
            csv_file.seek(0)
            return csv.reader(csv_file)




def download_and_extract_pubtator_files():
    base_path = "pub/lu/PubTatorCentral/"
    host = "ftp.ncbi.nih.gov"
    local_path = lambda file_name: os.path.join("./pubtator/input_samples/", file_name)
    
    ftp = FtpClient(host)
    filters = [
        "gene2pubtatorcentral.gz",
        "disease2pubtatorcentral.gz",
        "mutation2pubtatorcentral.gz",
        "species2pubtatorcentral.gz",
    ]

    files = ftp.filter_files(
        ftp.list_ftp_directory(base_path),
        filters,
        and_or="or",
    )
    for file in files:
        print(f"Downloading {file}...")
        ftp.download_file(
            os.path.join(base_path, file),
            local_path(file),
        )

if __name__ =="__main__":
    
    download_and_extract_pubtator_files()