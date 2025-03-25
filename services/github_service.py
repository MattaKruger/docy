from typing import Dict, Optional

from github import Github, Auth
from github.Repository import Repository
from github.ContentFile import ContentFile
from github.GithubException import UnknownObjectException

from pydantic import BaseModel

from logger import github_logger as logger

from settings import Settings


settings = Settings()


class RepoDocs(BaseModel):
    """
    Structured output for repository documentation extraction.
    """

    readme_content: Optional[str] = None
    docs_content: Dict[str, str] = {}
    error: Optional[str] = None


class GithubService:
    """Service for interacting with the GitHub API. Fetch docs and readme content. Saves to ChromaDB."""

    def __init__(self):
        github_access_token = settings.GITHUB_ACCESS_TOKEN
        auth = None
        if github_access_token:
            auth = Auth.Token(github_access_token)
        self.client = Github(auth=auth)

    def _extract_readme(self, repo: Repository) -> str | None:
        """Helper function to extract README content."""
        try:
            readme = repo.get_readme()
            # latest_release = repo.get_latest_release()
            return readme.decoded_content.decode("utf-8")
        except UnknownObjectException:
            return None
        except Exception as e:
            logger.info(f"Warning: Error fetching README for {repo.full_name}: {e}")
            return None

    def _process_content_file(self, content_file: ContentFile, docs_content: Dict[str, str]) -> None:
        """Helper function to process a single content file."""
        if content_file.name.lower().endswith((".md", ".mdx", ".txt", ".rst", ".py")):
            try:
                file_content = content_file.decoded_content.decode("utf-8")

                docs_content[content_file.path] = file_content
            except Exception as e:
                logger.info(f"Warning: Error decoding content of {content_file.path}: {e}")
        else:
            logger.info(f"Skipping non-text document in docs path: {content_file.path}")

    def _extract_docs_from_path(self, repo: Repository, docs_path: str) -> Dict[str, str]:
        """Helper function to recursively extract documentation content from a given path."""
        docs_content: Dict[str, str] = {}
        try:
            contents = repo.get_contents(docs_path)
            if isinstance(contents, list):
                for content_file in contents:
                    if content_file.type == "file":
                        self._process_content_file(content_file, docs_content)
                    elif content_file.type == "dir":
                        logger.info(f"Entering subdirectory: {content_file.path}")
                        docs_content.update(self._extract_docs_from_path(repo, content_file.path))
            elif isinstance(contents, ContentFile):
                self._process_content_file(contents, docs_content)
            else:
                logger.info(f"Warning: Unexpected content type at {docs_path} in {repo.full_name}")

        except UnknownObjectException:
            logger.info(f"Info: No '{docs_path}' found in {repo.full_name}")
        except Exception as e:
            logger.info(f"Warning: Error accessing '{docs_path}' in {repo.full_name}: {e}")
        return docs_content

    # TODO remove chroma_client deps

    # def extract_repo_docs(self, collection_name: str, repo_name: str, docs_path: Optional[str] = "docs") -> RepoDocs:
    # 	"""
    # 	Extracts README and documentation content from a GitHub repository and stores docs in ChromaDB.
    # 	Recursively extracts docs from the given path.
    # 	Checks if repo docs already exist in ChromaDB before extraction.

    # 	Args:
    # 	    repo_name (str): The full name of the repository (e.g., "user/repo").
    # 	    docs_path (Optional[str]): The path to the documentation directory within the repository.
    # 	                                    Defaults to 'docs'. If None, no docs are extracted.

    # 	Returns:
    # 	    RepoDocs: A structured object containing README content and documentation content.
    # 	"""
    # 	g = self.client

    # 	try:
    # 		repo: Repository = g.get_repo(repo_name)
    # 	except UnknownObjectException:
    # 		return RepoDocs(
    # 			readme_content=None,
    # 			docs_content={},
    # 			error=f"Repository '{repo_name}' not found.",
    # 		)
    # 	except Exception as e:
    # 		return RepoDocs(
    # 			readme_content=None,
    # 			docs_content={},
    # 			error=f"Error accessing repository: {e}",
    # 		)

    # 	query_results = self.chroma_service.get_documents(
    # 		collection_name=collection_name,
    # 		where_filter={
    # 			"$and": [
    # 				{"repo_name": repo_name},
    # 				{"docs_path": docs_path if docs_path else "readme_only"},
    # 			]
    # 		},
    # 		limit=1,
    # 	)
    # 	if query_results["ids"]:
    # 		logger.info(
    # 			f"Docs for repo '{repo_name}' and path '{docs_path}' already exist in ChromaDB. Skipping extraction."
    # 		)
    # 		return RepoDocs(
    # 			readme_content=None,
    # 			docs_content={},
    # 			error="Docs already exist in vector store.",
    # 		)

    # 	readme_content = self._extract_readme(repo)
    # 	docs_content: Dict[str, str] = {}
    # 	if docs_path:
    # 		docs_content = self._extract_docs_from_path(repo, docs_path)

    # 	if docs_content or readme_content:
    # 		ids = list(docs_content.keys()) if docs_content else ["readme"]
    # 		documents = list(docs_content.values()) if docs_content else [readme_content] if readme_content else []
    # 		if docs_path:
    # 			metadata_docs = [{"repo_name": repo_name, "doc_path": path, "docs_path": docs_path} for path in ids]
    # 		else:
    # 			metadata_docs = (
    # 				[
    # 					{
    # 						"repo_name": repo_name,
    # 						"doc_path": "readme",
    # 						"docs_path": "readme_only",
    # 					}
    # 				]
    # 				if readme_content
    # 				else []
    # 			)

    # 		metadatas = metadata_docs

    # 		if documents:
    # 			self.chroma_service.add_documents(collection="test", ids=ids, documents=documents, metadatas=metadatas)
    # 			logger.info(
    # 				f"Added {len(documents)} documents to ChromaDB for repo: {repo_name}, path: {docs_path if docs_path else 'readme'}"
    # 			)

    # 	extracted_data = RepoDocs(readme_content=readme_content, docs_content=docs_content, error=None)
    # 	return extracted_data
