from typing import Dict, List, Optional, Any
from datetime import datetime

import chromadb
from chromadb.errors import NotFoundError
from chromadb.utils import embedding_functions

sentence_transformer_ef = embedding_functions


class ChromaService:
    def __init__(self, embedding_model: str = "all-mpnet-base-v2") -> None:
        self.client = chromadb.PersistentClient()
        self.embedding_model = embedding_model

    def get_or_create(self, name: str, metadata: Optional[Dict[str, str]] = None):
        return self.client.get_or_create_collection(name=name, metadata=metadata, embedding_function=sentence_transformer_ef)

    def delete_collection(self, name: str):
        try:
            collection = self.client.get_collection(name)
            if collection:
                self.client.delete_collection(name)
        except NotFoundError:
            raise NotFoundError(f"Collection '{name}' not found")

    def add_document_to_collection(self, name: str, ids: list[str], documents: list[str], metadatas):
        collection = self.client.get_collection(name)
        collection.add(ids=ids, documents=documents, metadatas=metadatas)

    def get_documents(
        self, collection_name: str, where_filter: Optional[Dict[str, Any]] = None, limit: Optional[int] = None
    ):
        """Gets documents from ChromaDB collection based on filters."""
        documents = self.client.get_collection(collection_name).get(where=where_filter, limit=limit)
        return documents

    # def query_collection(self, query):
    #     collection = self.client.get_collection(query.collection_name)
    #     # Ensure where and where_document are dictionaries (or None)
    #     where = query.where
    #     where_document = query.where_document
    #     return collection.query(
    #         query_texts=query.query_texts,
    #         n_results=query.n_results,
    #         where=where,
    #         where_document=where_document,
    #     )

    # def upsert_collection(self, collection: CollectionUpsert):
    #     chroma_collection = self.client.get_collection(collection.collection_name)
    #     chroma_collection.upsert(
    #         ids=collection.ids,
    #         documents=collection.documents,
    #         metadatas=collection.metadatas,
    #     )
    #     return chroma_collection
