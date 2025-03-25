from typing import Optional, List

from pydantic import BaseModel, Field


class CollectionMetadata(BaseModel):
    language: Optional[str] = Field(default="Python", description="The programming language used in the documents")
    library_name: Optional[str] = Field(default="", description="Name of the library/framework/package")
    library_version: Optional[str] = Field(default="", description="Version of the library")
    documentation_version: Optional[str] = Field(default="", description="Version of the documentation")
    official_website: Optional[str] = Field(default="", description="Official website of the library/package")
    repository_url: Optional[str] = Field(default="", description="URL of the source code repository")
    license_type: Optional[str] = Field(default="", description="License type (MIT, Apache, etc.)")
    embedding_model: Optional[str] = Field(default="", description="Model used to generate embeddings")
    chunk_strategy: Optional[str] = Field(default="", description="Strategy used for chunking the documents")


class DocumentMetadata(BaseModel):
    category: str = Field(default="default", description="Category of document, can be anything.")
    description: str = Field(default="main entry point for fastapi", description="The description of the document.")
    source: Optional[str] = Field(default="github", description="The source of the documents.")
    doc_extension: Optional[str] = Field(default=".md", description="The extension of the documents.")

    title: Optional[str] = Field(default="", description="Title of the document")
    path_in_repo: Optional[str] = Field(default="", description="Path to the document in repository")
    document_type: Optional[str] = Field(
        default="", description="Type of document (API reference, tutorial, guide, example, etc.)"
    )
    section: Optional[str] = Field(
        default="", description="Section within overall documentation (e.g. 'Advanced Usage')"
    )

    # Content-specific metadata
    api_class: Optional[str] = Field(default="", description="Class name for class documentation")
    api_function: Optional[str] = Field(default="", description="Function/method name for function documentation")
    api_module: Optional[str] = Field(default="", description="Module name for module documentation")

    # Content characteristics
    has_code_examples: Optional[bool] = Field(default=False, description="Whether the document contains code examples")
    has_diagrams: Optional[bool] = Field(default=False, description="Whether the document contains diagrams")
    complexity_level: Optional[str] = Field(
        default="", description="Difficulty level (beginner, intermediate, advanced)"
    )

    # Versioning and updates
    version_specific: Optional[bool] = Field(
        default=False, description="Whether content is specific to a particular version"
    )
    last_updated: Optional[str] = Field(default="", description="When the document was last updated")

    # Searchability enhancers
    keywords: Optional[str] = Field(default="", description="Key terms for this document")
    related_docs: Optional[str] = Field(default="", description="Related documentation files")


class DocumentQuery(BaseModel):
    texts: List[str] = Field(default_factory=list)
    language: str = Field(default="")
    category: str = Field(default="")
