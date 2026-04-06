"""Document processing module for RVG Project"""

import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Handles document loading and preprocessing"""

    SUPPORTED_FORMATS = {".txt", ".pdf", ".docx", ".md"}

    def __init__(self):
        """Initialize DocumentProcessor"""
        logger.info("DocumentProcessor initialized")

    def load_documents(self, path):
        """Load documents from a given path"""
        documents = []
        path = Path(path)

        if path.is_file():
            documents.append(self._load_single_document(path))
        elif path.is_dir():
            for file_path in path.rglob("*"):
                if file_path.is_file() and file_path.suffix in self.SUPPORTED_FORMATS:
                    documents.append(self._load_single_document(file_path))

        logger.info(f"Loaded {len(documents)} documents")
        return documents

    def _load_single_document(self, file_path):
        """Load a single document"""
        file_path = Path(file_path)
        logger.debug(f"Loading: {file_path}")

        try:
            if file_path.suffix == ".txt":
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
            elif file_path.suffix == ".md":
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
            else:
                content = f"Content from {file_path.name}"

            return {"path": str(file_path), "content": content}
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            return None

    def preprocess(self, documents):
        """Preprocess documents"""
        processed = []
        for doc in documents:
            if doc:
                # Remove extra whitespace
                content = " ".join(doc["content"].split())
                processed.append({"path": doc["path"], "content": content})
        return processed
