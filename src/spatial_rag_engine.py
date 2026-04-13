"""Enhanced RAG Engine with spatial capabilities"""

import logging
from datetime import datetime
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
        self.tower_records: List[Dict] = []

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
        self.tower_records = []
        
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
            spatial_metadata = self.metadata_extractor.create_spatial_metadata(
                doc.get("content", ""),
                doc_coords
            )

            self.tower_records.append({
                "source": doc.get("path"),
                "content": doc.get("content", ""),
                "coordinates": doc_coords,
                "embedding": self.vector_generator._generate_embedding(
                    doc.get("content", "")
                ),
                **spatial_metadata,
            })
            
            # Chunk with spatial context
            chunks = self.spatial_chunker.chunk_document(
                content=doc.get("content", ""),
                coordinates=doc_coords,
                metadata={
                    "tower_info": tower_info,
                    "tower_id": spatial_metadata.get("tower_id"),
                    "line_name": spatial_metadata.get("line_name"),
                    "component_types": spatial_metadata.get("component_types", []),
                    "defect_types": spatial_metadata.get("defect_types", []),
                    "phases": spatial_metadata.get("phases", []),
                    "severity": spatial_metadata.get("severity"),
                    "inspection_date": spatial_metadata.get("inspection_date"),
                    "hotspot_flag": spatial_metadata.get("hotspot_flag", False),
                    "condition_summary": spatial_metadata.get("condition_summary", ""),
                    "source": doc.get("path"),
                }
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

    def query_structured(
        self,
        query_text: str = "",
        coordinates: Optional[Tuple[float, float]] = None,
        radius_km: Optional[float] = None,
        filters: Optional[Dict] = None,
        top_k: int = 5
    ) -> Dict:
        """
        Query normalized tower records with filter-first retrieval.

        This first iteration implements the MVP queries from the execution plan:
        hotspot, phase, component, severity, tower id, and location radius.
        """
        applied_filters = filters.copy() if filters else {}
        inferred_filters = self.metadata_extractor.parse_query_filters(query_text)
        applied_filters.update({
            key: value for key, value in inferred_filters.items()
            if key not in applied_filters
        })

        matched = []
        query_embedding = self.vector_generator._generate_embedding(query_text or "tower status")

        for record in self.tower_records:
            if not self._record_matches_filters(record, applied_filters):
                continue

            distance_km = None
            if coordinates and radius_km is not None:
                record_coords = record.get("coordinates")
                if not record_coords:
                    continue
                distance_km = self.spatial_retrieval.haversine_distance(
                    coordinates[0], coordinates[1],
                    record_coords[0], record_coords[1]
                )
                if distance_km > radius_km:
                    continue

            score = self.spatial_retrieval._cosine_similarity(
                query_embedding,
                record.get("embedding", [])
            )
            if record.get("severity") == applied_filters.get("severity"):
                score += 0.05
            if record.get("hotspot_flag") and applied_filters.get("hotspot_flag"):
                score += 0.05

            matched.append({
                "tower_id": record.get("tower_id"),
                "line_name": record.get("line_name"),
                "coordinates": record.get("coordinates"),
                "inspection_date": record.get("inspection_date"),
                "severity": record.get("severity"),
                "hotspot_flag": record.get("hotspot_flag"),
                "component_types": record.get("component_types", []),
                "defect_types": record.get("defect_types", []),
                "phases": record.get("phases", []),
                "condition_summary": record.get("condition_summary", ""),
                "source": record.get("source"),
                "distance_km": round(distance_km, 2) if distance_km is not None else None,
                "match_score": round(score, 3),
            })

        matched.sort(
            key=lambda item: (
                item["distance_km"] if item["distance_km"] is not None else float("inf"),
                -item["match_score"],
            )
        )

        return {
            "query": query_text,
            "applied_filters": applied_filters,
            "location": (
                {"latitude": coordinates[0], "longitude": coordinates[1]}
                if coordinates else None
            ),
            "search_radius_km": radius_km,
            "results": matched[:top_k],
            "total_results": len(matched),
        }

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

    def _record_matches_filters(self, record: Dict, filters: Dict) -> bool:
        """Apply exact structured filters before any ranking."""
        if not filters:
            return True

        if filters.get("tower_id") and record.get("tower_id") != filters["tower_id"]:
            return False

        if filters.get("phase") and filters["phase"] not in record.get("phases", []):
            return False

        if (
            filters.get("component_type")
            and filters["component_type"] not in record.get("component_types", [])
        ):
            return False

        if (
            filters.get("defect_type")
            and filters["defect_type"] not in record.get("defect_types", [])
        ):
            return False

        if filters.get("severity") and record.get("severity") != filters["severity"]:
            return False

        if filters.get("hotspot_flag") and not record.get("hotspot_flag"):
            return False

        date_from = filters.get("date_from")
        if date_from and record.get("inspection_date"):
            try:
                if datetime.fromisoformat(record["inspection_date"]) < datetime.fromisoformat(date_from):
                    return False
            except ValueError:
                return False

        return True

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
