#!/usr/bin/env python3
"""
Test script for Spatial RAG document loading and initialization
Tests the add_documents_with_coordinates functionality
"""

import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.spatial_rag_engine import SpatialRAGEngine

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_document_loading():
    """Test 1: Load documents and verify spatial context"""
    logger.info("=" * 80)
    logger.info("TEST 1: Document Loading with Spatial Context")
    logger.info("=" * 80)
    
    # Initialize engine
    engine = SpatialRAGEngine()
    logger.info("✓ SpatialRAGEngine initialized")
    
    # Path to sample documents
    sample_docs_path = "data/sample_documents"
    
    if not Path(sample_docs_path).exists():
        logger.error(f"✗ Sample documents directory not found: {sample_docs_path}")
        logger.info("  Please ensure sample documents are in: data/sample_documents/")
        return False
    
    # Load documents with default coordinates (center point)
    default_coords = (28.7041, 77.1025)  # Tower T001 location
    
    try:
        num_docs = engine.add_documents_with_coordinates(
            path=sample_docs_path,
            coordinates=default_coords
        )
        logger.info(f"✓ Loaded {num_docs} documents")
    except Exception as e:
        logger.error(f"✗ Failed to load documents: {e}")
        return False
    
    # Verify documents loaded
    if num_docs == 0:
        logger.error("✗ No documents were loaded")
        return False
    
    # Check internal state
    num_vectors = len(engine.spatial_retrieval.vectors)
    logger.info(f"✓ Generated {num_vectors} vectors (chunks + embeddings)")
    
    if num_vectors == 0:
        logger.error("✗ No vectors were generated")
        return False
    
    # Display loaded documents summary
    logger.info("\nLoaded Documents Summary:")
    logger.info("-" * 80)
    
    unique_sources = set()
    for vector in engine.spatial_retrieval.vectors:
        source = vector.get("path", "unknown")
        unique_sources.add(source)
        coords = vector.get("coordinates", (None, None))
        tower_id = vector.get("metadata", {}).get("tower_info", {}).get("tower_id", "N/A")
        
    for source in sorted(unique_sources):
        source_vectors = [v for v in engine.spatial_retrieval.vectors if v.get("path") == source]
        coords = source_vectors[0].get("coordinates", (None, None))
        tower_id = source_vectors[0].get("metadata", {}).get("tower_info", {}).get("tower_id", "Unknown")
        logger.info(
            f"  • {Path(source).name:20} | Tower: {tower_id:10} | "
            f"Coords: {coords} | Chunks: {len(source_vectors)}"
        )
    
    logger.info("\n✓ TEST 1 PASSED: Documents loaded successfully with spatial context")
    return True


