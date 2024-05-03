import json
import sys

import tomli


def main() -> None:
    if "-h" in sys.argv or "--help" in sys.argv:
        print("Usage: toml2json < input.toml > output.json")
        return

    data = tomli.loads(sys.stdin.read())
    json.dump(data, sys.stdout, indent=2)


if __name__ == "__main__":
    main()
