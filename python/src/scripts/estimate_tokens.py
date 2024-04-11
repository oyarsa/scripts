import typer
import tiktoken

app = typer.Typer()

# Let's use a reasonably common GPT-4 encoding
encoding = tiktoken.get_encoding("cl100k_base")


@app.command()
def calculate(file: typer.FileText = typer.Argument(..., help="Path to the file")):
    """Calculates a more accurate GPT-4 token count of a text file using tiktoken."""
    text = file.read()
    tokens = encoding.encode(text)

    print(len(tokens))


if __name__ == "__main__":
    app()
