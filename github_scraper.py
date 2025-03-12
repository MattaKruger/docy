# import os

# from github import Github, Auth, ContentFile, Repository
# from github.Repository import Repository
# from github.GithubException import UnknownObjectException
# from github.ContentFile import ContentFile
# from logger import github_logger as logger
# from sqlmodel import Session
# from models.model import Repository as DBRepository, ReadmeChunk, DocFile, DocChunk, ExampleFile, ExampleChunk


# class GithubScraper:
#     def __init__(self, access_token):
#         self.access_token = os.getenv("GITHUB_ACCESS_TOKEN", "")
#         auth = Auth.Token(self.access_token)
#         self.client = Github(auth=auth)

#     def _extract_readme(self, repo: Repository) -> str | None:
#         """Helper function to extract README content."""
#         try:
#             readme = repo.get_readme()
#             return readme.decoded_content.decode("utf-8")
#         except UnknownObjectException:
#             return None
#         except Exception as e:
#             logger.info(f"Warning: Error fetching README for {repo.full_name}: {e}")
#             return None

#     def _chunk_text(self, text, chunk_size=1000, chunk_overlap=200):
#         """
#         Split text into overlapping chunks of a specified size.

#         Args:
#             text (str): The text to be chunked
#             chunk_size (int): Maximum size of each chunk
#             chunk_overlap (int): Overlap between consecutive chunks

#         Returns:
#             list: List of text chunks
#         """
#         if not text:
#             return []

#         chunks = []
#         start = 0
#         text_length = len(text)

#         while start < text_length:
#             # Get a chunk of size chunk_size or the remaining text
#             end = min(start + chunk_size, text_length)

#             # If we're not at the end of the text, try to break at a natural boundary
#             if end < text_length:
#                 # Look for a newline or period within the last 100 characters of the chunk
#                 look_back = min(100, chunk_size // 4)
#                 break_point = text.rfind("\n", end - look_back, end)

#                 if break_point == -1:  # No newline found
#                     break_point = text.rfind(". ", end - look_back, end)
#                     if break_point != -1:
#                         break_point += 2  # Include the period and space

#                 if break_point != -1:
#                     end = break_point

#             # Extract the chunk and add to the list
#             chunks.append(text[start:end])

#             # Move the start position for the next chunk, considering overlap
#             start = end - chunk_overlap if end < text_length else text_length

#         return chunks

#     def scrape_repository(self, repo_url: str, chunk_size=1000, chunk_overlap=200, apply_chunking=True):
#         """
#         Scrape a GitHub repository for its README, examples, and documentation folders.

#         Args:
#             repo_url (str): The full repository URL or owner/repo path
#             chunk_size (int): Maximum size of each content chunk when chunking is applied
#             chunk_overlap (int): Overlap between consecutive chunks when chunking is applied
#             apply_chunking (bool): Whether to chunk the content or return it as is

#         Returns:
#             dict: Repository data including README content and files from examples/docs folders
#         """
#         try:
#             repo = self.client.get_repo(repo_url)
#             logger.info(f"Successfully accessed repository: {repo.full_name}")

#             # Extract README content
#             readme_content = self._extract_readme(repo)

#             # Chunk the README if needed
#             if apply_chunking and readme_content:
#                 readme_chunks = self._chunk_text(readme_content, chunk_size, chunk_overlap)
#                 readme_data = {"content": readme_content, "chunks": readme_chunks}
#             else:
#                 readme_data = readme_content

#             # Extract basic repo information
#             repo_data = {
#                 "name": repo.name,
#                 "full_name": repo.full_name,
#                 "description": repo.description,
#                 "stars": repo.stargazers_count,
#                 "forks": repo.forks_count,
#                 "readme": readme_data,
#                 "examples": [],
#                 "docs": [],
#             }

#             # Look for examples folder
#             try:
#                 examples_contents = repo.get_contents("examples")
#                 if isinstance(examples_contents, list):  # It's a directory
#                     for content in examples_contents:
#                         if content.type == "file":
#                             try:
#                                 file_content = content.decoded_content.decode("utf-8")
#                                 file_data = {"name": content.name, "path": content.path, "content": file_content}

#                                 # Add chunked content if needed
#                                 if apply_chunking:
#                                     file_data["chunks"] = self._chunk_text(file_content, chunk_size, chunk_overlap)

#                                 repo_data["examples"].append(file_data)
#                                 logger.info(f"Found example file: {content.path}")
#                             except Exception as e:
#                                 logger.info(f"Error decoding content for {content.path}: {e}")
#             except UnknownObjectException:
#                 logger.info(f"No examples folder found in {repo.full_name}")
#             except Exception as e:
#                 logger.info(f"Error accessing examples folder in {repo.full_name}: {e}")

#             # Look for docs or documentation folder
#             for docs_folder in ["docs", "doc", "documentation", "Documentation"]:
#                 try:
#                     docs_contents = repo.get_contents(docs_folder)
#                     if isinstance(docs_contents, list):  # It's a directory
#                         for content in docs_contents:
#                             if content.type == "file":
#                                 try:
#                                     file_content = content.decoded_content.decode("utf-8")
#                                     file_data = {"name": content.name, "path": content.path, "content": file_content}

