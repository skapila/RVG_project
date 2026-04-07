# Spatial RAG Testing & Production Guide

## Overview

This guide explains how to test the Spatial RAG system in a production environment after providing document paths.

---

## Quick Start

### Prerequisites
```bash
# Ensure you're in the project directory
cd /path/to/RVG_project

# Install dependencies (if not already done)
pip install -r requirements.txt
```

### Run All Tests (30 seconds)
```bash
# Run document loading tests
python tests/test_document_loading.py

# Run query tests
python tests/test_spatial_queries.py
```

---

## Sample Data Provided

The project includes **4 realistic transmission tower documents** with:
- Tower specifications and design
- Maintenance history and inspection reports
- Fault history and incidents
- Geographic coordinates
- Adjacent tower references
- Risk assessments

**Location:** `data/sample_documents/`

**Files:**
- `tower_001.txt` - Tower T001 at coordinates (28.7041, 77.1025)
- `tower_002.txt` - Tower T002 at coordinates (28.7082, 77.1042)
- `tower_003.txt` - Tower T003 at coordinates (28.7001, 77.1009)
- `tower_004.txt` - Tower T004 at coordinates (28.7082, 77.1103)

---

## Test Suite 1: Document Loading (`test_document_loading.py`)

### What It Tests
1. **Document Loading:** Loads all documents from `data/sample_documents/`
2. **Spatial Context:** Extracts coordinates and tower information
3. **Chunking:** Splits documents into semantic chunks
4. **Embedding Generation:** Converts chunks to vector embeddings
5. **Spatial Indexing:** Organizes documents by geographic location

### Run Test
```bash
python tests/test_document_loading.py
```

### Expected Output
```
TEST 1: Document Loading with Spatial Context
✓ SpatialRAGEngine initialized
✓ Loaded 4 documents
✓ Generated 32 vectors (chunks + embeddings)

Loaded Documents Summary:
  • tower_001.txt         | Tower: 001        | Coords: (28.7041, 77.1025) | Chunks: 8
  • tower_002.txt         | Tower: 002        | Coords: (28.7082, 77.1042) | Chunks: 8
  • tower_003.txt         | Tower: 003        | Coords: (28.7001, 77.1009) | Chunks: 8
  • tower_004.txt         | Tower: 004        | Coords: (28.7082, 77.1103) | Chunks: 8

✓ TEST 1 PASSED: Documents loaded successfully
```

### What Each Test Does

**Test 1: Document Loading**
- Initializes the SpatialRAGEngine
- Loads documents from `data/sample_documents/`
- Verifies coordinate extraction
- Displays summary of loaded documents

**Test 2: Spatial Indexing**
- Checks spatial grid organization
- Displays geographic distribution of documents
- Verifies all vectors have coordinates

**Test 3: Metadata Extraction**
- Identifies unique towers from documents
- Calculates coordinate extraction rate
- Displays tower information

**Test 4: Nearby Towers Discovery**
- Tests tower proximity queries
- Finds towers within 1km and 5km radius
- Displays distance calculations

---

## Test Suite 2: Query & Retrieval (`test_spatial_queries.py`)

### What It Tests
1. **Spatial Queries:** Retrieve documents near a location
2. **Multi-Radius Queries:** Test different search radiuses (0.5km, 1km, 2km, 5km)
3. **Location-Based Queries:** Query from different tower locations
4. **Response Generation:** Format results for LLM
5. **Edge Cases:** Handle boundary conditions

### Run Test
```bash
python tests/test_spatial_queries.py
```

### Expected Output
```
TEST 1: Basic Spatial Query
✓ Loaded 4 documents
✓ Spatial query executed successfully

Query Location: (28.7041, 77.1025)
Search Radius: 1.0 km
Total Results: 8

Retrieved Documents:
1. Distance:   0.05 km | Relevance: 0.945 | Content preview: Tower T001 at 28.7041, 77.1025...
2. Distance:   0.28 km | Relevance: 0.892 | Content preview: Adjacent Tower T002 is located...
3. Distance:   0.25 km | Relevance: 0.756 | Content preview: Tower location and specifications...
...
```

### What Each Test Does

**Test 1: Basic Spatial Query**
- Executes a query from Tower T001 location
- Retrieves nearby documents within 1km
- Displays distance and relevance scores

**Test 2: Multi-Radius Queries**
- Tests the same query with radii: 0.5km, 1km, 2km, 5km
- Shows how results change with search radius
- Displays document count and average distance

**Test 3: Location-Based Queries**
- Executes identical query from each tower location
- Demonstrates how results vary by location
- Tests spatial awareness of the system

**Test 4: Response Generation**
- Generates natural language responses
- Combines retrieved documents with spatial context
- Shows formatted output ready for LLM

**Test 5: Edge Cases**
- Tests empty queries
- Tests very small/large radiuses
- Tests queries from far away
- Tests specific domain queries

---

## Using Your Own Documents

### Step 1: Prepare Your Documents
Create text files in `data/sample_documents/` with content like:

```
Tower T005
Location: Tower_005
Coordinates: 28.7142, 77.1103
Transmission Line: Delhi-Gurgaon 220kV Main Line

[Document content with coordinates, tower ID, maintenance info, etc.]
```

### Step 2: Load Documents
```python
from src.spatial_rag_engine import SpatialRAGEngine

# Initialize engine
engine = SpatialRAGEngine()

# Load your documents
num_docs = engine.add_documents_with_coordinates(
    path="data/sample_documents",
    coordinates=(28.7041, 77.1025)  # Default location
)

print(f"Loaded {num_docs} documents")
```

### Step 3: Test Loading
```bash
python tests/test_document_loading.py
```

