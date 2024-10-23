#!/usr/bin/env python3
"""Find classes that are not dataclasses, NamedTuples, Enums, TypedDicts, or Pydantic models."""

# pyright: basic
import argparse
import ast
import subprocess
import sys
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Class:
    filename: Path
    lineno: int
    name: str


@dataclass(frozen=True)
class ClassDefinition:
    node: ast.ClassDef
    bases: set[str]


@dataclass(frozen=True)
class ClassFinder(ast.NodeVisitor):
    filename: Path
    classes: list[Class] = field(default_factory=list)
    _class_definitions: dict[str, ClassDefinition] = field(default_factory=dict)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:  # noqa: N802
        # Store the class definition for later inheritance checking
        self._class_definitions[node.name] = ClassDefinition(
            node=node,
            bases=set(self._get_base_names(node.bases)),
        )

        if is_non_traditional_class(node) or self._inherits_from_basemodel(node.name):
            return

        self.classes.append(Class(self.filename, node.lineno, node.name))

    def _get_base_names(self, bases: list[ast.expr]) -> list[str]:
        """Extract base class names from AST expressions."""
        names = []
        for base in bases:
            if isinstance(base, ast.Name):
                names.append(base.id)
            elif isinstance(base, ast.Attribute):
                names.append(base.attr)
        return names

    def _inherits_from_basemodel(
        self, class_name: str, visited: set[str] | None = None
    ) -> bool:
        """Check if a class inherits from Pydantic's BaseModel directly or indirectly."""
        if visited is None:
            visited = set()

        if class_name in visited:
            return False

        visited.add(class_name)
        class_def = self._class_definitions.get(class_name)
        if not class_def:
            return False

        # Check direct inheritance from BaseModel
        if "BaseModel" in class_def.bases:
            return True

        # Check indirect inheritance through other bases
        return any(
            self._inherits_from_basemodel(base, visited)
            for base in class_def.bases
            if base in self._class_definitions
        )


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
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
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
