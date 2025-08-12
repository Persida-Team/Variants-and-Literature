from dataclasses import dataclass

from test_interface import Test


@dataclass
class PNGTest(Test):
    extension: str = "png"


def main():
    # x = PNGTest("main")
    x = PNGTest("main", to_save=True)
    # x.catch_errors_only()
    # x.run_test(inputs)
    x.run_on_all_documents()
    ...


if __name__ == "__main__":
    main()
