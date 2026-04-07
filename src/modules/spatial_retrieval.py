"""Spatial retrieval engine for location-aware document retrieval"""

import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from math import radians, cos, sin, asin, sqrt

logger = logging.getLogger(__name__)


@dataclass
class SpatialResult:
    """Result from spatial retrieval query"""
    content: str
    coordinates: Tuple[float, float]
    distance_km: float
    relevance_score: float
    metadata: Dict
    source_id: str


class SpatialRetrievalEngine:
    """Retrieves documents based on spatial proximity and semantic relevance"""

    def __init__(self):
        """Initialize SpatialRetrievalEngine"""
        logger.info("SpatialRetrievalEngine initialized")
        self.vectors = []
        self.spatial_index = {}  # cell -> documents

    def haversine_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """
        Calculate distance between two coordinates in kilometers
        
        Args:
            lat1, lon1: First coordinate
            lat2, lon2: Second coordinate
            
        Returns:
            Distance in kilometers
        """
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        km = 6371 * c  # Earth radius in kilometers
        
        return km

    def spatial_filter(
        self,
        query_coords: Tuple[float, float],
        radius_km: float = 5.0
    ) -> List[Dict]:
        """
        Filter vectors by geographic proximity
        
        Args:
            query_coords: (latitude, longitude)
            radius_km: Search radius in kilometers
            
        Returns:
            List of documents within radius
        """
        nearby_docs = []
        query_lat, query_lon = query_coords
        
        for vector in self.vectors:
            if not vector.get("coordinates"):
                continue
            
            doc_lat, doc_lon = vector["coordinates"]
            distance = self.haversine_distance(
                query_lat, query_lon,
                doc_lat, doc_lon
            )
            
            if distance <= radius_km:
                vector_copy = vector.copy()
                vector_copy["distance_km"] = distance
                nearby_docs.append(vector_copy)
        
        # Sort by distance
        nearby_docs.sort(key=lambda x: x.get("distance_km", float('inf')))
        
        logger.info(f"Spatial filter found {len(nearby_docs)} documents within {radius_km}km")
        return nearby_docs

    def semantic_rank(
        self,
        query_embedding: List[float],
        candidates: List[Dict]
    ) -> List[Dict]:
        """
        Rank candidates by semantic similarity
        
        Args:
            query_embedding: Query vector
            candidates: Candidate documents with embeddings
            
        Returns:
            Ranked documents with relevance scores
        """
        ranked = []
        
        for candidate in candidates:
            doc_embedding = candidate.get("embedding", [])
            
            # Cosine similarity
            score = self._cosine_similarity(query_embedding, doc_embedding)
            
            candidate_copy = candidate.copy()
            candidate_copy["relevance_score"] = score
            ranked.append(candidate_copy)
        
        # Sort by relevance
        ranked.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        return ranked

    @staticmethod
    def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity between two vectors"""
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a ** 2 for a in vec1) ** 0.5
        norm2 = sum(b ** 2 for b in vec2) ** 0.5
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)

    def retrieve_spatial(
        self,
        query_coords: Tuple[float, float],
        query_embedding: List[float],
        radius_km: float = 5.0,
        top_k: int = 5
    ) -> List[SpatialResult]:
        """
        Multi-stage spatial + semantic retrieval
        
        Args:
            query_coords: Query location
            query_embedding: Query vector
            radius_km: Spatial search radius
            top_k: Number of results to return
            
        Returns:
            Top-k spatial results with rankings
        """
        # Stage 1: Spatial filtering
        spatial_candidates = self.spatial_filter(query_coords, radius_km)
        
        if not spatial_candidates:
            logger.warning("No documents found within search radius")
            return []
        
        # Stage 2: Semantic ranking
        ranked = self.semantic_rank(query_embedding, spatial_candidates)
        
        # Stage 3: Combine signals (distance + relevance)
        results = []
        for i, doc in enumerate(ranked[:top_k]):
            result = SpatialResult(
                content=doc.get("content", ""),
                coordinates=doc.get("coordinates", (0, 0)),
                distance_km=doc.get("distance_km", 0),
                relevance_score=doc.get("relevance_score", 0),
                metadata=doc.get("metadata", {}),
                source_id=doc.get("id", f"doc_{i}")
            )
            results.append(result)
        
        logger.info(f"Retrieved {len(results)} spatial results")
        return results

    def store_spatial_vectors(self, vectors: List[Dict]) -> None:
        """
        Store vectors with spatial indexing
        
        Args:
            vectors: List of vectors with coordinates
        """
        self.vectors.extend(vectors)
        
        # Build spatial index (simple grid)
        for vector in vectors:
            coords = vector.get("coordinates")
            if coords:
                cell = (round(coords[0]), round(coords[1]))
                if cell not in self.spatial_index:
                    self.spatial_index[cell] = []
                self.spatial_index[cell].append(vector)
        
        logger.info(f"Stored {len(vectors)} spatial vectors")

    def get_nearby_towers(
        self,
        coordinates: Tuple[float, float],
        radius_km: float = 5.0
    ) -> List[Dict]:
        """
        Get towers near a location
        
        Args:
            coordinates: Query coordinates
            radius_km: Search radius
            
        Returns:
            List of nearby towers
        """
        nearby = []
        lat, lon = coordinates
        
        for vector in self.vectors:
            if "tower_id" in vector.get("metadata", {}):
                vector_coords = vector.get("coordinates")
                if vector_coords:
                    distance = self.haversine_distance(
                        lat, lon,
                        vector_coords[0], vector_coords[1]
                    )
                    
                    if distance <= radius_km:
                        nearby.append({
                            "tower_id": vector["metadata"]["tower_id"],
                            "coordinates": vector_coords,
                            "distance_km": distance,
                            "metadata": vector.get("metadata", {})
                        })
        
        nearby.sort(key=lambda x: x["distance_km"])
        
        logger.info(f"Found {len(nearby)} nearby towers within {radius_km}km")
        return nearby
