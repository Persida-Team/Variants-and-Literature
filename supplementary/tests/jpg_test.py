from dataclasses import dataclass

from test_interface import Test


@dataclass
class JPGTest(Test):
    extension: str = "jpg"


def main():
    x = JPGTest("main", to_save=True)
    # x.catch_errors_only()
    # inputs = [
    #     "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3403905/bin/1471-2164-13-147-S7.png",
    # ]
    x.run_on_all_documents()
    ...


if __name__ == "__main__":
    main()
