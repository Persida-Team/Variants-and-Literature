import itertools
import os
import re
import requests
from bs4 import BeautifulSoup


def clean_text(text: str):
    return re.sub(r"\s+", " ", text)


def extract_text_from(table_wrap, what: str):
    temp = table_wrap.find(what)
    if temp is None:
        return ""
    return clean_text(temp.text)


def extract_label(table_wrap):
    return extract_text_from(table_wrap, "label")


def extract_caption(table_wrap):
    return extract_text_from(table_wrap, "caption")


def extract_table_wrap_foot(table_wrap):
    return extract_text_from(table_wrap, "table-wrap-foot")


def combine_table_header_and_body(table_header, table_body):
    if table_body is None:
        return []
    if table_header is None:
        table = [
            {"Column " + str(i): val for i, val in enumerate(row, 1)}
            for row in table_body
        ]
    else:
        table = [
            {col: val for col, val in zip(table_header, row)} for row in table_body
        ]
    return table


def extract_table(table_wrap, pmcid, label):
    table = table_wrap.find("table")
    table_header = extract_table_header(table, pmcid, label)
    table_body = extract_table_body(table, pmcid, label)
    new_table = combine_table_header_and_body(table_header, table_body)
    return new_table


def do_from_xml_element(element):
    tables = []
    result = {}
    table_wraps = element.find_all("table-wrap")
    for table_wrap in table_wraps:
        label = extract_label(table_wrap)
        result["label"] = label
        result["caption"] = extract_caption(table_wrap)
        result["table_wrap_foot"] = extract_table_wrap_foot(table_wrap)
        table = extract_table(table_wrap, pmcid, label)
        result["contents"] = table
        tables.append(result)


def extract_table_wraps(soup, pmcid):
    results = []
    table_wraps = soup.find_all("table-wrap")
    for table_wrap in table_wraps:
        result = {}
        label = extract_label(table_wrap)
        result["label"] = label
        result["caption"] = extract_caption(table_wrap)
        result["table_wrap_foot"] = extract_table_wrap_foot(table_wrap)
        table = extract_table(table_wrap, pmcid, label)
        result["contents"] = table
        results.append(result)
    return results

    # save the table to a json file
    # with open(f"{save_dir}/{label}.json", "w", encoding="utf8") as f:
    #     json.dump(result, f, indent=4, ensure_ascii=False)
    # # save as a dataframe tsv

    # df = pd.DataFrame(table)
    # df.to_csv(f"{save_dir}/{label}.tsv", sep="\t", index=False)


def download_article_and_extract_tables(
    pmcid: str, parent_dir: str = "./outputs/"
) -> None:
    # make a directory for the article
    SAVE_DIR = parent_dir + pmcid

    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)
    # download the article
    get_xml_article_by_pmcid(pmcid, save_dir=SAVE_DIR)
    if not os.path.exists(f"{SAVE_DIR}/{pmcid}.xml"):
        return
    extract_data(f"{SAVE_DIR}/{pmcid}.xml", SAVE_DIR, pmcid)


def extract_data(xml_file, pmcid):
    with open(xml_file, "r") as f:
        xml = f.read()
    soup = BeautifulSoup(xml, "xml")
    return extract_table_wraps(soup, pmcid)


def get_xml_article_by_pmcid(id: str, save_dir: str = "new_demo") -> None:
    """
    downloads a full text article by pmcid and saves it to a directory in xml format

    :param id: pmcid
    :param save_dir: path to directory to save the article
    """
    # https://www.ebi.ac.uk/europepmc/webservices/rest/PMC3046256/fullTextXML
    # https://www.ebi.ac.uk/europepmc/webservices/rest/PMC3046256/bookXML
    # https://www.ebi.ac.uk/europepmc/webservices/rest/PMC3046256/supplementaryFiles
    with requests.get(
        url=f"https://www.ebi.ac.uk/europepmc/webservices/rest/{id}/fullTextXML"
    ) as r:
        print(r.url)
        text = r.text
        if text != "":
            with open(f"{save_dir}/{id}.xml", "w") as f:
                f.write(text)


def handle_non_numerical_span_value(span_value):
    try:
        return int(span_value)
    except ValueError:
        return 1


