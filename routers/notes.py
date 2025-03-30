from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from pydantic import BaseModel

from services import NoteService
from settings import Settings


settings = Settings()


router = APIRouter(prefix="/notes", tags=["notes"])


class NoteMetadata(BaseModel):
    tags: Optional[List[str]] = []
    created: Optional[datetime] = None
    modified: Optional[datetime] = None
    status: Optional[str] = None


class NoteCreate(BaseModel):
    title: str
    content: Optional[str] = None
    metadata: Optional[NoteMetadata] = None
    folder: Optional[str] = None
    template: Optional[str] = None


class NoteUpdate(BaseModel):
    content: Optional[str] = None
    metadata: Optional[NoteMetadata] = None


class NoteResponse(BaseModel):
    title: str
    path: str
    content: str
    metadata: NoteMetadata
    created: datetime
    modified: datetime


def get_note_service():
    # You might want to make this a proper dependency injection
    # with configuration and error handling
    return NoteService(settings.OBSIDIAN_VAULT_DIR)


@router.get("/", response_model=List[NoteResponse])
async def get_all_notes(
    obsidian_service: NoteService = Depends(get_note_service),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Get all notes with pagination"""
    try:
        notes = obsidian_service.get_all_notes()
        return notes[offset : offset + limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recent", response_model=List[NoteResponse])
async def get_recent_notes(
    limit: int = Query(10, ge=1, le=50), obsidian_service: NoteService = Depends(get_note_service)
):
    """Get recent notes"""
    try:
        return obsidian_service.get_recent_notes(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_model=List[NoteResponse])
async def search_notes(
    query: str = Query(..., min_length=1), obsidian_service: NoteService = Depends(get_note_service)
):
    """Search notes by content"""
    try:
        return obsidian_service.search_notes(query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: str = Path(..., description="The note identifier or path"),
    obsidian_service: NoteService = Depends(get_note_service),
):
    """Get a specific note by ID"""
    try:
        note = obsidian_service.read_note(note_id)
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        return note
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=NoteResponse, status_code=201)
async def create_note(note: NoteCreate, obsidian_service: NoteService = Depends(get_note_service)):
    """Create a new note"""
    try:
        created_note = obsidian_service.create_note(
            title=note.title,
            content=note.content,
            metadata=note.metadata.dict() if note.metadata else None,
            folder=note.folder,
            template=note.template,
        )
        return obsidian_service.read_note(created_note)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(note_id: str, note_update: NoteUpdate, obsidian_service: NoteService = Depends(get_note_service)):
    """Update an existing note"""
    try:
        success = obsidian_service.update_note(
            note_id, content=note_update.content, metadata=note_update.metadata.dict() if note_update.metadata else None
        )
        if not success:
            raise HTTPException(status_code=404, detail="Note not found")
        return obsidian_service.read_note(note_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{note_id}/links", response_model=List[str])
async def get_note_links(note_id: str, obsidian_service: NoteService = Depends(get_note_service)):
    """Get all links from a specific note"""
    try:
        note = obsidian_service.read_note(note_id)
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        return obsidian_service.find_links(note["content"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{note_id}/tags", response_model=List[str])
async def get_note_tags(note_id: str, obsidian_service: NoteService = Depends(get_note_service)):
    """Get all tags from a specific note"""
    try:
        note = obsidian_service.read_note(note_id)
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        return obsidian_service.get_tags(note["content"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
