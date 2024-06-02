"""Calculate the number of tokens for items in a datasetm using a Hugging Face model.

By default, the script prints the number of tokens in the longest sequence. It can
also print the longest sequence itself.

It can also save a new JSON file with the added token count for each item.

The input format a JSON file with a list of objects. Each object must have an "input"
key with the text to tokenise.
"""

# pyright: basic
import argparse
import json
import os
from typing import Any, cast

from beartype.door import is_bearable

# Disable "None of PyTorch, TensorFlow >= 2.0, or Flax have been found." warning.
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
from transformers import AutoTokenizer  # noqa: E402


def longest_sequence(model_name: str, data: list[dict[str, Any]]) -> list[str]:
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    longest_seq: list[str] | None = None

    for item in data:
        tokens = tokenizer.tokenize(item["input"].strip())
        if longest_seq is None or len(tokens) > len(longest_seq):
            longest_seq = cast(list[str], tokens)

    assert longest_seq is not None, "No data provided."
    return longest_seq


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("model_name", type=str, help="Model name")
    parser.add_argument(
        "input",
        type=argparse.FileType("r"),
        help="Input file path",
        nargs="?",
        default="-",
    )
    parser.add_argument(
        "--print-sequence",
        "-P",
        help="Print the longest sequence",
        action="store_true",
    )
    args = parser.parse_args()

    data = json.load(args.input)

    data_keys = {"input"}
    if not is_bearable(data, list[dict[str, Any]]):
        raise SystemExit("Invalid JSON format. Expected a list of objects.")
    if missing := data_keys - data[0].keys():
        raise SystemExit(f"Invalid JSON format. Missing keys: {missing}.")

    longest_seq = longest_sequence(args.model_name, data)

    if args.print_sequence:
        print(longest_seq)
    print(f"{len(longest_seq)} tokens.")


if __name__ == "__main__":
    main()
