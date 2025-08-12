from typing import Hashable

import pandas as pd


def transform_table(df: pd.DataFrame) -> list[dict[Hashable, str]]:
    """
    Transforms a DataFrame object into a format
    that is suitable for further analysis

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame object to be transformed

    Returns
    -------
    list[dict[Hashable, str]]
        List of dictionaries with the transformed data.
        This represents a list of rows, where each row
        is a dictionary with the column name as key and
        the table cell value as value.

    """
    return df.to_dict(orient="records")


if __name__ == "__main__":
    ...
