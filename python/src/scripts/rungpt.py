"""Generate text using OpenAI's GPT, given a prompt and a file as input."""

import argparse

import openai


def generate_text(client: openai.OpenAI, model: str, prompt: str) -> str:
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        model=model,
    )

    return response.choices[0].message.content or "<empty>"


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
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

    client = openai.OpenAI()
    prompt = args.prompt.read()
    result = generate_text(client, args.model, prompt)

    args.output.write(result)


if __name__ == "__main__":
    main()
