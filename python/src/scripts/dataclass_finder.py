#!/usr/bin/env python3
"Find classes that are not dataclasses or NamedTuples in the directory."
# pyright: basic
import argparse
import ast
import subprocess
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ClassFinder(ast.NodeVisitor):
    filename: Path
    add_filename: bool

    def visit_ClassDef(self, node: ast.ClassDef) -> None:  # noqa: N802
        if is_dataclass_or_namedtuple(node):
            return

        if self.add_filename:
            print(f"{self.filename}\t{node.name}")
        else:
            print(node.name)


def is_dataclass_or_namedtuple(node: ast.ClassDef) -> bool:
    is_dataclass = any(
        (isinstance(decorator, ast.Name) and decorator.id == "dataclass")
        or (isinstance(decorator, ast.Attribute) and decorator.attr == "dataclass")
        for decorator in node.decorator_list
    )

    is_namedtuple = any(
        (isinstance(base, ast.Name) and base.id == "NamedTuple")
        or (isinstance(base, ast.Attribute) and base.attr == "NamedTuple")
        for base in node.bases
    )

    return is_dataclass or is_namedtuple


def find_classes_in_file(filename: Path, add_filename: bool) -> None:
    node = ast.parse(filename.read_text(), filename=filename)
    class_finder = ClassFinder(filename, add_filename)
    class_finder.visit(node)


def find_python_files(directory: Path) -> Iterable[Path]:
    try:
        git_files = subprocess.check_output(
            ["git", "-C", directory, "ls-files", "*.py"], text=True
        )
        for file in git_files.splitlines():
            full_path = directory / file
            if full_path.is_file():
                yield full_path
    except subprocess.CalledProcessError:
        print("Error: Make sure you are in a Git repository")
        sys.exit(1)


def find_non_dataclasses(directory: Path, add_filename: bool) -> None:
    for file in find_python_files(directory):
        find_classes_in_file(file, add_filename)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "dir",
        type=Path,
        default=Path("."),
        nargs="?",
        help="Directory to search (default: current directory)",
    )
    parser.add_argument(
        "--add-filename", action="store_true", help="Add filename to the output"
    )

    args = parser.parse_args()
    find_non_dataclasses(args.dir, args.add_filename)


if __name__ == "__main__":
    main()
