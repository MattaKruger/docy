import uuid
from typing import Optional, List, Annotated, Dict
from chromadb.api.models.CollectionCommon import Document
from fastapi import APIRouter, Depends, HTTPException, Path

from services import ChromaService, GithubService

from pydantic import BaseModel, Field

router = APIRouter(prefix="/chroma", tags=["chroma"])


class QueryResult(BaseModel):
    ids: List[str]
    documents: List[str]
    metadatas: List[dict]


class CollectionMetadata(BaseModel):
    language: Optional[str] = Field(default="Python", description="The programming language of the documents.")
    framework: Optional[str] = Field(default="FastAPI", description="The framework used in the documents")


class DocumentMetadata(BaseModel):
    description: str = Field(default="main entry point for fastapi", description="The description of the document.")
    source: Optional[str] = Field(default="github", description="The source of the documents.")
    doc_extension: Optional[str] = Field(default=".md", description="The extension of the documents.")


@router.post("/{name}")
def get_or_create_collection(
    name: str = Path(..., description="The name of the collection to retrieve"),
    collection_metadata: CollectionMetadata = CollectionMetadata(),
    chroma_client: ChromaService = Depends(ChromaService),
):
    try:
        collection = chroma_client.get_or_create(name, collection_metadata.model_dump())
        return {
            "name": collection.name,
            "metadata": collection.metadata,
            "documents": collection.get(include=["documents", "metadatas"]),  # type: ignore
            "document_count": collection.count(),
        }
    except:
        return HTTPException(status_code=404, detail="Not found.")


@router.post("/{name}/add")
def add_docs_to_collection(
    docs: Annotated[List[str], Field(..., description="The documents to add")],
    name: str = Path(..., description="The name of the collection to retrieve"),
    document_metadata: DocumentMetadata = DocumentMetadata(),
    chroma_client: ChromaService = Depends(ChromaService),
):
    try:
        collection = chroma_client.get_or_create(name)
        collection.add(
            ids=[str(uuid.uuid4()) for _ in docs],
            embeddings=[],
            documents=docs,
            metadatas=document_metadata.model_dump())
    except:
        return HTTPException(status_code=404, detail="Not found.")


@router.post("/{name}/get")
def get_collection_documents(
    query_texts: Annotated[List[str], Field(..., description="The query texts to search for")],
    name: str = Path(..., description="The name of the collection to retrieve"),
    where: Annotated[str, "The filter condition for the query"] = "",
    where_document: Annotated[str, Field(..., description="The filter condition for the document")] = "",
    chroma_client: ChromaService = Depends(ChromaService),
):
    try:
        collection = chroma_client.get_or_create(name, None)
        results = collection.query(query_texts=query_texts, n_results=2, where_document={"$contains": where_document})
        return results
    except:
        return HTTPException(status_code=404, detail="Not found.")


@router.delete("/")
def delete_collection(name: str, chroma_client: ChromaService = Depends(ChromaService)):
    try:
        collection = chroma_client.get_or_create(name, None)
        chroma_client.delete_collection(collection.name)
    except:
        return HTTPException(status_code=404, detail="Not found.")


@router.post("/")
def create_collection(name: str, metadata: CollectionMetadata, chroma_client: ChromaService = Depends(ChromaService)):
    chroma_client.get_or_create(name, metadata)


@router.post("/repo", response_model=None)
def create_collection_from_repo(
    name: str,
    repo_url: str,
    docs_path: str,
    # chroma_client: ChromaService = Depends(ChromaService),
    # github_client: GithubService = Depends(GithubService),
):
    chroma = ChromaService()
    github = GithubService(chroma)
    try:
        collection = chroma.get_or_create(name, None)
        github.extract_repo_docs(collection.name, repo_url, docs_path)
    except:
        return HTTPException(status_code=404, detail="Not found.")
