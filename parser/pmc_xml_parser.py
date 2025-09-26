import json
import os
import re
from typing import List

# import xml.etree.ElementTree as ET
from lxml import etree as ET

"""
    LIMITATIONS:

    1. and 2. limitations fixed by adding " " at the start of 
    each tag, but this complicates elasticsearch later on

    1. 
    If the article text contains multiple xml tags, the text 
    inside the tags will not be separated by a space. For example:
    <abstract>
        <sec>
            <title>Aims</title>
            <p>Although genetic, clinical and demographic...</p>
        </sec>
    </abstract>
    will be parsed as:
    "AimsAlthough genetic, clinical and demographic..."

    2. 
    Table columns are not separated by spaces. For example:
    <tr>
        <td ...>
            <bold>Median weight, kg (range)</bold>
        </td>
        <td ...>
            20 (3.6&#x02013;100.1)
        </td>
    </tr>
    will be parsed as:
    Median weight, kg (range)20 (3.6–100.1)


"""

TABLE_SEPARATOR = " \t "
TEXT_SEPARATOR = ". "


def extract_clean_text(element: ET.Element) -> str:
    """
    extracts the text from an xml element and cleans it from xml tags and other unwanted characters

    :param element: root element of nxml file
    :return: cleaned text
    """
    if element is None:
        return ""
    return re.sub(
        " +",  # replace multiple spaces
        " ",  # with a single space
        ET.tostring(
            element,  # convert element to string
            encoding="unicode",  # do encoding to return a string, not bytestring
            method="text",  # removing all html/xml tags
        ).replace(
            "\n", " "
        ),  # replace newlines with spaces
    )


def parse_article_text(element: ET.Element) -> dict:
    """
    parses the article text from an nxml file

    :param element: root element of nxml file
    :return: dictionary containing the article text
    """
    d = {"text": ""}
    # d['text'] = '\n'.join({extract_clean_text(p) for p in element.find('body').iter('p')})
    # article_text = '\n'.join({extract_clean_text(p) for p in element.find('body')})
    # d['text'] = '\n'.join([extract_clean_text(p) for p in element.find('body').iter('p')])
    d["text"] = TEXT_SEPARATOR.join(
        [extract_clean_text(p) for p in element.findall("body/sec")]
    )
    return d


def parse_article_title(element: ET.Element) -> dict:
    """
    parses the article title from an nxml file

    :param element: root element of nxml file
    :return: dictionary containing the article title
    """
    d = {"title": "", "alternative_title": {}}
    d["title"] = extract_clean_text(
        element.find("front/article-meta/title-group/article-title")
    )
    try:
        d["alternative_title"] = {
            x.attrib["alt-title-type"]: extract_clean_text(x)
            for x in element.findall("front/article-meta/title-group/alt-title")
        }
    except KeyError as e:
        pass
    return d


def parse_article_table(element: ET.Element) -> dict:
    """
    parses the article table from an nxml file

    :param element: root element of nxml file
    :return: dictionary containing the article table
    """
    d = {"tables": ""}
    d["tables"] = TABLE_SEPARATOR.join(
        [extract_clean_text(p) for p in element.findall(".//td")]
    )
    return d


def parse_article_abstract(element: ET.Element) -> dict:
    """
    parses the article abstract from an nxml file

    :param element: root element of nxml file
    :return: dictionary containing the article abstract
    """
    d = {"abstract": "", "alternative_abstract": {}}
    for i, abstract in enumerate(element.findall("front/article-meta/abstract")):
        if i == 0:  # main abstract is first
            d["abstract"] = extract_clean_text(abstract)
        else:  # alternative abstracts are second and onwards
            try:
                d["alternative_abstract"][abstract.attrib["abstract-type"]] = (
                    extract_clean_text(abstract)
                )
            except KeyError:
                pass  # no abstract type, or alternative abstract
    return d


