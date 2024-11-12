#!/usr/bin/env python3
"""Find classes that are not record types.

This means dataclasses, NamedTuples, Enums, TypedDicts, or Pydantic models.
NB: this script doesn't import files, just checks the names in the AST. This means that
it cannot track the inheritance chains, so if A <: BaseModel and B <: A, A won't show
but B will.
"""

import ast
import subprocess
import sys
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

from scripts.util import HelpOnErrorArgumentParser


@dataclass(frozen=True)
class Class:
    filename: Path
    lineno: int
    name: str
    source_line: str
    prev_line: str | None = None


@dataclass
class ClassDefinition:
    node: ast.ClassDef
    bases: set[str]


SPECIAL_BASE_SUFFIXES = {"BaseModel", "NamedTuple", "Enum", "TypedDict"}


@dataclass
class ClassFinder(ast.NodeVisitor):
    filename: Path
    source_lines: list[str]
    classes: list[Class] = field(default_factory=list)
    _class_definitions: dict[str, ClassDefinition] = field(default_factory=dict)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:  # noqa: N802
        # Store the class definition for later inheritance checking
        self._class_definitions[node.name] = ClassDefinition(
            node=node,
            bases=set(self._get_base_names(node.bases)),
        )

        if self._should_exclude_class(node.name):
            return

        # Get the actual source line (lineno is 1-based, list is 0-based)
        source_line = self.source_lines[node.lineno - 1].rstrip()

        # Get previous line if it exists and isn't empty
        prev_line = None
        if node.lineno > 1:
            prev_line = self.source_lines[node.lineno - 2].rstrip()
            if not prev_line:  # Don't include empty or whitespace-only lines
                prev_line = None

        self.classes.append(
            Class(self.filename, node.lineno, node.name, source_line, prev_line)
        )

    def _get_base_names(self, bases: list[ast.expr]) -> list[str]:
        """Extract base class names from AST expressions."""
        names: list[str] = []
        for base in bases:
            if isinstance(base, ast.Name):
                names.append(base.id)
            elif isinstance(base, ast.Attribute):
                # Get the full attribute chain
                parts: list[str] = []
                current = base
                while isinstance(current, ast.Attribute):
                    parts.append(current.attr)
                    current = current.value
                if isinstance(current, ast.Name):
                    parts.append(current.id)
                names.append(".".join(reversed(parts)))
        return names

    def _should_exclude_class(self, class_name: str) -> bool:
        """Determine if a class should be excluded from the results."""
        class_def = self._class_definitions.get(class_name)
        if not class_def:
            return False

        # Check for dataclass decorator
        if class_def.node.decorator_list and any(
            (isinstance(dec, ast.Name) and dec.id == "dataclass")
            or (
                isinstance(dec, ast.Call)
                and isinstance(dec.func, ast.Name)
                and dec.func.id == "dataclass"
            )
            or (
                isinstance(dec, ast.Call)
                and isinstance(dec.func, ast.Attribute)
                and dec.func.attr == "dataclass"
            )
            for dec in class_def.node.decorator_list
        ):
            return True

        return self._inherits_from_special_base(class_name)

    def _inherits_from_special_base(
        self, class_name: str, visited: set[str] | None = None
    ) -> bool:
        """Check if a class inherits from any special base class directly or indirectly."""
        if visited is None:
            visited = set()

        if class_name in visited:
            return False

        visited.add(class_name)
        class_def = self._class_definitions.get(class_name)
        if not class_def:
            return False

        # Check if any base class ends with our special suffixes
        if any(
            any(base.endswith(suffix) for suffix in SPECIAL_BASE_SUFFIXES)
            for base in class_def.bases
        ):
            return True

        # Check indirect inheritance through other bases
        return any(
            self._inherits_from_special_base(base, visited)
            for base in class_def.bases
            if base in self._class_definitions
        )


def find_classes_in_file(filename: Path) -> list[Class]:
    source_text = filename.read_text()
    source_lines = source_text.splitlines()
    node = ast.parse(source_text, filename=filename)
    class_finder = ClassFinder(filename, source_lines)
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
    parser = HelpOnErrorArgumentParser(__doc__)
    parser.add_argument(
        "dirs", type=Path, nargs="*", default=[Path.cwd()], help="Directory to search"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show text surrounding the class definition",
    )
    args = parser.parse_args()

    dirs: list[Path] = args.dirs
    classes = [
        class_
        for dir in dirs
        for file in find_python_files(dir)
        for class_ in find_classes_in_file(file)
    ]

    for class_ in classes:
        if args.verbose:
            print(f"{class_.filename}:{class_.lineno}")
            if class_.prev_line:
                print(f"  {class_.prev_line}")
            print(f"  {class_.source_line}")
            print()
        else:
            print(f"{class_.filename}:{class_.lineno}::{class_.name}")


if __name__ == "__main__":
    main()
