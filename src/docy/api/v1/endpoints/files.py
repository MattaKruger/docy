import os

from typing import List
from pathlib import Path
from pydantic import BaseModel

from fastapi import APIRouter, Depends, status, Query, HTTPException, Path as PathParam
from fastapi.responses import FileResponse, JSONResponse

from docy.core import Settings

settings = Settings()


DATA_DIR = Path(settings.DOCY_DATA_DIR)
DATA_DIR.mkdir(exist_ok=True, parents=True)


class File(BaseModel):
    name: str
    content: str


class FileInfo(BaseModel):
    name: str
    size: int
    modified: str


router = APIRouter(prefix="/files", tags=["files"])


@router.get("/", response_model=List[FileInfo])
async def get_files():
    files = []
    for file_path in DATA_DIR.glob("*"):
        if file_path.is_file():
            try:
                stat = file_path.stat()
                files.append(FileInfo(
                    name=file_path.name,
                    size=stat.st_size,
                    modified=str(stat.st_mtime)
                ))
            except Exception as e:
                # Skip files that can't be accessed
                continue

    return files


@router.get("/{file_name}")
async def get_file(
    file_name: str = PathParam(...),
    as_download: bool = Query(False, description="Set to true to download the file instead of viewing it")
):
    """
    Get a specific file by name.
    Can return file content as JSON or serve the file directly depending on the query parameter.
    """
    file_path = DATA_DIR / file_name

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File '{file_name}' not found"
        )

    # Return the file as a direct download/view
    return FileResponse(
        path=file_path,
        filename=file_name if as_download else None,
        media_type="application/octet-stream" if as_download else None
    )


@router.get("/{file_name}/content", response_model=File)
async def get_file_content(file_name: str = PathParam(...)):
    """
    Get a specific file's content as JSON.
    """
    file_path = DATA_DIR / file_name

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File '{file_name}' not found"
        )

    try:
        content = file_path.read_text()
        return File(name=file_name, content=content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reading file: {str(e)}"
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_file(file: File):
    """
    Create a new file or update an existing file.
    """
    file_path = DATA_DIR / file.name

    # Check if file contains invalid characters or paths
    try:
        # Ensure the file path is within the DATA_DIR
        if not file_path.resolve().is_relative_to(DATA_DIR.resolve()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file name - path traversal detected"
            )
    except (ValueError, RuntimeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file name"
        )

    try:
        # Write content to file
        file_path.write_text(file.content)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"message": f"File '{file.name}' created successfully"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating file: {str(e)}"
        )


@router.delete("/{file_name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(file_name: str = PathParam(...)):
    """
    Delete a file by name.
    """
    file_path = DATA_DIR / file_name

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File '{file_name}' not found"
        )

    try:
        file_path.unlink()
        return None
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting file: {str(e)}"
        )
