import pathlib
from typing import Dict, List

import logfire

from config import settings


BASE_DIR = settings.BASE_DATA_DIR
CODING_DIR = BASE_DIR / settings.CODING_SUBDIR

CODING_DIR.mkdir(exist_ok=True)


async def list_files(directory: str = settings.CODING_SUBDIR) -> List[str] | str:
    """Lists files in a specified subdirectory within the data directory."""
    target_dir = BASE_DIR / directory
    if not str(target_dir.resolve()).startswith(str(BASE_DIR.resolve())):
        return f"Error: Access denied to directory '{directory}'."
    if not target_dir.is_dir():
        return f"Error: Directory '{directory}' does not exist relative to {BASE_DIR}."
    try:
        files = [f.name for f in target_dir.iterdir() if f.is_file()]
        return files
    except Exception as e:
        logfire.error(f"Error listing files in '{directory}': {e}")
        return f"Error listing files in '{directory}': {e}"


async def save_file(file_name: str, file_content: str, extension: str) -> str:
    """Save file to the coding subdirectory."""
    if not extension.startswith("."):
        extension = "." + extension
    safe_file_name = pathlib.Path(f"{file_name}{extension}").name
    if not safe_file_name or safe_file_name != f"{file_name}{extension}":
        return "Error: Invalid file name or extension provided."

    file_path = CODING_DIR / safe_file_name
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(file_content)
        return f"File saved at {file_path}"
    except Exception as e:
        logfire.error(f"Error saving file '{file_path}': {e}")
        return f"Error saving file '{file_path}': {e}"


async def read_file(file_name: str) -> Dict[str, str] | str:
    """Read file from the coding subdirectory."""
    safe_file_name = pathlib.Path(file_name).name
    if not safe_file_name or safe_file_name != file_name:
        return "Error: Invalid file name provided."

    file_path = CODING_DIR / safe_file_name
    if not file_path.is_file():
        return f"Error: File '{safe_file_name}' not found in {CODING_DIR}."
    try:
        read_content = file_path.read_text(encoding="utf-8")
        return {"file_name": safe_file_name, "content": read_content}
    except Exception as e:
        logfire.error(f"Error reading file '{file_path}': {e}")
        return f"Error reading file '{file_path}': {e}"


exported_tools = {
    "list_files": list_files,
    "save_file": save_file,
    "read_file": read_file,
}
