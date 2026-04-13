# Sample Structured Tower Records

This folder contains iteration 2 sample data for structured ingestion.

Files:
- `towers.csv`: tower-level records with normalized retrieval fields
- `observations.json`: richer observation-style records with notes, thermal values, and image paths

Use this folder with:

```python
from src.spatial_rag_engine import SpatialRAGEngine

engine = SpatialRAGEngine()
engine.add_documents_with_coordinates("data/sample_structured_records")

result = engine.query_structured(
    query_text="find hotspot towers with insulator issues in R phase",
    coordinates=(28.7041, 77.1025),
    radius_km=2.0,
)
```
