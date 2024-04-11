import argparse
from datetime import datetime
from pathlib import Path


def modified_time(path: Path) -> datetime:
    return datetime.fromtimestamp(path.stat().st_mtime)


def get_latest_modified_time(path: Path) -> datetime:
    return max(
        (modified_time(file) for file in path.rglob("*")),
        default=modified_time(path),
    )


def is_code_file(path: Path) -> bool:
    extension = path.suffix.lower()
    if extension in {".py", ".sh", ".bash", ".fish"}:
        return True

    try:
        first_line = path.read_text().splitlines()[0].strip()
        if first_line.startswith("#!"):  # First line is a shebang
            shells = ["python", "bash", "fish", "/bin/sh", "env"]
            return any(shell in first_line for shell in shells)
    except (UnicodeDecodeError, IndexError):
        return False

    return False


def coloured(text: object, colour: str) -> str:
    return f"{colour}{text}\033[0m"


def path_color(path: Path) -> str:
    if path.is_dir():
        return "\033[94m"  # Blue
    if is_code_file(path):
        return "\033[92m"  # Green
    if path.suffix.lower() == ".json":
        return "\033[95m"  # Magenta
    return "\033[97m"  # White


def pretty_print_entries(paths: list[Path], reverse: bool = False) -> str:
    entries = sorted(
        (
            (get_latest_modified_time(subpath), subpath)
            for path in paths
            for subpath in path.glob("*")
        ),
        key=lambda x: x[0],
        reverse=reverse,
    )

    return "\n".join(
        f"{time.strftime('%a %Y-%m-%d %H:%M:%S')}  {coloured(path, path_color(path))}"
        for time, path in entries
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Pretty print directory entries.")
    parser.add_argument(
        "paths",
        type=Path,
        nargs="*",
        default=[Path(".")],
        help="Paths to pretty print (default: current directory)",
    )
    parser.add_argument(
        "-r", "--reverse", action="store_true", help="Reverse the order of the entries"
    )
    args = parser.parse_args()

    output = pretty_print_entries(args.paths, args.reverse)
    print(output)


if __name__ == "__main__":
    main()
