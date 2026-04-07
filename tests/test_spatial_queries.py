#!/usr/bin/env python3
"""
Test script for Spatial RAG query functionality
Tests the query_spatial and retrieve functionality
"""

import sys
import json
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


def test_spatial_query():
    """Test 1: Basic spatial query"""
    logger.info("=" * 80)
    logger.info("TEST 1: Basic Spatial Query")
    logger.info("=" * 80)
    
    engine = SpatialRAGEngine()
    sample_docs_path = "data/sample_documents"
    
    # Load documents
    try:
        num_docs = engine.add_documents_with_coordinates(
            path=sample_docs_path,
            coordinates=(28.7041, 77.1025)
        )
        logger.info(f"✓ Loaded {num_docs} documents")
    except Exception as e:
        logger.error(f"✗ Failed to load documents: {e}")
        return False
    
    # Perform spatial query
    try:
        query_coords = (28.7041, 77.1025)  # Tower T001 location
        result = engine.query_spatial(
            query_text="fault risks and maintenance concerns",
            coordinates=query_coords,
            radius_km=1.0,
            top_k=5
        )
        logger.info("✓ Spatial query executed successfully")
    except Exception as e:
        logger.error(f"✗ Query failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Display results
    logger.info(f"\nQuery Location: {query_coords}")
    logger.info(f"Search Radius: 1.0 km")
    logger.info(f"Total Results: {result.get('total_results', 0)}")
    
    logger.info("\nRetrieved Documents:")
    logger.info("-" * 80)
    
    for i, doc in enumerate(result.get('retrieved_documents', []), 1):
        logger.info(
            f"{i}. Distance: {doc['distance_km']:6.2f} km | "
            f"Relevance: {doc['relevance_score']:.3f} | "
            f"Content preview: {doc['content'][:60]}..."
        )
    
    logger.info("\nNearby Towers:")
    logger.info("-" * 80)
    
    nearby_towers = result.get('nearby_towers', [])
    if nearby_towers:
        for tower in nearby_towers:
            logger.info(
                f"  • Tower {tower['tower_id']:10} | "
                f"Distance: {tower['distance_km']:6.2f} km"
            )
    else:
        logger.warning("  No nearby towers found")
    
    logger.info("\n✓ TEST 1 PASSED: Spatial query successful")
    return True


def test_different_radii():
    """Test 2: Query with different search radii"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 2: Queries with Different Search Radii")
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
    
    query_coords = (28.7041, 77.1025)
    radii = [0.5, 1.0, 2.0, 5.0]
    
    logger.info(f"\nQuery: 'corrosion maintenance' at {query_coords}")
    logger.info("-" * 80)
    logger.info(f"{'Radius (km)':15} {'Documents Found':20} {'Avg Distance (km)':20}")
    logger.info("-" * 80)
    
    for radius in radii:
        try:
            result = engine.query_spatial(
                query_text="corrosion and maintenance",
                coordinates=query_coords,
                radius_km=radius,
                top_k=5
            )
            
            docs = result.get('retrieved_documents', [])
            if docs:
                avg_distance = sum(d['distance_km'] for d in docs) / len(docs)
            else:
                avg_distance = 0
            
            num_results = len(docs)
            logger.info(f"{radius:15.1f} {num_results:20} {avg_distance:20.2f}")
        except Exception as e:
            logger.error(f"✗ Query failed for radius {radius}km: {e}")
            return False
    
    logger.info("\n✓ TEST 2 PASSED: Multi-radius queries successful")
    return True


def test_different_locations():
    """Test 3: Query from different locations"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 3: Queries from Different Locations")
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
    
    # Different query locations (tower coordinates)
    test_locations = {
        "Tower T001": (28.7041, 77.1025),
        "Tower T002": (28.7082, 77.1042),
        "Tower T003": (28.7001, 77.1009),
        "Tower T004": (28.7082, 77.1103),
    }
    
    logger.info("\nQuery: 'insulator condition and testing' from different locations")
    logger.info("-" * 80)
    logger.info(f"{'Location':20} {'Coordinates':30} {'Results Found':15}")
    logger.info("-" * 80)
    
    for location_name, coords in test_locations.items():
        try:
            result = engine.query_spatial(
                query_text="insulator condition and testing",
                coordinates=coords,
                radius_km=1.0,
                top_k=5
            )
            
            num_results = result.get('total_results', 0)
            logger.info(f"{location_name:20} {str(coords):30} {num_results:15}")
        except Exception as e:
            logger.error(f"✗ Query failed for {location_name}: {e}")
            return False
    
    logger.info("\n✓ TEST 3 PASSED: Location-based queries successful")
    return True


def test_response_generation():
    """Test 4: Response generation"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 4: Response Generation")
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
    
    test_queries = [
        ("What are the fault risks?", (28.7041, 77.1025), 1.0),
        ("Which towers need maintenance?", (28.7082, 77.1042), 2.0),
        ("What is the structural condition?", (28.7001, 77.1009), 1.0),
    ]
    
    logger.info("\nGenerated Responses:")
    logger.info("-" * 80)
    
    for query, coords, radius in test_queries:
        try:
            response = engine.generate_response(
                query_text=query,
                coordinates=coords,
                radius_km=radius
            )
            
            logger.info(f"\nQuery: {query}")
            logger.info(f"Location: {coords} (radius: {radius}km)")
            logger.info("-" * 40)
            
            # Display first 300 chars of response
            response_preview = response[:300] + "..." if len(response) > 300 else response
            logger.info(response_preview)
        except Exception as e:
            logger.error(f"✗ Response generation failed: {e}")
            return False
    
    logger.info("\n✓ TEST 4 PASSED: Response generation successful")
    return True


def test_edge_cases():
    """Test 5: Edge cases and boundary conditions"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 5: Edge Cases and Boundary Conditions")
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
    
    test_cases = [
        ("Empty query", "", (28.7041, 77.1025), 1.0),
        ("Very small radius", "fault", (28.7041, 77.1025), 0.1),
        ("Very large radius", "maintenance", (28.7041, 77.1025), 100.0),
        ("Far away location", "tower", (28.0, 76.0), 1.0),
        ("Very specific query", "ceramic disk insulator degradation", (28.7041, 77.1025), 2.0),
    ]
    
    logger.info("\nTesting Edge Cases:")
    logger.info("-" * 80)
    
    for case_name, query, coords, radius in test_cases:
        try:
            result = engine.query_spatial(
                query_text=query,
                coordinates=coords,
                radius_km=radius,
                top_k=3
            )
            
            num_results = result.get('total_results', 0)
            logger.info(
                f"✓ {case_name:35} | "
                f"Results: {num_results:2} | "
                f"Query: '{query[:20]}...'"
            )
        except Exception as e:
            logger.warning(f"⚠ {case_name:35} | Error: {str(e)[:50]}")
    
    logger.info("\n✓ TEST 5 PASSED: Edge cases handled")
    return True


def main():
    """Run all query tests"""
    logger.info("\n" + "=" * 80)
    logger.info("SPATIAL RAG - QUERY TEST SUITE")
    logger.info("=" * 80 + "\n")
    
    tests = [
        ("Basic Spatial Query", test_spatial_query),
        ("Different Search Radii", test_different_radii),
        ("Different Locations", test_different_locations),
        ("Response Generation", test_response_generation),
        ("Edge Cases", test_edge_cases),
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
    logger.info("QUERY TEST SUMMARY")
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
