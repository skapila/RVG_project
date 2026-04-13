"""Test modules for RVG Project"""

import pytest
from src.config import Config
from src.modules.document_processor import DocumentProcessor
from src.modules.vector_generator import VectorGenerator
from src.modules.retrieval_engine import RetrievalEngine


class TestDocumentProcessor:
    """Test DocumentProcessor"""

    def test_initialization(self):
        """Test processor initialization"""
        processor = DocumentProcessor()
        assert processor is not None
        assert processor.SUPPORTED_FORMATS == {
            ".txt", ".pdf", ".docx", ".md", ".csv", ".json"
        }

    def test_load_documents(self):
        """Test document loading"""
        processor = DocumentProcessor()
        # Placeholder test
        documents = processor.load_documents(".")
        assert isinstance(documents, list)


class TestVectorGenerator:
    """Test VectorGenerator"""

    def test_initialization(self):
        """Test generator initialization"""
        generator = VectorGenerator()
        assert generator is not None
        assert generator.model_name == Config.EMBEDDING_MODEL

    def test_generate_vectors(self):
        """Test vector generation"""
        generator = VectorGenerator()
        documents = [{"path": "test.txt", "content": "Test content"}]
        vectors = generator.generate_vectors(documents)
        assert len(vectors) == 1
        assert "embedding" in vectors[0]


class TestRetrievalEngine:
    """Test RetrievalEngine"""

    def test_initialization(self):
        """Test engine initialization"""
        engine = RetrievalEngine()
        assert engine is not None
        assert engine.vectors == []

    def test_store_and_retrieve(self):
        """Test storing and retrieving vectors"""
        engine = RetrievalEngine()
        vectors = [{"id": 1, "content": "Test"}]
        engine.store_vectors(vectors)
        assert len(engine.vectors) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
