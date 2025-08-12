from dataclasses import dataclass, field

from .test_interface import Test


@dataclass
class CSVTest(Test):
    extension: str = "csv"


def main():
    """
    https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3789830/bin/pgen.1003853.s013.csv
    Error tokenizing data. C error: Buffer overflow caught - possible malformed input file.

    https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3937106/bin/1471-2164-15-64-S1.csv
    Error tokenizing data. C error: Expected 1 fields in line 3, saw 6
    """
    x = CSVTest("main", to_save=True)
    # x.catch_errors_only()
    inputs = [
        # "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3531492/bin/pgen.1003150.s001.csv",
        # "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3937106/bin/1471-2164-15-64-S1.csv",
        "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3789830/bin/pgen.1003853.s013.csv",
    ]
    # print(inputs)
    # x.run_test(inputs)

    x.run_on_all_documents()

    # x.run_on_subsample(2)
    ...


if __name__ == "__main__":
    main()
