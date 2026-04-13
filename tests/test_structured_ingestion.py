"""Tests for iteration 2 structured sample record ingestion."""

from pathlib import Path

from src.modules.document_processor import DocumentProcessor
from src.spatial_rag_engine import SpatialRAGEngine


def test_load_structured_sample_folder():
    """CSV and JSON sample records should expand into multiple documents."""
    processor = DocumentProcessor()
    sample_path = Path(__file__).parent.parent / "data" / "sample_structured_records"

    documents = processor.load_documents(str(sample_path))

    assert len(documents) >= 6
    assert any(doc["path"].endswith("towers.csv#row1") for doc in documents)
    assert any(doc["path"].endswith("observations.json#record1") for doc in documents)
    assert all("metadata" in doc for doc in documents)


def test_query_structured_sample_records():
    """Structured queries should match the new realistic sample records."""
    engine = SpatialRAGEngine()
    sample_path = Path(__file__).parent.parent / "data" / "sample_structured_records"
    engine.add_documents_with_coordinates(str(sample_path))

    result = engine.query_structured(
        query_text="find hotspot towers with insulator issues in R phase",
        coordinates=(28.7041, 77.1025),
        radius_km=2.5,
        top_k=10,
    )

    tower_ids = [item["tower_id"] for item in result["results"]]
    assert "T101" in tower_ids
    assert any(item["hotspot_flag"] for item in result["results"])
    assert result["total_results"] >= 1
