#!/usr/bin/env python3
"Convert JSON to Markdown table."

import argparse
import json
from typing import Any

from beartype.door import is_bearable


def generate_table(headers: list[str], values: list[list[Any]]) -> str:
    """Generate table from headers and values.

    Args:
        headers: List of strings representing the headers of the table.
        values:
            List of lists of values to be displayed in the table. They will be converted
            to strings before being displayed. Custom formatting must be done before.

    Returns:
        A string representing the table in Markdown format.
    """
    # Calculate the maximum length for each column, considering both headers and the
    # data in values
    max_lengths = [
        max(len(str(row[i])) if i < len(row) else 0 for row in [headers, *values])
        for i in range(len(headers))
    ]

    fmt_parts = [f"{{{i}:<{len}}}" for i, len in enumerate(max_lengths)]
    fmt_string = " | ".join(fmt_parts)

    def format_row(row: list[Any]) -> str:
        return fmt_string.format(*(map(str, row)))

    header_line = format_row(headers)
    separator_line = " | ".join("-" * length for length in max_lengths)
    rows = [format_row(row) for row in values]

    return "\n".join([header_line, separator_line, *rows])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "file",
        type=argparse.FileType(),
        default="-",
        nargs="?",
        help=(
            "The file containing the JSON data to convert to a table. If not provided,"
            " read from stdin."
        ),
    )
    parser.add_argument(
        "--fmt",
        action="append",
        nargs="+",
        metavar=("FORMAT", "COLUMN"),
        help=(
            "Specify the format for one or more columns. Example: --fmt '{:d}' age"
            " --fmt '{:>10}' name email"
        ),
    )
    args = parser.parse_args()

    data = json.load(args.file)
    if not is_bearable(data, list[dict[str, Any]]):
        raise ValueError("The JSON data must be a list of dictionaries.")

    headers = list(data[0].keys())

    fmt_: list[str] = args.fmt
    formats: dict[str, str] = {}
    for fmt_option in fmt_ or []:
        fmt, columns = fmt_option[0], fmt_option[1:]
        for column in columns:
            formats[column] = fmt

    values = [
        [
            formats.get(col, "{}").format(row[col]) if col in row else ""
            for col in headers
        ]
        for row in data
    ]

    print(generate_table(headers, values))


if __name__ == "__main__":
    main()
