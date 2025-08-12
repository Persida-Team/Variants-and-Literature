from dataclasses import dataclass, field

from test_interface import Test


@dataclass
class TXTTest(Test):
    extension: str = "txt"


def main():
    x = TXTTest("main", to_save=True)
    # x = TXTTest("main")
    # x.catch_errors_only()
    inputs = [
        "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4072933/bin/gb-2014-15-5-r73-S1.txt",
    ]
    # x.run_test(inputs)

    x.run_on_all_documents()

    # x.run_on_subsample(2)
    ...


if __name__ == "__main__":
    main()
