from dataclasses import dataclass, field

from .test_interface import Test


@dataclass
class ZIPTest(Test):
    extension: str = "zip"


def main():
    x = ZIPTest("main", to_save=True)
    # x = ZIPTest("main")
    # x.catch_errors_only()
    inputs = [
        "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3415393/bin/pone.0041815.s001.zip",
    ]
    # x.run_test(inputs)

    # x.run_on_all_documents()
    start_from = (
        "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3827063/bin/pone.0078496.s001.zip"
    )
    x.run_on_all_documents(start_from=start_from)

    # x.run_on_subsample(2)
    ...


if __name__ == "__main__":
    main()