def extract_column_number(rows) -> int:
    # find the number of columns from the first row
    row_0 = rows[0].find_all(["td", "th"])
    n_columns = 0
    for i, field in enumerate(row_0):
        n_columns += handle_non_numerical_span_value(field.get("colspan", 1))
    return n_columns


def transform_to_tuples(rows):
    values = []
    for row in rows:
        fields = row.find_all(["td", "th"])
        for field in fields:
            values.append(
                (
                    handle_non_numerical_span_value(field.get("rowspan", 1)),
                    handle_non_numerical_span_value(field.get("colspan", 1)),
                    clean_text(field.text.strip()),
                )
            )
    return values


def remove_consecutive_duplicates(lst):
    return [key for key, _ in itertools.groupby(lst)]


def extract_table_header(table, pmcid, label):
    matrix = parse_table_contents(table, "thead", pmcid, label)
    if matrix is None:
        return None
    merged_header_columns = []
    for column_field in zip(*matrix):
        texts = " ".join(remove_consecutive_duplicates(column_field))
        merged_header_columns.append(texts)
    return merged_header_columns


def parse_table_contents(table, find_what, pmcid, label):
    if table is None:
        return None
    contents = table.find(find_what)
    if contents is None:
        return None
    rows = contents.find_all("tr")
    n_rows = len(rows)
    n_columns = extract_column_number(rows)
    values = transform_to_tuples(rows)
    matrix = fill_matrix(n_rows, n_columns, values, pmcid, label)
    return matrix


def extract_table_body(table, pmcid, label):
    return parse_table_contents(table, "tbody", pmcid, label)


def fill_matrix(n, m, values, pmcid, label):
    NO_TEXT = "NO_TEXT"
    matrix = [[NO_TEXT] * m for _ in range(n)]
    current_row = 0
    current_col = 0
    for row, col, text in values:
        for i in range(row):
            for j in range(col):
                try:
                    while matrix[current_row + i][current_col + j] != NO_TEXT:
                        current_col += 1
                        if current_col >= m:
                            current_col = 0
                            current_row += 1
                    matrix[current_row + i][current_col + j] = text
                except IndexError:
                    # with open("./outputs/0_5000_articles/failed_by_pmcids_second_pass.txt", "a") as f:
                    #     f.write(f"{pmcid} {label}\n")
                    # print("IndexError -> ", pmcid)
                    # for err_row in matrix:
                    #     print(err_row)
                    # save to tsv file
                    # df = pd.DataFrame(matrix)
                    # df.to_csv(f"./outputs/test_by_pmcid/{pmcid}/{label}_breakpoint.tsv", sep="\t", index=False)

                    # LOGGER.exception(
                    #     f"For {pmcid} in {label} -> IndexError: {current_row + i}, {current_col + j} for {text}"
                    # )
                    # log that parsing failed
                    # print("IndexError")
                    return []
        current_col += col
        if current_col >= m:
            current_col = 0
            current_row += 1
    return matrix


def main():
    LOGGER.info("Started parsing\n\n")
    LIST_OF_PMICDS = [
        # "PMC4168390",
        # "PMC7866430",
        # "PMC6874453",
        # "PMC7603384",
        # "PMC7174602",
        # "PMC5837971",  # (rad moje mentorke sa mastera hehe)
        # "PMC9125070",  # (rad iz moje laboratorije :) )
        "PMC7158706",  # ne postoji
        # "PMC7897836",
        # "PMC10090369",
        # "PMC6592405",
        # "PMC6862154",
        # "PMC7726323",
        # "PMC9152158",
        # "PMC8953304",
        # "PMC8386437",
        # "PMC9928731",
        # "PMC6136796",
        # "PMC9952758",
        # "PMC6095993",
        # "PMC8538763",
        # "PMC5352069",
        # "PMC9971686",
        # "PMC9407083",
        # "PMC9778022",
    ]
    for pmcid in LIST_OF_PMICDS:
        download_article_and_extract_tables(pmcid)


def test_test2_xml():
    XML_FILE = "outputs/test2/table.xml"
    extract_data(XML_FILE, "outputs/test2", "PMC3575328")


