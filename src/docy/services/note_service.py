import re
from typing import Optional

from datetime import datetime
from pathlib import Path

import frontmatter
import yaml
from slugify import slugify


class NoteService:
    def __init__(self, vault_path: str):
        """
        Initialize the NoteService with the path to your vault

        Args:
            vault_path (str): The path to your vault directory
        """
        self.vault_path = Path(vault_path)
        if not self.vault_path.exists():
            raise ValueError(f"Vault path does not exist: {vault_path}")

    def get_all_notes(self):
        """
        Get all markdown files in the vault

        Returns:
            list: List of Path objects for all .md files
        """
        return list(self.vault_path.rglob("*.md"))

    def read_note(self, note_path: Path):
        """
        Read the contents of a specific note

        Args:
            note_path (Path or str): Path to the note file

        Returns:
            dict: Dictionary containing note metadata and content
        """
        note_path = Path(note_path)
        try:
            with open(note_path, "r", encoding="utf-8") as file:
                post = frontmatter.load(file)
                return {
                    "title": note_path.stem,
                    "path": str(note_path),
                    "metadata": post.metadata,
                    "content": post.content,
                    "created": datetime.fromtimestamp(note_path.stat().st_ctime),
                    "modified": datetime.fromtimestamp(note_path.stat().st_mtime),
                }
        except Exception as e:
            print(f"Error reading note {note_path}: {e}")
            return None

    def find_links(self, content: str):
        """
        Find all wiki-style links in the note content

        Args:
            content (str): Note content

        Returns:
            list: List of found links
        """
        # Match both [[link]] and [[link|alias]] formats
        wiki_links = re.findall(r"\[\[(.*?)\]\]", content)
        return [link.split("|")[0] for link in wiki_links]

    def search_notes(self, query: str):
        """
        Search through all notes for a specific query

        Args:
            query (str): Search query

        Returns:
            list: List of notes containing the query
        """
        results = []
        for note_path in self.get_all_notes():
            note = self.read_note(note_path)
            if note and query.lower() in note["content"].lower():
                results.append(note)
        return results

    def get_tags(self, content: str):
        """
        Extract tags from note content

        Args:
            content (str): Note content

        Returns:
            list: List of tags found in the note
        """
        return re.findall(r"#(\w+)", content)

    def get_recent_notes(self, limit: int = 10):
        """
        Get the most recently modified notes

        Args:
            limit (int): Number of notes to return

        Returns:
            list: List of recent notes
        """
        notes = [(note_path, note_path.stat().st_mtime) for note_path in self.get_all_notes()]
        notes.sort(key=lambda x: x[1], reverse=True)
        return [self.read_note(note_path) for note_path, _ in notes[:limit]]

    def create_note(self, title: str, content: Optional[str] = "", metadata=None, folder=None, template=None):
        """
        Create a new note in the Obsidian vault

        Args:
            title (str): The title of the note
            content (str, optional): The content of the note
            metadata (dict, optional): YAML frontmatter metadata
            folder (str, optional): Subfolder path within the vault
            template (str, optional): Name of template to use

        Returns:
            Path: Path object of the created note
        """
        # Create a filename-safe version of the title
        safe_filename = slugify(title) + ".md"

        # Handle folder path
        if folder:
            note_path = self.vault_path / folder / safe_filename
            # Create folder if it doesn't exist
            note_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            note_path = self.vault_path / safe_filename

        # Initialize default metadata
        default_metadata = {"created": datetime.now().isoformat(), "title": title, "tags": []}

        # Merge with provided metadata
        if metadata:
            default_metadata.update(metadata)

        # Handle template if provided
        if template:
            template_content = self._get_template_content(template)
            if template_content:
                content = template_content.replace("{{title}}", title) + "\n" + content

        # Create the note content with YAML frontmatter
        note_content = "---\n"
        note_content += yaml.dump(default_metadata)
        note_content += "---\n\n"
        note_content += content

        try:
            # Write the file
            with open(note_path, "w", encoding="utf-8") as file:
                file.write(note_content)
            return note_path
        except Exception as e:
            raise Exception(f"Failed to create note: {e}") from e

    def _get_template_content(self, template_name):
        """
        Get content from a template file

        Args:
            template_name (str): Name of the template

        Returns:
            str: Template content or empty string if template not found
        """
        template_dir = self.vault_path / "templates"
        template_path = template_dir / f"{template_name}.md"

        if template_path.exists():
            with open(template_path, "r", encoding="utf-8") as file:
                return file.read()
        return ""

    def update_note(self, note_path, content=None, metadata=None):
        """
        Update an existing note

        Args:
            note_path (Path or str): Path to the note
            content (str, optional): New content
            metadata (dict, optional): New metadata to merge

        Returns:
            bool: True if successful, False otherwise
        """
        note_path = Path(note_path)
        if not note_path.exists():
            raise FileNotFoundError(f"Note not found: {note_path}")

        try:
            with open(note_path, "r", encoding="utf-8") as file:
                post = frontmatter.load(file)

            # Update metadata if provided
            if metadata:
                post.metadata.update(metadata)

            # Update content if provided
            if content is not None:
                post.content = content

            # Write back to file
            with open(note_path, "w", encoding="utf-8") as file:
                file.write(frontmatter.dumps(post))
            return True
        except Exception as e:
            print(f"Error updating note {note_path}: {e}")
            return False


if __name__ == "__main__":
    # Initialize the service with your vault path
    vault_path = "../../Notes/main"
    obsidian_service = NoteService(vault_path)

    # Get all notes
    all_notes = obsidian_service.get_all_notes()
    print(f"Total notes found: {len(all_notes)}")

    # # Read a specific note
    # if all_notes:
    #     first_note = obsidian_service.read_note(all_notes[0])
    #     print("\nFirst note:")
    #     print(f"Title: {first_note['title']}")
    #     print(f"Created: {first_note['created']}")
    #     print(f"Modified: {first_note['modified']}")

    # # Search for notes containing a specific term
    # search_results = obsidian_service.search_notes("python")
    # print(f"\nFound {len(search_results)} notes containing 'python'")

    # # Get recent notes
    recent_notes = obsidian_service.get_recent_notes(5)
    print("\nRecent notes:")
    for note in recent_notes:
        if note is not None:
            print(f"- {note['title']}")
