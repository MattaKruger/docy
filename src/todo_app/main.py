import datetime
import json
import re
from pathlib import Path
from typing import Annotated, Any, Dict, List

import typer
from pydantic import BaseModel, Field, field_validator, model_validator

app = typer.Typer()

TODO_SPAN_START = "# TODO-{name}"
TODO_SPAN_END = "# TODO-end"
TODO_SESSION_TIMESTAMP = "{timestamp}"
CONFIG_FILE = "gt_config.json"

PROMPT_STRUCTURE = """
    Context for the TODO item:
    Name: {name}

    Instructions for generation:
    {prompt_instruction}

    Code block to analyze:
    ```python
    {code_block}
"""


def save_to_file(path: str = "TODO.md", content: str = ""):
    file_path = Path(path)
    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(file_path, "a+") as f:
        # generate_timestamp
        f.write(content)


def read_config(path: str):
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            print("Succesfully loaded config...")
    except FileNotFoundError:
        config = {}
    return config


@app.command()
def parse_todo():
    return 0


if __name__ == "__main__":
    app()
