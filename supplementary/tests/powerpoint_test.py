from dataclasses import dataclass, field

from test_interface import Test


@dataclass
class PPTXTest(Test):
    extension: str = "pptx"


@dataclass
class PPTTest(Test):
    extension: str = "ppt"


def main():
    # x = PPTXTest("main", to_save=True)
    # x = PPTXTest("main")
    x = PPTTest("main", to_save=True)
    # x.run_on_subsample(1000)
    # x.run_on_all_documents()
    # x = PDFTest("main")
    # x.catch_errors_only()

    inputs = [
        # "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3431328/bin/pgen.1002895.s001.pptx",
        # "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3733595/bin/1471-2350-14-75-S4.pptx",
        "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3876991/bin/pone.0082956.s002.ppt",
    ]

    # x.run_on_all_documents()
    result = x.run_test(inputs)
    print(result)
    ...


if __name__ == "__main__":
    main()
