from dataclasses import dataclass

from test_interface import Test


@dataclass
class XLSTest(Test):
    extension: str = "xls"


@dataclass
class XLSXTest(Test):
    extension: str = "xlsx"


def main():
    x = XLSTest("main", to_save=True)
    y = XLSXTest("main", to_save=True)
    # x.catch_errors_only()
    inputs = [
        # "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC514708/bin/1471-244X-4-21-S1.xls",
        # "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC514708/bin/1471-244X-4-21-S3.xls",
        # "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC514708/bin/1471-244X-4-21-S4.xls",
        # "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3400573/bin/pone.0041261.s002.xls",
        # "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3402391/bin/pone.0041537.s007.xls",
        # "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3402391/bin/pone.0041537.s008.xls",
        # "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3403905/bin/1471-2164-13-147-S2.xlsx",
        # "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3403905/bin/1471-2164-13-147-S4.xlsx",
        # "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3403905/bin/1471-2164-13-147-S5.xlsx",
        # "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3403905/bin/1471-2164-13-147-S6.xlsx",
        # "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3403905/bin/1471-2164-13-147-S11.xlsx",
        "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9005588/bin/NIHMS1740908-supplement-Supplementary_Table_9.xlsx",
    ]

    y.run_test(inputs)

    # x.run_test(inputs)

    # start_xls_from = "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3709075/bin/10552_2013_237_MOESM3_ESM.xls"
    # x.run_on_all_documents(start_from=start_xls_from)
    # y.run_on_all_documents()
    ...


if __name__ == "__main__":
    main()
