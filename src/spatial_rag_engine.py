"""Enhanced RAG Engine with spatial capabilities"""

import logging
from typing import Tuple, Optional, List, Dict
from src.config import Config
from src.modules.document_processor import DocumentProcessor
from src.modules.vector_generator import VectorGenerator
from src.modules.spatial_processor import SpatialChunker, SpatialMetadataExtractor
from src.modules.spatial_retrieval import SpatialRetrievalEngine

# Setup logging
logging.basicConfig(level=Config.LOG_LEVEL)
logger = logging.getLogger(__name__)


class SpatialRAGEngine:
    """Retrieval-Augmented Generation Engine with Spatial Capabilities"""

    def __init__(self):
        """Initialize Spatial RAG Engine components"""
        logger.info(f"Initializing {Config.PROJECT_NAME} with Spatial RAG")
        self.doc_processor = DocumentProcessor()
        self.vector_generator = VectorGenerator()
        self.spatial_retrieval = SpatialRetrievalEngine()
        self.spatial_chunker = SpatialChunker()
        self.metadata_extractor = SpatialMetadataExtractor()

    def add_documents_with_coordinates(
        self,
        path: str,
        coordinates: Optional[Tuple[float, float]] = None
    ) -> int:
        """
        Add documents with spatial context
        
        Args:
            path: Path to documents
            coordinates: Optional default coordinates
            
        Returns:
            Number of documents added
        """
        logger.info(f"Processing documents from: {path}")
        
        # Load documents
        documents = self.doc_processor.load_documents(path)
        
        if not documents:
            logger.warning("No documents loaded")
            return 0
        
        # Process with spatial context
        processed_vectors = []
        
        for doc in documents:
            if not doc:
                continue
            
            # Extract coordinates from document if available
            doc_coords = self.metadata_extractor.extract_coordinates(
                doc.get("content", "")
            ) or coordinates
            
            # Extract tower/line metadata
            tower_info = self.metadata_extractor.extract_tower_info(
                doc.get("content", "")
            )
            
            # Chunk with spatial context
            chunks = self.spatial_chunker.chunk_document(
                content=doc.get("content", ""),
                coordinates=doc_coords,
                metadata={"tower_info": tower_info, "source": doc.get("path")}
            )
            
            # Generate vectors
            for chunk in chunks:
                vector = {
                    "id": f"{doc.get('path')}_{chunk['position']}",
                    "path": doc.get("path"),
                    "content": chunk["content"],
                    "coordinates": chunk["coordinates"],
                    "metadata": chunk["metadata"],
                    "embedding": self.vector_generator._generate_embedding(
                        chunk["content"]
                    )
                }
                processed_vectors.append(vector)
        
        # Store in spatial retrieval engine
        self.spatial_retrieval.store_spatial_vectors(processed_vectors)
        
        logger.info(f"Added {len(documents)} documents with spatial context")
        return len(documents)

    def query_spatial(
        self,
        query_text: str,
        coordinates: Tuple[float, float],
        radius_km: float = 5.0,
        top_k: int = 5
    ) -> Dict:
        """
        Query with spatial context
        
        Args:
            query_text: Query string
            coordinates: (latitude, longitude)
            radius_km: Search radius
            top_k: Number of results
            
        Returns:
            Query results with spatial context
        """
        logger.info(
            f"Spatial query at {coordinates}: {query_text} "
            f"(radius: {radius_km}km)"
        )
        
        # Generate query embedding
        query_embedding = self.vector_generator._generate_embedding(query_text)
        
        # Retrieve with spatial awareness
        spatial_results = self.spatial_retrieval.retrieve_spatial(
            query_coords=coordinates,
            query_embedding=query_embedding,
            radius_km=radius_km,
            top_k=top_k
        )
        
        # Get nearby towers for additional context
        nearby_towers = self.spatial_retrieval.get_nearby_towers(
            coordinates, radius_km
        )
        
        result = {
            "query": query_text,
            "location": {"latitude": coordinates[0], "longitude": coordinates[1]},
            "search_radius_km": radius_km,
            "retrieved_documents": [
                {
                    "content": r.content[:200],
                    "coordinates": r.coordinates,
                    "distance_km": round(r.distance_km, 2),
                    "relevance_score": round(r.relevance_score, 3),
                    "source_id": r.source_id
                }
                for r in spatial_results
            ],
            "nearby_towers": nearby_towers,
            "total_results": len(spatial_results)
        }
        
        return result

    def generate_response(
        self,
        query_text: str,
        coordinates: Tuple[float, float],
        radius_km: float = 5.0
    ) -> str:
        """
        Generate response based on spatial query
        
        Args:
            query_text: User query
            coordinates: Query location
            radius_km: Search radius
            
        Returns:
            Generated response
        """
        # Get spatial query results
        query_result = self.query_spatial(
            query_text, coordinates, radius_km
        )
        
        # Format context for LLM
        context = self._format_spatial_context(query_result)
        
        # Generate response (placeholder for LLM integration)
        response = (
            f"Based on spatial analysis at {coordinates} "
            f"(radius: {radius_km}km):\n\n"
            f"{context}\n\n"
            f"Query: {query_text}"
        )
        
        return response

    @staticmethod
    def _format_spatial_context(query_result: Dict) -> str:
        """Format spatial context for LLM"""
        lines = ["Spatial Context:"]
        
        if query_result["nearby_towers"]:
            lines.append(f"Nearby Towers ({len(query_result['nearby_towers'])}):")
            for tower in query_result["nearby_towers"][:3]:
                lines.append(
                    f"  - {tower.get('tower_id', 'Unknown')} "
                    f"({tower['distance_km']:.1f} km away)"
                )
        
        if query_result["retrieved_documents"]:
            lines.append(f"\nTop Documents ({len(query_result['retrieved_documents'])}):")
            for doc in query_result["retrieved_documents"][:3]:
                lines.append(
                    f"  - Distance: {doc['distance_km']:.1f} km, "
                    f"Relevance: {doc['relevance_score']}"
                )
        
        return "\n".join(lines)

    def __repr__(self):
        return f"SpatialRAGEngine(project={Config.PROJECT_NAME})"


if __name__ == "__main__":
    engine = SpatialRAGEngine()
    print(engine)
    
    # Example usage:
    # coordinates = (28.7041, 77.1025)  # Delhi, India example
    # engine.add_documents_with_coordinates("path/to/docs", coordinates)
    # result = engine.query_spatial(
    #     "What are fault risks?",
    #     coordinates,
    #     radius_km=5
    # )
