from fastapi import APIRouter, Depends, HTTPException
from chroma_client import ChromaClient

from pydantic import BaseModel


router = APIRouter(prefix="/chroma", tags=["chroma"])


@router.get("/")
def get_collection(name: str, chroma_client: ChromaClient = Depends(ChromaClient)):
    try:
        collection = chroma_client.get_collection(name)
    except:
        return HTTPException(status_code=404, detail="Not found.")


@router.delete("/")
def delete_collection(name: str, chroma_client: ChromaClient = Depends(ChromaClient)):
    try:
        collection = chroma_client.get_collection(name)
        chroma_client.delete_collection(collection.name)
    except:
        return HTTPException(status_code=404, detail="Not found.")


# @router.post("/")
# def create_collection(collection: CollectionCreate, chroma_client: ChromaClient = Depends(ChromaClient)):
#     chroma_client.create_collection(collection)


# @router.get("/query")
# def query_collection(query: CollectionQuery, chroma_client: ChromaClient = Depends(ChromaClient)):
#     chroma_client.query_collection(query)