def parse_article_id(element: ET.Element) -> dict:
    """
    parses the article id from an nxml file

    :param element: root element of nxml file
    :return: dictionary containing the article id
    """
    d = {"ids": {}}
    for x in element.findall("front/article-meta/article-id"):
        if key := x.attrib.get("pub-id-type"):
            d["ids"][key] = x.text
    return d


def parse_article_type(element: ET.Element) -> dict:
    return {"type": element.attrib.get("article-type")}


def parse_supplementary_list(element: ET.Element, file_path: str) -> dict:
    supplementary_material = []
    pmc_id = file_path.split("/")[-1].split(".")[0]
    SUPPLEMENTARY_BASE_URL = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc_id}/bin/"
    for x in element.findall(
        "body/sec[@sec-type='supplementary-material']//supplementary-material/media"
    ):
        filename_key = list(
            filter(lambda attrib_keys: "href" in attrib_keys, x.attrib.keys())
        )[0]
        supplementary_material.append(x.attrib.get(filename_key))
    supplementary_material = list(filter(lambda x: x, supplementary_material))
    supplementary_material = list(
        map(lambda x: SUPPLEMENTARY_BASE_URL + x, supplementary_material)
    )

    return {"supplementary_material": supplementary_material}


def parse_article(file: str) -> dict:
    """
    parses an article in nxml format to a dictionary containing the
    article title, abstract, text, ids, and table content

    :param file: path to nxml file
    :return: dictionary containing the article title, abstract, text, ids, and table content
    """
    # root = ET.parse(file).getroot()
    root = ET.parse(file, parser=ET.XMLParser(recover=True)).getroot()
    d = {
        **parse_article_id(root),
        **parse_article_type(root),
        **parse_supplementary_list(root, file),
        **parse_article_title(root),
        **parse_article_abstract(root),
        # **parse_article_table(root),
        # **parse_article_text(root),
    }
    return d


def parse_nxml_to_json(list_of_files: List[str], json_file: str = "test.json") -> None:
    """
    parses a list of nxml files and saves them to a json file

    :param list_of_files: list of nxml files
    :param json_file: path to json file
    """
    if not os.path.isfile(json_file):
        f = open(json_file, "x")
        f.close()
    list_of_parsed_articles = []
    with open(json_file, "r+", encoding="utf8") as file:
        for article_nxml in list_of_files:
            list_of_parsed_articles.append(parse_article(article_nxml))
        file.seek(0)
        json.dump(list_of_parsed_articles, file, indent=4, ensure_ascii=False)


"""
    def get_article_ids(article : ET.Element) -> dict: # article must be ./PubmedArticle
        ids = {}
        for id in article.find('PubmedData/ArticleIdList'):
            key = id.attrib['IdType']
            value = id.text
            ids[key] = value
        return ids

    def get_article_title(article : ET.Element) -> str:
        return article.find('MedlineCitation/Article/ArticleTitle').text

    def get_article_abstract(article : ET.Element) -> str:
        try:
            return article.find('MedlineCitation/Article/Abstract/AbstractText').text
        except AttributeError:
            return ''

    def get_pubmed_id(article : ET.Element) -> str:
        return article.find('MedlineCitation/PMID').text
        
    def get_article(article : ET.Element) -> dict:
        d = {}    
        # d['pmid'] = get_pubmed_id(article)
        d['title'] = get_article_title(article)
        d['ids'] = get_article_ids(article)
        d['abstract'] = get_article_abstract(article)
        return d

    def parse_xml_to_json(xml_file):
        root = ET.parse(xml_file).getroot()    
        d = {get_pubmed_id(item) : get_article(item) for item in root.findall('./PubmedArticle')}
        return d

    def save_json(d, json_file):
        with open(json_file, 'w') as f:
            json.dump(d, f, indent=4)

    test_file = 'test.xml'
    x = parse_xml_to_json(test_file)
    save_json(x, 'test.json')
"""
