import re
from typing import Any, Dict, List

from pydantic import BaseModel, Field, field_validator, model_validator


# TODO implement exceptions
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
                return {"name": match.group(1), "prompt": match.group(2)}
            else:
                raise ValueError(f"Input string '{data}' does not match format '#TODO-{{name}}[{{prompt_text}}]")

        if isinstance(data, dict):
            required_keys = {"name", "prompt_text", "raw_string"}
            if not required_keys.issubset(data.keys()):
                required_keys - data.keys()
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
