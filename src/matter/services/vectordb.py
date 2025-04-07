import re
from abc import ABC, abstractmethod
from typing import Dict, List

import numpy as np
from sentence_transformers import SentenceTransformer


class SimpleMarkdownParser:
    def parse(self, content: str) -> List[Dict]:
        sections = []
        current_section = {"header": None, "content": []}

        for line in content.split("\n"):
            header_match = re.match(r"^(#+)\s*(.*)", line)
            if header_match:
                if current_section["content"]:
                    sections.append(current_section)
                current_section = {"header": header_match.group(2).strip(), "content": []}
            else:
                if line.strip():
                    current_section["content"].append(line.strip())

        if current_section["content"]:
            sections.append(current_section)

        return sections


class EmbeddingModel:
    """Handles text embedding generation"""

    def __init__(self, model_name: str = "all-MiniLM-l6-v2"):
        self.model = SentenceTransformer(model_name)

    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        return self.model.encode(texts, convert_to_tensor=False)


class VectorDBInterface(ABC):
    """Abstract base class for vector database operations"""

    @abstractmethod
    def insert(self, vectors: np.ndarray, metadata: List[Dict]):
        """Insert vectors with metadata into the database"""
        pass

    @abstractmethod
    def search(self, query: str, k: int = 5):
        """Search the database for similar vectors"""
        pass
