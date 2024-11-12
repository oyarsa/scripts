"""Generate text using OpenAI's GPT, given a prompt and a file as input.

Prints number of input and output tokens and the cost to stderr.
"""

import argparse
from dataclasses import dataclass
from typing import TextIO

import openai

from scripts.util import HelpOnErrorArgumentParser

# Cost in $ per 1M tokens: (input cost, output cost)
# From https://openai.com/api/pricing/
MODEL_COSTS = {
    "gpt-4o-mini-2024-07-18": (0.15, 0.6),
    "gpt-4o-2024-08-06": (2.5, 10),
}


def calc_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    """Calculate API request based on the model and input/output tokens.

    NB: prompt_tokens/completion_tokens is the name given to input/output tokens in the
    usage object from the OpenAI result.

    Args:
        model: OpenAI model key
        prompt_tokens: the input tokens for the API
        completion_tokens: the output tokens from the API

    Returns:
        The total cost of the request. If the model is invalid, returns 0.
    """
    if model not in MODEL_COSTS:
        return 0

    input_cost, output_cost = MODEL_COSTS[model]
    return prompt_tokens / 1e6 * input_cost + completion_tokens / 1e6 * output_cost


@dataclass(frozen=True, kw_only=True)
class Result:
    input_tokens: int
    output_tokens: int
    output: str
    cost: float


def _generate_text(client: openai.OpenAI, model: str, prompt: str) -> Result:
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        model=model,
    )
    if usage := response.usage:
        cost = calc_cost(model, usage.prompt_tokens, usage.completion_tokens)
        input_tokens = usage.prompt_tokens
        output_tokens = usage.completion_tokens
    else:
        cost, input_tokens, output_tokens = 0, 0, 0

    output = response.choices[0].message.content or "<empty>"
    return Result(
        cost=cost, output=output, input_tokens=input_tokens, output_tokens=output_tokens
    )


def generate_text(prompt_file: TextIO, model: str, output: TextIO) -> None:
    client = openai.OpenAI()
    prompt = prompt_file.read()
    result = _generate_text(client, model, prompt)

    output.write(result.output + "\n")
    print(f"\nInput tokens: {result.input_tokens}")
    print(f"Output tokens: {result.output_tokens}")
    print(f"Cost: ${result.cost:.10f}")


def main() -> None:
    parser = HelpOnErrorArgumentParser(__doc__)
    parser.add_argument(
        "--prompt",
        type=argparse.FileType("r"),
        default="-",
        help="The file to use as input for text generation. Defaults to stdin.",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o",
        help="The model to use for text generation.",
    )
    parser.add_argument(
        "--output",
        type=argparse.FileType("w"),
        default="-",
        help="The file to write the output to. Defaults to stdout.",
    )
    args = parser.parse_args()
    generate_text(args.prompt, args.model, args.output)


if __name__ == "__main__":
    main()
