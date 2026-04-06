"""Main RAG Engine module"""

import logging
from src.config import Config
from src.modules.document_processor import DocumentProcessor
from src.modules.vector_generator import VectorGenerator
from src.modules.retrieval_engine import RetrievalEngine

# Setup logging
logging.basicConfig(level=Config.LOG_LEVEL)
logger = logging.getLogger(__name__)


class RAGEngine:
    """Retrieval-Augmented Generation Engine"""

    def __init__(self):
        """Initialize RAG Engine components"""
        logger.info(f"Initializing {Config.PROJECT_NAME}")
        self.doc_processor = DocumentProcessor()
        self.vector_generator = VectorGenerator()
        self.retrieval_engine = RetrievalEngine()

    def add_documents(self, path):
        """Add documents to the system"""
        logger.info(f"Processing documents from: {path}")
        documents = self.doc_processor.load_documents(path)
        vectors = self.vector_generator.generate_vectors(documents)
        self.retrieval_engine.store_vectors(vectors)
        logger.info(f"Added {len(documents)} documents")

    def query(self, query_text):
        """Query the RAG system"""
        logger.info(f"Processing query: {query_text}")
        retrieved_docs = self.retrieval_engine.retrieve(query_text)
        response = self.retrieval_engine.generate_response(query_text, retrieved_docs)
        return response

    def __repr__(self):
        return f"RAGEngine(project={Config.PROJECT_NAME})"


if __name__ == "__main__":
    engine = RAGEngine()
    print(engine)
