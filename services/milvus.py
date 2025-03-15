# from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
# import numpy as np
# from typing import List, Dict, Any, Optional, Union, Tuple


# class MilvusClient:
#     """
#     A client class for interacting with Milvus vector database.
#     Simplifies connection management and common vector DB operations.
#     """

#     def __init__(self, host: str = "localhost", port: str = "19530", alias: str = "default"):
#         """
#         Initialize the Milvus client.

#         Args:
#             host: Milvus server host
#             port: Milvus server port
#             alias: Connection alias
#         """
#         self.host = host
#         self.port = port
#         self.alias = alias
#         self.connected = False

#     def connect(self) -> bool:
#         """Connect to Milvus server."""
#         try:
#             connections.connect(alias=self.alias, host=self.host, port=self.port)
#             self.connected = True
#             print(f"Connected to Milvus server at {self.host}:{self.port}")
#             return True
#         except Exception as e:
#             print(f"Failed to connect to Milvus: {e}")
#             return False

#     def disconnect(self) -> None:
#         """Disconnect from Milvus server."""
#         if self.connected:
#             connections.disconnect(self.alias)
#             self.connected = False
#             print("Disconnected from Milvus server")

#     def create_collection(
#         self,
#         collection_name: str,
#         vector_dim: int,
#         vector_field_name: str = "vector",
#         id_field_name: str = "id",
#         text_field_name: Optional[str] = None,
#         text_max_length: int = 255,
#         description: str = "",
#         recreate: bool = False,
#     ) -> Optional[Collection]:
#         """
#         Create a new collection in Milvus.

#         Args:
#             collection_name: Name of the collection
#             vector_dim: Dimension of the vector field
#             vector_field_name: Name of the vector field
#             id_field_name: Name of the ID field
#             text_field_name: Optional name for a text field
#             text_max_length: Maximum length for the text field
#             description: Collection description
#             recreate: Whether to drop and recreate if collection exists

#         Returns:
#             The created collection or None if failed
#         """
#         if not self.connected:
#             print("Not connected to Milvus. Call connect() first.")
#             return None

#         # Check if collection exists
#         if utility.has_collection(collection_name):
#             if recreate:
#                 print(f"Collection '{collection_name}' exists. Dropping it.")
#                 utility.drop_collection(collection_name)
#             else:
#                 print(f"Collection '{collection_name}' already exists.")
#                 return Collection(name=collection_name)

#         # Define fields
#         fields = [
#             FieldSchema(name=id_field_name, dtype=DataType.INT64, is_primary=True, auto_id=False),
#             FieldSchema(name=vector_field_name, dtype=DataType.FLOAT_VECTOR, dim=vector_dim),
#         ]

#         # Add text field if specified
#         if text_field_name:
#             fields.append(FieldSchema(name=text_field_name, dtype=DataType.VARCHAR, max_length=text_max_length))

#         # Create schema and collection
#         schema = CollectionSchema(fields, description=description)
#         collection = Collection(name=collection_name, schema=schema)
#         print(f"Collection '{collection_name}' created successfully.")

#         return collection

#     def create_index(
#         self,
#         collection_name: str,
#         field_name: str = "vector",
#         index_type: str = "IVF_FLAT",
#         metric_type: str = "L2",
#         index_params: Optional[Dict[str, Any]] = None,
#     ) -> bool:
#         """
#         Create an index on a field in a collection.

#         Args:
#             collection_name: Name of the collection
#             field_name: Name of the field to index
#             index_type: Type of index
#             metric_type: Metric type for similarity
#             index_params: Additional parameters for the index

#         Returns:
#             Success status
#         """
#         if not self.connected:
#             print("Not connected to Milvus. Call connect() first.")
#             return False

#         try:
#             collection = Collection(name=collection_name)
#             if index_params is None:
#                 if index_type == "IVF_FLAT":
#                     index_params = {"nlist": 128}
#                 elif index_type == "HNSW":
#                     index_params = {"M": 8, "efConstruction": 64}
#                 else:
#                     index_params = {}

#             index = {"index_type": index_type, "metric_type": metric_type, "params": index_params}

#             collection.create_index(field_name, index)
#             print(f"Created {index_type} index on field '{field_name}' in collection '{collection_name}'")
#             return True
#         except Exception as e:
#             print(f"Failed to create index: {e}")
#             return False