### Step 4: Query Your Data
```python
# Query with spatial context
result = engine.query_spatial(
    query_text="fault risks and maintenance",
    coordinates=(28.7041, 77.1025),
    radius_km=5.0,
    top_k=5
)

# Generate response
response = engine.generate_response(
    query_text="What are the risks?",
    coordinates=(28.7041, 77.1025),
    radius_km=5.0
)

print(response)
```

---

## Production Workflow

### Phase 1: Setup (5 minutes)
```bash
# Navigate to project
cd /home/om/Desktop/RAG_based_project/RVG_project

# Verify structure
ls -la data/sample_documents/

# Install dependencies (if needed)
pip install -r requirements.txt
```

### Phase 2: Load & Test (2 minutes)
```bash
# Run document loading tests
python tests/test_document_loading.py

# Expected: All 4 tests PASSED
```

### Phase 3: Query Testing (3 minutes)
```bash
# Run query and retrieval tests
python tests/test_spatial_queries.py

# Expected: All 5 tests PASSED
```

### Phase 4: Custom Testing (varies)
```bash
# Write custom test script (optional)
# Or use interactive Python shell:

python3 << 'EOF'
from src.spatial_rag_engine import SpatialRAGEngine

engine = SpatialRAGEngine()
engine.add_documents_with_coordinates("data/sample_documents")

# Your queries here
result = engine.query_spatial(
    "Your question",
    (28.7041, 77.1025),
    radius_km=5.0
)

for doc in result['retrieved_documents']:
    print(f"Distance: {doc['distance_km']:.2f}km, Relevance: {doc['relevance_score']:.3f}")
EOF
```

---

## Understanding Results

### Distance Metrics
- **Distance (km):** Real-world distance from query location (uses Haversine formula)
- **Relevance Score:** Semantic similarity to query (0.0 = unrelated, 1.0 = perfect match)

### Result Examples

```
Distance: 0.05 km, Relevance: 0.945
↓
- Document is 50 meters away (very close)
- Content matches query meaning very well (94.5% similarity)
```

```
Distance: 3.20 km, Relevance: 0.756
↓
- Document is 3.2 kilometers away
- Content has moderate relevance to query (75.6% similarity)
```

---

## Troubleshooting

### Issue: "No documents found"
**Solution:**
```bash
# Check if sample documents exist
ls -la data/sample_documents/

# If missing, they should have been created
# Verify file contents
head -20 data/sample_documents/tower_001.txt
```

### Issue: "Import error for SpatialRAGEngine"
**Solution:**
```bash
# Ensure you're in the correct directory
pwd

# Should output: .../RVG_project

# Run from correct location
cd /home/om/Desktop/RAG_based_project/RVG_project
python tests/test_document_loading.py
```

### Issue: "pytest not found"
**Solution:**
```bash
# Install test dependencies
pip install pytest pytest-cov

# Then run tests
python tests/test_document_loading.py
```

### Issue: Low relevance scores
**Explanation:**
- The embedding model is a placeholder (MD5-based)
- In production, use real embedding models (BERT, OpenAI, etc.)
- Current scores are based on content hashing

---

## Next Steps for Production

### 1. Integrate Real Embeddings
```python
# Replace placeholder embeddings with:
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
embedding = model.encode(text)
```

### 2. Add Database
```python
# Replace in-memory storage with:
# - PostgreSQL + PostGIS (spatial)
# - Pinecone (vector search)
# - MongoDB (document storage)
```

### 3. Integrate LLM
```python
# Replace response generation with:
from openai import OpenAI

client = OpenAI(api_key="your_key")
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": context}]
)
```

### 4. Deploy API
```bash
# Use FastAPI or Flask
pip install fastapi uvicorn

# Create api.py with endpoints
# Run: uvicorn api:app --reload
```

---

## Document Path Format

When using your own documents, structure them as:

```
data/sample_documents/
├── tower_001.txt          ← File with coordinates in content
├── tower_002.txt
├── my_tower_docs/
│   ├── tower_a.txt
│   └── tower_b.txt
└── ...
```

**Important:** The system recursively searches all subdirectories and expects documents to contain:
- Coordinates (latitude, longitude)
- Tower ID or name
- Relevant content (fault history, specifications, etc.)

---

## Performance Metrics

### Expected Times
- **Document Loading:** < 1 second for 4 files
- **Embedding Generation:** < 2 seconds for 32 chunks
- **Single Query:** < 50ms
- **Nearby Tower Search:** < 10ms

### Memory Usage
- **4 Tower Documents:** ~5-10 MB
- **32 Vector Embeddings:** ~2-3 MB
- **Total:** ~15-20 MB

---

## Success Criteria

✅ **Test passes if:**
- All documents load successfully
- Coordinates are extracted correctly
- Spatial index is created
- Queries return results with distances
- Relevance scores are calculated
- Response generation works

✅ **System is production-ready when:**
- All test suites pass
- Custom documents load correctly
- Queries return expected results
- Response quality is acceptable
- Performance meets requirements

---

## Support & Debugging

### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)

from src.spatial_rag_engine import SpatialRAGEngine
engine = SpatialRAGEngine()  # Shows detailed logs
```

### Inspect Internal State
```python
engine = SpatialRAGEngine()
engine.add_documents_with_coordinates("data/sample_documents")

# Check loaded vectors
print(f"Total vectors: {len(engine.spatial_retrieval.vectors)}")

# Check spatial index
print(f"Grid cells: {len(engine.spatial_retrieval.spatial_index)}")

# Check specific vector
print(engine.spatial_retrieval.vectors[0])
```

---

## Conclusion

The Spatial RAG system is now ready for testing with provided sample documents. Follow the production workflow above to validate the system with your own documents.
