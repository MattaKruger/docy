from fastapi import APIRouter, Depends, HTTPException
from services import ChromaService

from pydantic import BaseModel


router = APIRouter(prefix="/chroma", tags=["chroma"])


class CollectionMetadata(BaseModel):
    framework: str
    language: str



@router.get("/")
def get_collection(name: str, chroma_client: ChromaService = Depends(ChromaService)):
    try:
        collection = chroma_client.get_collection(name)
    except:
        return HTTPException(status_code=404, detail="Not found.")


@router.delete("/")
def delete_collection(name: str, chroma_client: ChromaService = Depends(ChromaService)):
    try:
        collection = chroma_client.get_collection(name)
        chroma_client.delete_collection(collection.name)
    except:
        return HTTPException(status_code=404, detail="Not found.")


@router.post("/")
def create_collection(name: str, metadata: CollectionMetadata, chroma_client: ChromaService = Depends(ChromaService)):
    chroma_client.create_collection(name, metadata.model_dump())
