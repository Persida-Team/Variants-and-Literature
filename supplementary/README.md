# SUPPLEMENTARY MATERIAL EXTRACTION

## 1.1. Requirements

- Python 3.11.3 (I use it, maybe something lower can work as well)
- install the requirements.txt file

## 1.2. Understand projects workflow, code, and structure

### 1.2.1 Workflow

A general workflow of this project is divided into two steps:

- fetching the data from the PMC website, transforming, and saving it in a unified format in the **output_examples**.
### 1.2.2 Structure

- **supplementary_format.json** - main input file for the project, contains all the information about the extensions and their corresponding URLs
- **readers/**
  - **reader_interface.py** - contains the interface for the reader classes
  - **readers.py** - contains the dictionaries of the reader classes
  - **supported_readers/\*** - contains the reader classes for each extension
- **tests/**
  - **test_interface.py** - contains the interface for the test classes
  - **extension_test.py** - contains the test classes for each extension
- **utils/**
  - **data_fetching.py** - contains the code for fetching the data from the website (_can save data to file or just return it_)
  - **result_saver.py** - saves the processed data to a designated directory
- **downloaded_files/\***
  - **extension/\*** - contains all the files downloaded from the website for a specific extension
- **output_formatters/\***
  - **pandas_formatter.py** - contains the code for formatting the data processed by readers that use pandas DataFrames (_tables_), into a unified format
- **output_examples/\*** - contains the processed data (_the result from a reader class_)
- **README.md** - this file

### 1.2.3 Code

**If one would like to add a support for a new extension, one can do the following:**

inside the **readers/supported_readers/** create a python file representing a reader class:

```python
from readers.reader_interface import FormatReader


class TemplateFormatReader(FormatReader):
    def read_bytes(self, byte_contents):
        # implement the logic for reading the bytes gathered via the data_fetching.py
        ...

    def read_from_path(self, path):
        # implement the logic for reading the file from the path
        ...

if __name__ == "__main__":
    ...
```

The reader class inherits the **reader_interface.FormatReader** class, which has one optional boolean argument **save**. If the **save** is set to **True**, the reader will save the processed data _(this still needs to be implemented or called as an existing function. There is a **save** function in **utils/result_saver.py** that can be used)_. If the **save** is set to **False**, the reader will just return the processed data.

Each new reader class should be registered in **readers/readers.py** dictionaries, where the key should be **lower-case extension** of the file and the value should be the reader class. We differentiate between the readers that save the data and the ones that don't. The dictionaries are as follows:

```python
READERS_DICT: dict[str, FormatReader] = {
    "csv": CSVFormatReader(),
    "txt": TXTFormatReader(),
    "xls": EXCELFormatReader(),
    # add the new reader here
}

READERS_DICT_SAVE: dict[str, FormatReader] = {
    "csv": CSVFormatReader(save=True),
    "txt": TXTFormatReader(save=True),
    "xls": EXCELFormatReader(save=True),
    # add the new reader here
}
```

In order to run the first step of this project's workflow, one needs to run a test for a desired reader class. The tests (**tests/extension_test.py**) inherit the **tests/test_interface.Test** class, which implements all necessary functions for running the test. Here is what the test class can look like and what you can do with it:

```python
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
    my_test_class.run_on_subsample(n = 2)

    """
        run the test on all documents of extension from the
        supplementary_format.json that corresponds to the test's extension
        and print out the errors that occur with the documents URL or path
    """
    my_test_class.catch_errors_only()


if __name__ == "__main__":
    main()

```

Please run these tests from the **root** of the project, so the command would be:

```bash
# running template_test.py from the root of the project
python /tests/template_test.py
```