def test_by_pmcid(pmcid: str):
    # make a directory for the article
    SAVE_DIR = "./outputs/test_by_pmcid/"
    download_article_and_extract_tables(pmcid, parent_dir=SAVE_DIR)


def do_0_5000_articles_but_only_ones_that_failed():
    FAILED = "outputs/0_5000_articles/failed_by_pmcids.txt"
    with open(FAILED, "r") as f:
        pmcids = f.readlines()
    for pmcid in pmcids:
        pmcid = pmcid.strip().split(" ")[0]
        print(pmcid)
        download_article_and_extract_tables(
            pmcid, parent_dir="./outputs/0_5000_articles/TABLE_RESULTS/"
        )


def do_0_5000_articles():
    START_FROM = "3438446"
    PMCIDS_PATH = "./outputs/0_5000_articles/pmcids.txt"
    with open(PMCIDS_PATH, "r") as f:
        pmcids = f.readlines()
    did_pass_start = False
    for pmcid in pmcids:
        pmcid = pmcid.strip()
        # print("#", pmcid.strip(), "#")

        if pmcid != f"{START_FROM}" and not did_pass_start:
            # print("skipping", pmcid)
            continue
        else:
            did_pass_start = True
        download_article_and_extract_tables(
            "PMC" + pmcid, parent_dir="./outputs/0_5000_articles/TABLE_RESULTS/"
        )


def count_failed_pmcids():
    # read log file and extract how many PMCIDS failed to parse
    counter = 0
    with open(FILE_HANDLER_PATH, "r") as f:
        lines = f.readlines()
    failed_pmcids = []
    for line in lines:
        if "IndexError" in line:
            # extract PMC_id from line
            try:
                pmcid_with_table = "PMC" + line.split("PMC")[1].split("->")[0]
                failed_pmcids.append(pmcid_with_table)
                counter += 1
            except IndexError:
                # the line doesn't contain some of the expected info
                continue
    return counter // 2, list(set(failed_pmcids))


def count_parsed_tables():
    # calculate how many tables have parsed
    from functools import reduce

    RESULT_DIR = "./outputs/0_5000_articles/TABLE_RESULTS/"
    counter = 0
    for _, _, filenames in os.walk(RESULT_DIR):
        counter += reduce(
            lambda acc, x: acc + 1,
            filter(lambda filename: filename.endswith(".json"), filenames),
            0,
        )
    return counter


if __name__ == "__main__":
    FILE_HANDLER_PATH = (
        "outputs/0_5000_articles/failed_to_parse.log"  # for 0_5000_articles
    )
    # FILE_HANDLER_PATH = "outputs/failed_to_parse.log" # for general outputs
    LOGGER = logging.getLogger(__name__)
    LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"
    logging.basicConfig(
        filename=FILE_HANDLER_PATH, level=logging.INFO, format=LOG_FORMAT
    )
    FILE_HANDLER = logging.FileHandler(FILE_HANDLER_PATH)
    LOGGER.addHandler(FILE_HANDLER)
    test_test2_xml()

    # test_by_pmcid("PMC3404944")

    # do_0_5000_articles_but_only_ones_that_failed()

    with open("outputs/0_5000_articles/failed_by_pmcids_second_pass.txt", "r") as f:
        lines = map(lambda x: x.strip(), f.readlines())
        s = sorted(list(set(lines)))
        pmcids = list(set(list(map(lambda x: x.split(" ")[0], s))))

        # print(len(s))
        # with open("outputs/0_5000_articles/failed_by_pmcids_second_pass_unique.txt", "w") as f:
        #     f.write("\n".join(s))
    for pmcid in pmcids:
        test_by_pmcid(pmcid)

    # do_0_5000_articles()
    # counter, failed_pmcids = count_failed_pmcids()
    # LOGGER.info(f"Failed to parse {counter} tables from {len(failed_pmcids)} articles")
    # save failed pmcids to a file
    # with open("outputs/0_5000_articles/failed_by_pmcids.txt", "w") as f:
    #     f.write("\n".join(failed_pmcids))
    # counter = count_parsed_tables()
    # LOGGER.info(f"Successfully parsed {counter} tables")
    # main()
