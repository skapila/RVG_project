"""Tests for spatial RAG components"""

import pytest
from src.modules.spatial_processor import SpatialChunker, SpatialMetadataExtractor
from src.modules.spatial_retrieval import SpatialRetrievalEngine


class TestSpatialChunker:
    """Test SpatialChunker"""

    def test_initialization(self):
        """Test chunker initialization"""
        chunker = SpatialChunker()
        assert chunker is not None
        assert chunker.chunk_size == 500
        assert chunker.overlap == 50

    def test_chunk_document(self):
        """Test document chunking with spatial metadata"""
        chunker = SpatialChunker()
        content = "This is a test document. " * 50  # Long content
        coords = (28.7041, 77.1025)
        metadata = {"tower_id": "tower_001"}
        
        chunks = chunker.chunk_document(content, coords, metadata)
        
        assert len(chunks) > 0
        assert all("content" in chunk for chunk in chunks)
        assert all(chunk["coordinates"] == coords for chunk in chunks)
        assert all(chunk["metadata"]["tower_id"] == "tower_001" for chunk in chunks)

    def test_chunk_by_region(self):
        """Test regional chunking"""
        chunker = SpatialChunker()
        docs = [
            {"coordinates": (28.7, 77.1), "content": "Tower A"},
            {"coordinates": (28.8, 77.2), "content": "Tower B"},
            {"coordinates": (28.75, 77.15), "content": "Tower C"}
        ]
        
        regional = chunker.chunk_by_region(docs)
        
        assert len(regional) > 0
        assert all(isinstance(key, tuple) for key in regional.keys())


class TestSpatialMetadataExtractor:
    """Test SpatialMetadataExtractor"""

    def test_extract_coordinates(self):
        """Test coordinate extraction"""
        text = "Tower located at 28.7041, 77.1025"
        coords = SpatialMetadataExtractor.extract_coordinates(text)
        
        assert coords is not None
        assert abs(coords[0] - 28.7041) < 0.001
        assert abs(coords[1] - 77.1025) < 0.001

    def test_extract_tower_info(self):
        """Test tower information extraction"""
        text = "Tower_001 on transmission line ABC-123"
        tower_info = SpatialMetadataExtractor.extract_tower_info(text)
        
        assert "tower_id" in tower_info or "line_name" in tower_info

    def test_create_spatial_metadata(self):
        """Test metadata creation"""
        content = "Test document at 28.7041, 77.1025"
        coords = (28.7041, 77.1025)
        
        metadata = SpatialMetadataExtractor.create_spatial_metadata(content, coords)
        
        assert metadata["coordinates"] == coords
        assert metadata["has_spatial_context"] is True
        assert metadata["content_length"] > 0


class TestSpatialRetrievalEngine:
    """Test SpatialRetrievalEngine"""

    def test_initialization(self):
        """Test engine initialization"""
        engine = SpatialRetrievalEngine()
        assert engine is not None
        assert engine.vectors == []

    def test_haversine_distance(self):
        """Test distance calculation"""
        engine = SpatialRetrievalEngine()
        
        # Same point
        dist1 = engine.haversine_distance(28.7, 77.1, 28.7, 77.1)
        assert dist1 < 0.1
        
        # Different points
        dist2 = engine.haversine_distance(28.7, 77.1, 28.8, 77.2)
        assert dist2 > 10  # ~15 km between these points

    def test_spatial_filter(self):
        """Test spatial filtering"""
        engine = SpatialRetrievalEngine()
        
        # Add test vectors
        vectors = [
            {"id": 1, "content": "Tower 1", "coordinates": (28.7, 77.1)},
            {"id": 2, "content": "Tower 2", "coordinates": (28.8, 77.2)},
            {"id": 3, "content": "Tower 3", "coordinates": (35.0, 85.0)},  # Far away
        ]
        engine.store_spatial_vectors(vectors)
        
        # Query near first two towers
        results = engine.spatial_filter((28.75, 77.15), radius_km=50)
        
        assert len(results) >= 2
        assert all(r.get("distance_km") <= 50 for r in results)

    def test_cosine_similarity(self):
        """Test similarity calculation"""
        vec1 = [1, 0, 0]
        vec2 = [1, 0, 0]
        vec3 = [0, 1, 0]
        
        sim1 = SpatialRetrievalEngine._cosine_similarity(vec1, vec2)
        sim2 = SpatialRetrievalEngine._cosine_similarity(vec1, vec3)
        
        assert sim1 > 0.99  # Same vector
        assert abs(sim2) < 0.01  # Orthogonal vectors

    def test_get_nearby_towers(self):
        """Test getting nearby towers"""
        engine = SpatialRetrievalEngine()
        
        vectors = [
            {
                "id": 1,
                "coordinates": (28.7, 77.1),
                "metadata": {"tower_id": "tower_001"}
            },
            {
                "id": 2,
                "coordinates": (28.8, 77.2),
                "metadata": {"tower_id": "tower_002"}
            }
        ]
        engine.store_spatial_vectors(vectors)
        
        nearby = engine.get_nearby_towers((28.75, 77.15), radius_km=50)
        
        assert len(nearby) >= 2
        assert all("tower_id" in t["metadata"] for t in nearby)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
