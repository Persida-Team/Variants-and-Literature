from dataclasses import dataclass

from .test_interface import Test


@dataclass
class DOCTest(Test):
    extension: str = "doc"


@dataclass
class DOCXTest(Test):
    extension: str = "docx"


def main():
    x = DOCTest("main", to_save=True)
    # y = DOCXTest("main", to_save=True)

    print("Running on all documents")
    """
    preskocio:
        "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2805773/bin/NIHMS155597-supplement-01.doc",
    """

    inputs = [
        # "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3742455/bin/pone.0071958.s001.doc",
        "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2034480/bin/nar_gkm588_nar-01373-c-2007-File003.doc"
    ]
    x.run_test(inputs)
    # with open("/mnt/d/Storage/WORK/P/Clingen/PubMedCentral/50k_articles/supplementary_results/not_parsed_doc.txt", "r") as f:
    #     not_parsed = f.readlines()
    #     not_parsed = [x.strip() for x in not_parsed]
    #     x.run_test(not_parsed)
    # with open("/mnt/d/Storage/WORK/P/Clingen/PubMedCentral/50k_articles/supplementary_results/not_parsed_docx.txt", "r") as f:
    #     not_parsed = f.readlines()
    #     not_parsed = [x.strip() for x in not_parsed]
    #     y.run_test(not_parsed)

    # x.run_on_all_documents(
    #     start_from="https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2953480/bin/pntd.0000849.s002.doc"
    #     # start_from="https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2553267/bin/pone.0003283.s011.doc"
    # )
    # y.run_on_all_documents()
    print("Done")
    inputs = [
        "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3397219/bin/10549_2012_1965_MOESM1_ESM.doc",  # not a Word File error
        # "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3527477/bin/pone.0051882.s001.docx",
        "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC551616/bin/1471-2156-6-9-S2.doc",  # not a zip file error
    ]
    # x.run_test(["https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2991352/bin/pone.0014116.s003.doc"])
    # result = x.run_test(inputs)
    # print(result)
    # ""
    # x.run_on_all_documents(start_from="https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3536563/bin/1471-2164-13-320-S3.doc")
    # x.run_on_all_documents(start_from="https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3534505/bin/12879_2012_2133_MOESM1_ESM.doc")

    # y.run_on_all_documents(
    #     start_from="https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3531317/bin/pcbi.1002817.s001.docx"
    # )
    ...


if __name__ == "__main__":
    main()
