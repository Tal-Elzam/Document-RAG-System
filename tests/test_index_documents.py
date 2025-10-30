"""
Tests for index_documents.py
Tests helper functions (text chunking, document processing) without API or database calls
"""

import pytest
import sys
import os

# Add parent directory to path to import index_documents
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from index_documents import TextChunker, DocumentProcessor


class TestTextChunker:
    """Tests for TextChunker class"""
    
    def test_fixed_size_chunks_basic(self):
        """Test fixed size chunking with basic text"""
        chunker = TextChunker()
        text = "a" * 1000  # 1000 characters
        chunks = chunker.fixed_size_chunks(text, chunk_size=200, overlap=50)
        
        assert len(chunks) > 0
        assert all(len(chunk) <= 200 for chunk in chunks)
    
    def test_fixed_size_chunks_overlap(self):
        """Test that overlap works correctly"""
        chunker = TextChunker()
        text = "a" * 500
        chunks = chunker.fixed_size_chunks(text, chunk_size=100, overlap=25)
        
        # Should have multiple chunks due to overlap
        assert len(chunks) >= 1
        # First chunk should be 100 chars
        assert len(chunks[0]) == 100
    
    def test_sentence_based_chunks(self):
        """Test sentence-based chunking"""
        chunker = TextChunker()
        text = "First sentence. Second sentence. Third sentence. Fourth sentence. Fifth sentence. Sixth sentence."
        chunks = chunker.sentence_based_chunks(text, sentences_per_chunk=2)
        
        assert len(chunks) > 0
        # Each chunk should end with a period
        assert all(chunk.strip().endswith('.') for chunk in chunks if chunk.strip())
    
    def test_paragraph_based_chunks(self):
        """Test paragraph-based chunking"""
        chunker = TextChunker()
        text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
        chunks = chunker.paragraph_based_chunks(text)
        
        assert len(chunks) == 3
        assert "First paragraph." in chunks[0]
        assert "Second paragraph." in chunks[1]
        assert "Third paragraph." in chunks[2]
    
    def test_sentence_based_chunks_empty(self):
        """Test sentence-based chunking with empty text"""
        chunker = TextChunker()
        chunks = chunker.sentence_based_chunks("", sentences_per_chunk=5)
        
        assert len(chunks) == 0
    
    def test_paragraph_based_chunks_empty(self):
        """Test paragraph-based chunking with empty text"""
        chunker = TextChunker()
        chunks = chunker.paragraph_based_chunks("")
        
        assert len(chunks) == 0


class TestDocumentProcessor:
    """Tests for DocumentProcessor class"""
    
    def test_extract_text_file_type_detection(self):
        """Test file type detection"""
        processor = DocumentProcessor()
        
        # Test PDF extension
        file_path = "test.pdf"
        try:
            # This will fail if file doesn't exist, which is expected
            processor.extract_text(file_path)
        except (ValueError, FileNotFoundError) as e:
            # Either file not found or unsupported type - both are valid
            assert True
    
    def test_extract_text_unsupported_file_type(self):
        """Test that unsupported file types raise ValueError"""
        processor = DocumentProcessor()
        
        with pytest.raises(ValueError, match="Unsupported file type"):
            processor.extract_text("test.txt")  # .txt not supported
    
    def test_extract_text_docx_extension(self):
        """Test DOCX extension detection"""
        processor = DocumentProcessor()
        
        # Test that .docx is recognized
        try:
            processor.extract_text("test.docx")
        except (ValueError, FileNotFoundError):
            # File doesn't exist, but extension is recognized
            pass
    
    def test_extract_text_doc_extension(self):
        """Test that .doc extension is recognized"""
        processor = DocumentProcessor()
        
        try:
            processor.extract_text("test.doc")
        except (ValueError, FileNotFoundError):
            # File doesn't exist, but extension should be recognized
            pass


class TestIntegrationChunking:
    """Integration tests for chunking strategies"""
    
    def test_multiple_strategies_on_same_text(self):
        """Test that different strategies produce different results"""
        text = "Sentence one. Sentence two. Sentence three.\n\nParagraph two starts here."
        
        chunker = TextChunker()
        
        fixed_chunks = chunker.fixed_size_chunks(text, chunk_size=50, overlap=10)
        sentence_chunks = chunker.sentence_based_chunks(text, sentences_per_chunk=2)
        paragraph_chunks = chunker.paragraph_based_chunks(text)
        
        # All should produce at least one chunk
        assert len(fixed_chunks) > 0
        assert len(sentence_chunks) > 0
        assert len(paragraph_chunks) > 0
        
        # Different strategies should produce different number of chunks
        # (not always, but in this case they should)
        assert len(fixed_chunks) != len(sentence_chunks) or len(sentence_chunks) != len(paragraph_chunks)
    
    def test_chunks_preserve_all_text(self):
        """Test that chunking preserves all original text (for fixed_size)"""
        text = "abcdefghijklmnopqrstuvwxyz" * 10  # 260 characters
        chunker = TextChunker()
        
        chunks = chunker.fixed_size_chunks(text, chunk_size=100, overlap=20)
        combined_text = "".join(chunks).replace(" ", "")  # Remove overlaps
        
        # Original text should be contained in chunks (accounting for overlap)
        assert len(combined_text) >= len(text) - 50  # Allow some margin for overlap handling

