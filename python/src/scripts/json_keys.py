#!/usr/bin/env python3
"Obtain information about the keys of a JSON file containing a list of objects."

import argparse
import json
from collections import defaultdict
from typing import Any, TypedDict


class JSONKeyInfo(TypedDict):
    count: int
    type: set[str]
    nullable: bool


def analyze_json_file(data: list[dict[str, Any]]) -> dict[str, JSONKeyInfo]:
    field_info: dict[str, JSONKeyInfo] = defaultdict(
        lambda: {"count": 0, "type": set(), "nullable": False}
    )

    for obj in data:
        for key in field_info:
            if key not in obj or obj[key] is None:
                field_info[key]["nullable"] = True

        for key, value in obj.items():
            if value is not None:
                field_info[key]["count"] += 1
                field_info[key]["type"].add(type(value).__name__)

    return field_info


def print_table(title: str, headers: list[str], values: list[list[Any]]) -> str:
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

    return "\n".join([title, header_line, separator_line, *rows])


def render_data(
    info: dict[str, JSONKeyInfo], num_objects: int, add_count: bool
) -> list[list[str]]:
    result: list[list[str]] = []
    for k, v in info.items():
        row = [
            k,
            ", ".join(sorted(v["type"])),
            "✓" if v["nullable"] else "✗",
        ]
        if add_count:
            row.append(f"{v['count']} ({v['count'] / num_objects:.0%})")
        result.append(row)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "files", type=argparse.FileType("r"), nargs="+", help="Paths to the JSON files."
    )
    parser.add_argument(
        "--count",
        "-c",
        action="store_true",
        help="Add the count of objects with the key.",
    )
    args = parser.parse_args()

    for file in args.files:
        data = json.load(file)
        info = analyze_json_file(data)
        table = render_data(info, len(data), args.count)

        headers = ["Name", "Type", "Nullable"]
        if args.count:
            headers.append("Count (% of total)")
        print(print_table(file.name, headers, table))
        print(f"\nTotal objects: {len(data)}\n")


if __name__ == "__main__":
    main()
