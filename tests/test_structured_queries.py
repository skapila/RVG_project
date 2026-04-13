"""Tests for MVP structured tower retrieval."""

from pathlib import Path

from src.modules.spatial_processor import SpatialMetadataExtractor
from src.spatial_rag_engine import SpatialRAGEngine


SAMPLE_DOC = Path(__file__).parent.parent / "data" / "sample_documents" / "tower_002.txt"


def test_extract_structured_fields():
    """Structured metadata should be normalized from tower text."""
    text = SAMPLE_DOC.read_text(encoding="utf-8")

    metadata = SpatialMetadataExtractor.extract_structured_fields(text)

    assert metadata["tower_id"] == "T002"
    assert metadata["line_name"] == "Delhi-Gurgaon 220kV Main Line"
    assert metadata["severity"] == "high"
    assert "insulator" in metadata["component_types"]
    assert "corrosion" in metadata["defect_types"]
    assert "B" in metadata["phases"]
    assert metadata["inspection_date"] == "2024-03-05T00:00:00"


def test_parse_query_filters():
    """The MVP query parser should infer structured filters from text."""
    filters = SpatialMetadataExtractor.parse_query_filters(
        "Find high risk towers with insulator issues in B phase"
    )

    assert filters["severity"] == "high"
    assert filters["component_type"] == "insulator"
    assert filters["phase"] == "B"


def test_query_structured_with_filters():
    """Structured query should combine exact filters with radius search."""
    engine = SpatialRAGEngine()
    sample_docs_path = Path(__file__).parent.parent / "data" / "sample_documents"
    engine.add_documents_with_coordinates(str(sample_docs_path))

    result = engine.query_structured(
        query_text="Find high risk towers with insulator issues in B phase",
        coordinates=(28.7082, 77.1042),
        radius_km=1.0,
        top_k=5,
    )

    assert result["total_results"] >= 1
    assert result["results"][0]["tower_id"] == "T002"
    assert result["results"][0]["severity"] == "high"
    assert result["results"][0]["distance_km"] is not None
