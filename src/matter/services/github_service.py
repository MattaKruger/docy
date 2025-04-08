from typing import Dict, Optional

import logfire

from github import Auth, Github
from github.ContentFile import ContentFile
from github.GithubException import UnknownObjectException
from github.Repository import Repository
from pydantic import BaseModel

from matter.core import Settings

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
        except Exception:
            return None

    def _process_content_file(self, content_file: ContentFile, docs_content: Dict[str, str]) -> None:
        """Helper function to process a single content file."""
        if content_file.name.lower().endswith((".md", ".mdx", ".txt", ".rst", ".py")):
            try:
                file_content = content_file.decoded_content.decode("utf-8")

                docs_content[content_file.path] = file_content
            except Exception as e:
                logfire.info(f"Warning: Error decoding content of {content_file.path}: {e}")
        else:
            logfire.info(f"Skipping non-text document in docs path: {content_file.path}")

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
                        logfire.info(f"Entering subdirectory: {content_file.path}")
                        docs_content.update(self._extract_docs_from_path(repo, content_file.path))
            elif isinstance(contents, ContentFile):
                self._process_content_file(contents, docs_content)
            else:
                logfire.info(f"Warning: Unexpected content type at {docs_path} in {repo.full_name}")

        except UnknownObjectException:
            logfire.info(f"Info: No '{docs_path}' found in {repo.full_name}")
        except Exception as e:
            logfire.info(f"Warning: Error accessing '{docs_path}' in {repo.full_name}: {e}")
        return docs_content
