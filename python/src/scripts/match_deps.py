"""Compare dependencies between two pyproject.toml files.

Compatible with Hatch, Rye and PDM. Not compatible with Poetry.
"""

import argparse
import os
import re
from dataclasses import dataclass
from typing import BinaryIO

import tomli

from scripts.util import HelpOnErrorArgumentParser


def main() -> None:
    parser = HelpOnErrorArgumentParser(__doc__)
    parser.add_argument(
        "file1",
        type=argparse.FileType("rb"),
        help="Path to first pyproject.toml file.",
    )
    parser.add_argument(
        "file2",
        type=argparse.FileType("rb"),
        help="Path to second pyproject.toml file.",
    )
    args = parser.parse_args()

    packages1 = parse_deps(load_deps(args.file1))
    packages2 = parse_deps(load_deps(args.file2))

    deps = match_deps(packages1, packages2)
    print(render_deps(args.file1.name, args.file2.name, deps))


def load_deps(file: BinaryIO) -> list[str]:
    return tomli.load(file)["project"]["dependencies"]


def parse_deps(deps: list[str]) -> dict[str, str]:
    return dict(split(d) for d in deps)


def split(line: str) -> tuple[str, str]:
    name, *versions = re.split(r"(@|,|>|<|=)", line.strip())
    name = name.strip()
    versions = "".join(v for v in versions if v.strip()).strip()
    return name, versions


@dataclass
class Dependency:
    name: str
    version1: str
    version2: str


def match_deps(
    packages1: dict[str, str], packages2: dict[str, str]
) -> list[Dependency]:
    deps = set(packages1) | set(packages2)
    return [
        Dependency(dep, packages1.get(dep, "*"), packages2.get(dep, "*"))
        for dep in sorted(deps)
    ]


def render_deps(file_name1: str, file_name2: str, deps: list[Dependency]) -> str:
    fmt = "{:<25} | {:<20} | {:<20}"
    header = fmt.format(
        "Dependency", os.path.dirname(file_name1), os.path.dirname(file_name2)
    )
    sep = fmt.format("-" * 25, "-" * 20, "-" * 20)
    rows = [
        fmt.format(dep.name, dep.version1[-15:], dep.version2[-15:]) for dep in deps
    ]
    return "\n".join([header, sep, *rows])


if __name__ == "__main__":
    main()
