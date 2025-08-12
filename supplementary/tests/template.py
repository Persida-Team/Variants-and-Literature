from dataclasses import dataclass

from test_interface import Test


@dataclass
class TEMPLATETest(Test):
    extension: str = "some_extension"  # lower-case


def main():
    """
    instantiate the test class with a name and whether or not to
    save the results (select readers with save=True or save=False)
    """
    my_test_class = TEMPLATETest(name="some test name", to_save=True)

    # below are ways to run the test

    """
        Have a list of URLs, or local paths, or both
        and run the test on all of them
    """
    inputs = ["url_1", "url_2", ...]
    my_test_class.run_test(inputs)

    """
        run the test on all documents of extension from the
        supplementary_format.json that corresponds to the test's extension
    """
    my_test_class.run_on_all_documents()

    """
        run the test on a subsample of n documents from the 
        supplementary_format.json that corresponds to the test's extension    
    """
    my_test_class.run_on_subsample(n=2)

    """
        run the test on all documents of extension from the
        supplementary_format.json that corresponds to the test's extension
        and print out the errors that occur with the documents URL or path
    """
    my_test_class.catch_errors_only()


if __name__ == "__main__":
    main()
