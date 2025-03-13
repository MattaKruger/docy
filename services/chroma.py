from typing import Dict, List, Optional
from datetime import datetime

import chromadb


class ChromaService:
    def __init__(self, embedding_model: str) -> None:
        self.client = chromadb.PersistentClient()
        self.embedding_model = embedding_model

    def create_collection(self, name, metadata):
        chroma_collection = self.client.get_or_create_collection(name, metadata=metadata)
        return chroma_collection

    def get_collection(self, name: str):
        return self.client.get_collection(name)

    def delete_collection(self, name: str):
        self.client.delete_collection(name)

    def add_document_to_collection(self, name: str, ids: list[str], documents: list[str], metadatas):
        collection = self.client.get_collection(name)
        collection.add(ids=ids, documents=documents, metadatas=metadatas)

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
