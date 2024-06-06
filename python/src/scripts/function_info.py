"""Find information about the functions in the Python files in a directory.

The information is stored in a JSON file.

BETA!
"""

import argparse
import ast
import json
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any, TextIO


def get_function_info(node: ast.FunctionDef, path: Path) -> dict[str, Any]:
    if docstring := ast.get_docstring(node):
        len_docstring = len(docstring.split("\n"))
    else:
        len_docstring = 0

    lines_of_code = 0
    for body in node.body:
        is_docstring = isinstance(body, ast.Expr) and isinstance(
            body.value, ast.Constant
        )
        is_pass = isinstance(body, ast.Pass)
        is_comment = (
            isinstance(body, ast.Expr)
            and isinstance(body.value, ast.Constant)
            and isinstance(body.value.value, str)
        )
        if is_docstring or is_pass or is_comment:
            continue

        end_lineno = body.end_lineno or body.lineno
        lines_of_code += end_lineno - body.lineno + 1

    return {
        "path": f"{path}:{node.lineno}",
        "name": node.name,
        "lines": lines_of_code,
        "params": len(node.args.args),
        "defaults": len(node.args.defaults),
        "docstring": len_docstring,
    }


def process_file(path: Path) -> Iterator[dict[str, Any]]:
    try:
        code = path.read_text()
    except UnicodeDecodeError:
        print(f"Could not read {path}", file=sys.stderr)
        return

    tree = ast.parse(code)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            yield get_function_info(node, path)

        elif isinstance(node, ast.ClassDef):
            for subnode in node.body:
                if isinstance(subnode, ast.FunctionDef):
                    subnode_info = get_function_info(subnode, path)
                    subnode_info["name"] = f"{node.name}.{subnode_info['name']}"
                    yield subnode_info


def is_in_hidden_dir(path: Path) -> bool:
    return any(part.startswith(".") for part in path.parts)


def process_directory(directory: Path) -> list[dict[str, Any]]:
    return [
        func
        for file in directory.rglob("*.py")
        if "venv" not in str(file) and not is_in_hidden_dir(file)
        for func in process_file(file)
    ]


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "dir", type=Path, help="The directory to process", nargs="?", default=Path(".")
    )
    parser.add_argument(
        "output_file",
        type=argparse.FileType("w"),
        help="The output file",
        nargs="?",
        default="-",
    )
    args = parser.parse_args()
    dir: Path = args.dir
    output_file: TextIO = args.output_file

    functions = process_directory(dir)
    functions = sorted(functions, key=lambda x: x["lines"], reverse=True)
    json.dump(functions, output_file, indent=2)


if __name__ == "__main__":
    main()
