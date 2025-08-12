import json
from collections import defaultdict

import requests


def look_for_data_header(link: str):
    # Send a HEAD request to get metadata
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    response = requests.head(link, headers=headers)
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Access metadata headers
        content_length = response.headers.get("Content-Length")
        content_type = response.headers.get("Content-Type")
        # header = response.headers
        # Print the metadata
        # print(f"Content-Length: {content_length} bytes")
        # print(f"Content-Type: {content_type}")
        # print(f"Header: {header}")
        return content_length, content_type
    else:
        print(
            "Failed to retrieve metadata. Status code:",
            response.status_code,
            " -> ",
            link,
        )
        return "", 0


def main():
    with open("supplementary_format.json", "r") as f:
        data = json.load(f)
    result = []
    for i in data["RAR"]:
        print(i)
        if n_bytes := look_for_data_header(i):
            result.append(int(n_bytes))

    result = sorted(result)
    print(result)


def results():
    # results are in bytes
    zip_max_size = 40_755_262
    tgz_max_size = 73_194_012
    gz_max_size = 13_382_792
    rar_max_size = 9_597_960


def get_all_content_types():
    with open("supplementary_format.json", "r") as f:
        data = json.load(f)
    progress = 0
    total_progress = 0
    for extension, links in data.items():
        if extension == "TIFF":
            continue
        total_progress += len(links)
    result = defaultdict(list)
    for extension, links in data.items():
        if extension == "TIFF":
            continue
        for link in links:
            print(f"{progress}/{total_progress}", end="\r")
            n_bytes, content_type = look_for_data_header(link)
            result[content_type].append(n_bytes)
            progress += 1
            if progress % 100 == 0:
                with open("content_type_sizes.json", "w") as f:
                    json.dump(result, f, indent=4)

    with open("content_type_sizes.json", "w") as f:
        json.dump(result, f, indent=4)

    print("done")


if __name__ == "__main__":
    # main()
    ...
    # link = (
    #     "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3692482/bin/pone.0067899.s001.rar"
    # )
    # look_for_data_header(link=link)
    get_all_content_types()
