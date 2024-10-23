#!/usr/bin/env python3
"""Find classes that are not dataclasses, NamedTuples, Enums, or TypedDicts."""

# pyright: basic
import argparse
import ast
import subprocess
import sys
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Class:
    filename: Path
    lineno: int
    name: str


@dataclass
class ClassFinder(ast.NodeVisitor):
    filename: Path
    classes: list[Class] = field(default_factory=list)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:  # noqa: N802
        if is_non_traditional_class(node):
            return

        self.classes.append(Class(self.filename, node.lineno, node.name))


def do_exprs_match(exprs: list[ast.expr], base_cls: str) -> bool:
    return any(
        (isinstance(base, ast.Name) and base.id == base_cls)
        or (isinstance(base, ast.Attribute) and base.attr == base_cls)
        for base in exprs
    )


def is_non_traditional_class(node: ast.ClassDef) -> bool:
    is_dataclass = do_exprs_match(node.decorator_list, "dataclass")
    is_other_class = any(
        do_exprs_match(node.bases, base) for base in ["NamedTuple", "Enum", "TypedDict"]
    )

    return is_dataclass or is_other_class


def find_classes_in_file(filename: Path) -> list[Class]:
    node = ast.parse(filename.read_text(), filename=filename)
    class_finder = ClassFinder(filename)
    class_finder.visit(node)
    return class_finder.classes


def find_python_files(directory: Path) -> Iterable[Path]:
    try:
        git_files = subprocess.check_output(
            ["git", "-C", directory, "ls-files", "*.py"], text=True
        )
    except subprocess.CalledProcessError:
        print("Error: Make sure you are in a Git repository")
        sys.exit(1)

    for file in git_files.splitlines():
        full_path = directory / file
        if full_path.is_file():
            yield full_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("dirs", type=Path, nargs="+", help="Directory to search")
    args = parser.parse_args()

    dirs: list[Path] = args.dirs
    classes = [
        class_
        for dir in dirs
        for file in find_python_files(dir)
        for class_ in find_classes_in_file(file)
    ]

    for class_ in classes:
        print(f"{class_.filename}:{class_.lineno}\t{class_.name}")


if __name__ == "__main__":
    main()
