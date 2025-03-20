from typing import Dict, Optional, Any

import chromadb
from chromadb.api.models.Collection import Collection
from chromadb.errors import NotFoundError
from chromadb.utils import embedding_functions


class ChromaService:
    def __init__(self) -> None:
        self.embedding_model = "all-mpnet-base-v2"
        self.client = chromadb.PersistentClient()
        self.embeddings_function = embedding_functions.DefaultEmbeddingFunction()

    def get(self, name: str) -> Collection | None:
        try:
            return self.client.get_collection(name=name)
        except ValueError:
            return None

    def get_or_create(self, name: str, metadata: Optional[Dict[str, str]] = None):
        return self.client.get_or_create_collection(name=name, metadata=metadata)

    def add_documents_to_collection(self, name: str, ids: list[str], documents: list[str], metadatas):
        collection = self.client.get_collection(name)
        collection.add(ids=ids, documents=documents, metadatas=metadatas)

    def get_documents(
        self, collection_name: str, where_filter: Optional[Dict[str, Any]] = None, limit: Optional[int] = None
    ):
        """Gets documents from ChromaDB collection based on filters."""
        documents = self.client.get_collection(collection_name).get(where=where_filter, limit=limit)
        return documents

    def delete_collection(self, name: str):
        try:
            collection = self.client.get_collection(name)
            if collection:
                self.client.delete_collection(name)
        except NotFoundError:
            raise NotFoundError(f"Collection '{name}' not found")