#     def insert_data(
#         self,
#         collection_name: str,
#         ids: List[int],
#         vectors: List[List[float]],
#         text_data: Optional[List[str]] = None,
#         text_field_name: Optional[str] = None,
#     ) -> int:
#         """
#         Insert data into a collection.

#         Args:
#             collection_name: Name of the collection
#             ids: List of IDs
#             vectors: List of vectors
#             text_data: Optional list of text data
#             text_field_name: Name of the text field

#         Returns:
#             Number of entities inserted
#         """
#         if not self.connected:
#             print("Not connected to Milvus. Call connect() first.")
#             return 0

#         try:
#             collection = Collection(name=collection_name)

#             entities = [ids, vectors]
#             field_names = ["id", "vector"]

#             if text_data and text_field_name:
#                 entities.append(text_data)
#                 field_names.append(text_field_name)

#             insert_result = collection.insert(entities, field_names)
#             print(f"Inserted {insert_result.insert_count} entities into collection '{collection_name}'")
#             return insert_result.insert_count
#         except Exception as e:
#             print(f"Failed to insert data: {e}")
#             return 0

#     def search(
#         self,
#         collection_name: str,
#         query_vectors: List[List[float]],
#         field_name: str = "vector",
#         limit: int = 10,
#         output_fields: Optional[List[str]] = None,
#         metric_type: str = "L2",
#         params: Optional[Dict[str, Any]] = None,
#     ) -> List[List[Dict[str, Any]]]:
#         """
#         Search for similar vectors in a collection.

#         Args:
#             collection_name: Name of the collection
#             query_vectors: List of query vectors
#             field_name: Vector field name
#             limit: Maximum number of results to return
#             output_fields: Fields to include in results
#             metric_type: Distance metric type
#             params: Search parameters

#         Returns:
#             Search results
#         """
#         if not self.connected:
#             print("Not connected to Milvus. Call connect() first.")
#             return []

#         try:
#             collection = Collection(name=collection_name)
#             collection.load()

#             if params is None:
#                 params = {"nprobe": 10} if metric_type == "L2" or metric_type == "IP" else {}

#             search_params = {"metric_type": metric_type, "params": params}

#             results = collection.search(
#                 data=query_vectors, anns_field=field_name, param=search_params, limit=limit, output_fields=output_fields
#             )

#             # Convert results to a more friendly format
#             formatted_results = []
#             for hits in results:
#                 hits_list = []
#                 for hit in hits:
#                     hit_dict = {
#                         "id": hit.id,
#                         "distance": hit.distance,
#                     }

#                     # Add output fields if any
#                     if output_fields:
#                         for field in output_fields:
#                             hit_dict[field] = hit.entity.get(field)

#                     hits_list.append(hit_dict)
#                 formatted_results.append(hits_list)

#             return formatted_results
#         except Exception as e:
#             print(f"Search error: {e}")
#             return []

#     def drop_collection(self, collection_name: str) -> bool:
#         """Drop a collection."""
#         if not self.connected:
#             print("Not connected to Milvus. Call connect() first.")
#             return False

#         try:
#             if utility.has_collection(collection_name):
#                 utility.drop_collection(collection_name)
#                 print(f"Collection '{collection_name}' dropped.")
#                 return True
#             else:
#                 print(f"Collection '{collection_name}' does not exist.")
#                 return False
#         except Exception as e:
#             print(f"Failed to drop collection: {e}")
#             return False

#     def list_collections(self) -> List[str]:
#         """List all collections."""
#         if not self.connected:
#             print("Not connected to Milvus. Call connect() first.")
#             return []

#         try:
#             return utility.list_collections()
#         except Exception as e:
#             print(f"Failed to list collections: {e}")
#             return []

#     def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
#         """Get collection information."""
#         if not self.connected:
#             print("Not connected to Milvus. Call connect() first.")
#             return {}

#         try:
#             if not utility.has_collection(collection_name):
#                 print(f"Collection '{collection_name}' does not exist.")
#                 return {}

#             collection = Collection(name=collection_name)

#             return {
#                 "name": collection.name,
#                 "description": collection.description,
#                 "num_entities": collection.num_entities,
#                 "fields": [field.to_dict() for field in collection.schema.fields],
#             }
#         except Exception as e:
#             print(f"Failed to get collection info: {e}")
#             return {}

#     def __enter__(self):
#         """Support for context manager."""
#         self.connect()
#         return self

#     def __exit__(self, exc_type, exc_val, exc_tb):
#         """Ensure disconnect when using with statement."""
#         self.disconnect()
