# RVG Project - Retrieval Vector Generation

A Retrieval-Augmented Generation (RAG) based project for advanced document processing, vector storage, and intelligent information retrieval.

## Project Structure

```
RVG_project/
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── main.py
│   └── modules/
│       ├── __init__.py
│       ├── document_processor.py
│       ├── vector_generator.py
│       └── retrieval_engine.py
├── data/
│   ├── documents/
│   └── vectors/
├── tests/
│   ├── __init__.py
│   └── test_modules.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Features

- Document Processing: Load and process various document formats
- Vector Generation: Convert documents to embeddings with spatial context
- Retrieval Engine: Efficient semantic search with spatial filtering
- Spatial RAG: Location-aware retrieval for power transmission infrastructure
- Multi-Modal Embeddings: Text + image + geospatial features
- RAG Integration: Combine retrieval with generative models for domain-specific answers

## Installation

1. Clone or create the project
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```

## Usage

```python
from src.main import RAGEngine

# Initialize the RAG engine
engine = RAGEngine()

# Process documents
engine.add_documents("path/to/documents")

# Retrieve and generate responses
response = engine.query("Your question here")
print(response)
```

## Architecture

For detailed architecture design including spatial RAG components, database design, and query pipeline, see [SPATIAL_RAG_ARCHITECTURE.md](./SPATIAL_RAG_ARCHITECTURE.md).

### Key Components:
- **Spatial Indexing:** Geographic proximity-based retrieval
- **Multi-Stage Retrieval:** Spatial filtering + semantic ranking
- **Temporal Context:** Time-series data and incident history
- **Domain Integration:** Power transmission line analysis

## Development

- Python 3.9+
- See `requirements.txt` for dependencies
- Recommended VS Code settings are available in `.vscode/`

## VS Code Setup

1. Open the project in VS Code.
2. Select the Python interpreter in `.venv` or your environment.
3. Use the `Run Tests` task from `Terminal > Run Task...`.

## Testing

```bash
python -m pytest tests/
```

## Contributing

Follow PEP 8 standards and add tests for new features.
