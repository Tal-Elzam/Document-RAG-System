# Tests

This directory contains minimal tests for the RAG system.

## What's Tested

- **TextChunker**: Tests for all three chunking strategies (fixed_size, sentence, paragraph)
- **DocumentProcessor**: Tests for file type detection and error handling
- **Integration**: Tests that different strategies work correctly

## What's NOT Tested (by design)

- API calls to Gemini (requires API key and rate limits)
- Database operations (requires PostgreSQL connection)
- File I/O operations (PDF/DOCX reading)

## Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_index_documents.py

# Run specific test class
pytest tests/test_index_documents.py::TestTextChunker

# Run with coverage (optional)
pytest --cov=index_documents tests/
```

## Test Structure

```
tests/
├── __init__.py          # Package marker
├── test_index_documents.py  # Tests for indexing functions
└── README.md            # This file
```

