from pathlib import Path
from typing import List, Dict, Any, Annotated

import re
import json
import datetime

from pydantic import BaseModel, Field, field_validator, model_validator
import typer

app = typer.Typer()


class InvalidMarker:
    pass

class UnterminatedSpan:
    pass

class SkippedSize:
    pass

class TODO(BaseModel):
    name: str = Field("")
    prompt: str | None = Field(None)
    start_line: int = Field(0)
    code_lines: List[str]
    children: List["CompletedTODOSpan"]

    @model_validator(mode="before")
    @classmethod
    def parse_todo_string(cls, data: Any) -> Any:
        """
        Parses the input string '# TODO-{name}[{prompt_text}]'
        into a dictionary suitable for model creation.
        Runs *before* individual field validation.
        """
        if isinstance(data, str):
            pattern = r"^# TODO-(.+?)\[(.*?)\]$"
            match = re.match(pattern, data)

            if match:
                return {
                    "name": match.group(1),
                    "prompt": match.group(2)
                }
            else:
                raise ValueError(
                    f"Input string '{data}' does not match format '#TODO-{{name}}[{{prompt_text}}]"
                )

        if isinstance(data, dict):
            required_keys = {"name", "prompt_text", "raw_string"}
            if not required_keys.issubset(data.keys()):
                missing = required_keys - data.keys()
                pass
            return data

    @field_validator("name")
    @classmethod
    def check_name_format(cls, v: str) -> str:
        """
        Example: Validate the extracted name.
        Ensures the name is not empty and contains onyl alphanumeric chars.
        """
        if not v:
            raise ValueError("Name cannot be empty")
        if not v.isalnum():
            raise ValueError("Name must contain only alphanumeric characters")
        return v

    @field_validator("prompt")
    @classmethod
    def strip_prompt_whitespace(cls, v: str) -> str:
        """
        Example: Transform the extracted prompt text.
        Strips leading/trailing whitespace.
        """
        return v.strip()


class CompletedTODOSpan(TODO):
    llm_description: str = Field("")

class TODOError(BaseModel):
    error_type: InvalidMarker | UnterminatedSpan | SkippedSize
    file_path: str = Field("")
    line_number: int = Field(0)
    details: Dict[str, Any]


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
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
