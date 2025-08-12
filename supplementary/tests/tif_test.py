from dataclasses import dataclass

from test_interface import Test


@dataclass
class TIFTest(Test):
    extension: str = "tif"


def main():
    """
    takes to long to read, doesn't finish reading
    # "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3734060/bin/pone.0070694.s001.tif",


    """
    # x = TIFTest("main")
    x = TIFTest("main", to_save=True)
    # x.catch_errors_only()
    # inputs = [
    #     # "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3734069/bin/pone.0070307.s001.tif",
    #     # "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3879265/bin/pone.0083707.s004.tif",
    #     "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3879265/bin/pone.0083707.s005.tif",
    # ]
    # result = x.run_test(inputs)
    # print(result)
    # return
    start_from = (
        # "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3734069/bin/pone.0070307.s001.tif"
        # "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3789830/bin/pgen.1003853.s003.tif"
        "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3879265/bin/pone.0083707.s005.tif"
    )

    result = x.run_on_all_documents(start_from=start_from)
    # print(result)
    # x.run_on_all_documents()
    ...


if __name__ == "__main__":
    main()
