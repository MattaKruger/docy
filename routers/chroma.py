import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path

from logger import chroma_logger
from models import CollectionMetadata, DocumentMetadata, DocumentQuery
from services import ChromaService

router = APIRouter(prefix="/chroma", tags=["chroma"])


@router.post("/{name}/")
def get_collection(
    name: str = Path(..., description="The name of the collection to create or get"),
    chroma_service: ChromaService = Depends(ChromaService),
):
    try:
        collection = chroma_service.get(name=name)
        if collection:
            return {"name": collection.name, "count": collection.count()}
        return None
    except Exception as err:
        chroma_logger.error(err)
        raise err


@router.get("/collections")
def get_collections(chroma_service: ChromaService = Depends(ChromaService)):
    return chroma_service.get_collections()


@router.post("/{name}/create")
def create_collection(
    name: str = Path(..., description="The name of the collection to create or get"),
    chroma_service: ChromaService = Depends(ChromaService),
):
    chroma_service.get_or_create(name=name)


@router.put("/{name}/update")
def update_collection(
    name: str = Path(..., description="The name of the collection you want to update"),
    updated_documents: Optional[List[str]] = None,
    updated_metadata: CollectionMetadata = CollectionMetadata(),
    chroma_service: ChromaService = Depends(ChromaService),
):
    try:
        collection = chroma_service.get(name=name)

        if collection is None:
            return

        collection.upsert(
            ids=getattr(collection, "id", []),
            documents=updated_documents,
            metadatas=updated_metadata.model_dump(),
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Not found.")


@router.post("/{name}/docs/add")
def add_documents_to_collection(
    documents: List[str],
    name: str = Path(..., description="The name of the collection to retrieve"),
    document_metadata: DocumentMetadata = DocumentMetadata(),
    chroma_client: ChromaService = Depends(ChromaService),
):
    try:
        collection = chroma_client.get(name)
        if collection:
            collection.add(
                ids=[str(uuid.uuid4()) for _ in documents],
                documents=documents,
                metadatas=document_metadata.model_dump(),
            )
            return collection
    except Exception as e:
        chroma_logger.error(e)
        raise HTTPException(status_code=400, detail="Not found.")


@router.post("/{name}/get")
def get_collection_documents(
    document_query: DocumentQuery = DocumentQuery(),
    name: str = Path(..., description="The name of the collection to retrieve"),
    where_document: str = "",
    n_results: int = 5,
    chroma_client: ChromaService = Depends(ChromaService),
):
    try:
        collection = chroma_client.get(
            name=name,
        )
        if collection is None:
            return None

        return collection.query(
            query_texts=document_query.texts,
            where={"category": document_query.category, "language": document_query.language},
            where_document={"$contains": where_document},
            n_results=n_results,
        )
    except Exception as e:
        chroma_logger.error(e)
        return HTTPException(status_code=404, detail="Not found.")


@router.delete("/{name}/delete", response_model=None)
def delete_collection(
    name: str = Path(..., description="The name of the collection to delete"),
    chroma_client: ChromaService = Depends(ChromaService),
):
    try:
        collection = chroma_client.get(name=name)
        if collection is None:
            return {"message": f"Collection called {name} not found!"}

        chroma_client.delete_collection(collection.name)
        return {"message": f"{collection.name} collection deleted."}
    except Exception as e:
        chroma_logger.error(e)
        return HTTPException(status_code=404, detail="Not found.")