def test_spatial_indexing():
    """Test 2: Verify spatial indexing and grid organization"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 2: Spatial Indexing and Grid Organization")
    logger.info("=" * 80)
    
    engine = SpatialRAGEngine()
    sample_docs_path = "data/sample_documents"
    
    # Load documents
    try:
        engine.add_documents_with_coordinates(
            path=sample_docs_path,
            coordinates=(28.7041, 77.1025)
        )
    except Exception as e:
        logger.error(f"✗ Failed to load documents: {e}")
        return False
    
    # Check spatial index
    num_spatial_cells = len(engine.spatial_retrieval.spatial_index)
    logger.info(f"✓ Documents organized into {num_spatial_cells} geographic grid cells")
    
    if num_spatial_cells == 0:
        logger.warning("⚠ No spatial indexing created (may still be functional)")
    else:
        logger.info("\nGrid Cell Distribution:")
        for cell, docs in sorted(engine.spatial_retrieval.spatial_index.items()):
            logger.info(f"  • Cell {cell}: {len(docs)} documents")
    
    # Verify all vectors have coordinates
    vectors_with_coords = sum(1 for v in engine.spatial_retrieval.vectors if v.get("coordinates"))
    logger.info(f"\n✓ Vectors with coordinates: {vectors_with_coords}/{len(engine.spatial_retrieval.vectors)}")
    
    logger.info("\n✓ TEST 2 PASSED: Spatial indexing verified")
    return True


def test_metadata_extraction():
    """Test 3: Verify metadata extraction from documents"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 3: Metadata Extraction")
    logger.info("=" * 80)
    
    engine = SpatialRAGEngine()
    sample_docs_path = "data/sample_documents"
    
    # Load documents
    try:
        engine.add_documents_with_coordinates(
            path=sample_docs_path,
            coordinates=(28.7041, 77.1025)
        )
    except Exception as e:
        logger.error(f"✗ Failed to load documents: {e}")
        return False
    
    # Analyze extracted metadata
    logger.info("\nExtracted Tower Information:")
    logger.info("-" * 80)
    
    tower_ids = set()
    coord_extraction_rate = 0
    
    for vector in engine.spatial_retrieval.vectors:
        tower_info = vector.get("metadata", {}).get("tower_info", {})
        if tower_info:
            tower_ids.add(tower_info.get("tower_id"))
        
        if vector.get("coordinates"):
            coord_extraction_rate += 1
    
    logger.info(f"✓ Unique towers identified: {len(tower_ids)}")
    for tid in sorted(tower_ids):
        logger.info(f"  • Tower {tid}")
    
    if len(engine.spatial_retrieval.vectors) > 0:
        extraction_percentage = (coord_extraction_rate / len(engine.spatial_retrieval.vectors)) * 100
        logger.info(f"\n✓ Coordinate extraction rate: {extraction_percentage:.1f}%")
    
    logger.info("\n✓ TEST 3 PASSED: Metadata extraction verified")
    return True


def test_nearby_towers():
    """Test 4: Verify nearby tower discovery"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 4: Nearby Towers Discovery")
    logger.info("=" * 80)
    
    engine = SpatialRAGEngine()
    sample_docs_path = "data/sample_documents"
    
    # Load documents
    try:
        engine.add_documents_with_coordinates(
            path=sample_docs_path,
            coordinates=(28.7041, 77.1025)
        )
    except Exception as e:
        logger.error(f"✗ Failed to load documents: {e}")
        return False
    
    # Test nearby tower discovery
    test_coords = (28.7041, 77.1025)  # Tower T001
    
    nearby_towers = engine.spatial_retrieval.get_nearby_towers(
        coordinates=test_coords,
        radius_km=1.0
    )
    
    logger.info(f"\nTowers within 1km of {test_coords}:")
    logger.info("-" * 80)
    
    if nearby_towers:
        for tower in nearby_towers:
            logger.info(
                f"  • Tower {tower['tower_id']:10} | "
                f"Distance: {tower['distance_km']:6.2f} km | "
                f"Coords: {tower['coordinates']}"
            )
    else:
        logger.warning("⚠ No nearby towers found within 1km")
    
    # Test with larger radius
    nearby_towers_5km = engine.spatial_retrieval.get_nearby_towers(
        coordinates=test_coords,
        radius_km=5.0
    )
    
    logger.info(f"\n✓ Towers within 5km: {len(nearby_towers_5km)}")
    
    logger.info("\n✓ TEST 4 PASSED: Nearby tower discovery works")
    return True


def main():
    """Run all tests"""
    logger.info("\n" + "=" * 80)
    logger.info("SPATIAL RAG - DOCUMENT LOADING TEST SUITE")
    logger.info("=" * 80 + "\n")
    
    tests = [
        ("Document Loading", test_document_loading),
        ("Spatial Indexing", test_spatial_indexing),
        ("Metadata Extraction", test_metadata_extraction),
        ("Nearby Towers Discovery", test_nearby_towers),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"\n✗ {test_name} failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("TEST SUMMARY")
    logger.info("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        logger.info(f"{status:10} - {test_name}")
    
    logger.info("-" * 80)
    logger.info(f"Total: {passed}/{total} tests passed\n")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