#                                     # Add chunked content if needed
#                                     if apply_chunking:
#                                         file_data["chunks"] = self._chunk_text(file_content, chunk_size, chunk_overlap)

#                                     repo_data["docs"].append(file_data)
#                                     logger.info(f"Found documentation file: {content.path}")
#                                 except Exception as e:
#                                     logger.info(f"Error decoding content for {content.path}: {e}")
#                         # We found one docs folder, no need to check others
#                         break
#                 except UnknownObjectException:
#                     continue  # Try the next possible docs folder name
#                 except Exception as e:
#                     logger.info(f"Error accessing {docs_folder} folder in {repo.full_name}: {e}")

#             return repo_data

#         except UnknownObjectException:
#             logger.info(f"Repository not found: {repo_url}")
#             return None
#         except Exception as e:
#             logger.info(f"Error scraping repository {repo_url}: {e}")
#             return None

#     def save_repository_to_db(self, repo_data: dict, session: Session, generate_embedding_fn=None):
#         """
#         Save repository data to the database.

#         Args:
#             repo_data (dict): Repository data from scrape_repository
#             session (Session): SQLModel database session
#             generate_embedding_fn (callable): Function to generate embeddings for text

#         Returns:
#             DBRepository: Saved repository record
#         """
#         # Check if repository already exists
#         existing_repo = session.query(DBRepository).filter(DBRepository.full_name == repo_data["full_name"]).first()

#         if existing_repo:
#             # Update existing repository
#             db_repo = existing_repo
#             db_repo.name = repo_data["name"]
#             db_repo.description = repo_data["description"]
#             db_repo.stars = repo_data["stars"]
#             db_repo.forks = repo_data["forks"]

#             # Update readme if it's a simple string
#             if not isinstance(repo_data["readme"], dict):
#                 db_repo.readme = repo_data["readme"]

#             # Clear existing chunks to avoid duplicates
#             session.query(ReadmeChunk).filter(ReadmeChunk.repository_id == db_repo.id).delete()
#             session.query(DocFile).filter(DocFile.repository_id == db_repo.id).delete()
#             session.query(ExampleFile).filter(ExampleFile.repository_id == db_repo.id).delete()
#         else:
#             # Create new repository record
#             db_repo = DBRepository(
#                 name=repo_data["name"],
#                 full_name=repo_data["full_name"],
#                 description=repo_data["description"],
#                 stars=repo_data["stars"],
#                 forks=repo_data["forks"],
#                 readme=repo_data["readme"]["content"] if isinstance(repo_data["readme"], dict) else repo_data["readme"],
#             )
#             session.add(db_repo)
#             session.flush()  # Flush to get the ID

#         # Save README chunks if they exist
#         if isinstance(repo_data["readme"], dict) and "chunks" in repo_data["readme"]:
#             for i, chunk_text in enumerate(repo_data["readme"]["chunks"]):
#                 embedding = None
#                 if generate_embedding_fn:
#                     embedding = generate_embedding_fn(chunk_text)

#                 chunk = ReadmeChunk(
#                     repository_id=db_repo.id,
#                     content=chunk_text,
#                     chunk_index=i,
#                     embedding=embedding.tolist() if embedding is not None else None,
#                 )
#                 session.add(chunk)

#         # Save documentation files and chunks
#         for doc_data in repo_data["docs"]:
#             doc_file = DocFile(
#                 repository_id=db_repo.id, name=doc_data["name"], path=doc_data["path"], content=doc_data["content"]
#             )
#             session.add(doc_file)
#             session.flush()  # Flush to get the doc_file ID

#             # Save doc chunks if they exist
#             if "chunks" in doc_data:
#                 for i, chunk_text in enumerate(doc_data["chunks"]):
#                     embedding = None
#                     if generate_embedding_fn:
#                         embedding = generate_embedding_fn(chunk_text)

#                     chunk = DocChunk(
#                         doc_file_id=doc_file.id,
#                         content=chunk_text,
#                         chunk_index=i,
#                         embedding=embedding.tolist() if embedding is not None else None,
#                     )
#                     session.add(chunk)

#         # Save example files and chunks
#         for example_data in repo_data["examples"]:
#             example_file = ExampleFile(
#                 repository_id=db_repo.id,
#                 name=example_data["name"],
#                 path=example_data["path"],
#                 content=example_data["content"],
#             )
#             session.add(example_file)
#             session.flush()  # Flush to get the example_file ID

#             # Save example chunks if they exist
#             if "chunks" in example_data:
#                 for i, chunk_text in enumerate(example_data["chunks"]):
#                     embedding = None
#                     if generate_embedding_fn:
#                         embedding = generate_embedding_fn(chunk_text)

#                     chunk = ExampleChunk(
#                         example_file_id=example_file.id,
#                         content=chunk_text,
#                         chunk_index=i,
#                         embedding=embedding.tolist() if embedding is not None else None,
#                     )
#                     session.add(chunk)

#         # Commit all changes to the database
#         session.commit()
#         session.refresh(db_repo)
#         return db_repo
