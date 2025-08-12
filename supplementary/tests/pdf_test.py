from dataclasses import dataclass, field

from test_interface import Test


@dataclass
class PDFTest(Test):
    extension: str = "pdf"


def main():
    x = PDFTest("main", to_save=True)
    # x.run_on_subsample(1000)
    x.run_on_all_documents()
    # x = PDFTest("main")
    # x.catch_errors_only()

    inputs = [
        # "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC529269/bin/1472-6750-4-24-S1.pdf",
        "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC544879/bin/1471-2164-5-92-S1.pdf",
    ]
    # result = x.run_test(inputs)
    # print(result)
    ...


if __name__ == "__main__":
    main()
