import os
import sys
import time
from typing import List, Optional
from datetime import datetime
import argparse
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_values
import google.generativeai as genai
import pdfplumber
from docx import Document

"""
Purpose: Processing documents (PDF/DOCX) by: extracting text, chunking, creating embeddings and saving to PostgreSQL database
"""

load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
POSTGRES_URL = os.getenv('POSTGRES_URL')

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not defined in .env file")
if not POSTGRES_URL:
    raise ValueError("POSTGRES_URL not defined in .env file")

genai.configure(api_key=GEMINI_API_KEY)

class TextChunker:
    """Helper class for splitting text into chunks"""
    
    @staticmethod
    def fixed_size_chunks(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Split text into fixed-size chunks with overlap
        
        Args:
            text: Text to split
            chunk_size: Size of each chunk (number of characters)
            overlap: Number of characters for overlap between chunks
            
        Returns:
            List of chunks

        Note: there is also an alteernative other python packages such as: 
        # "tiktoken" - https://github.com/openai/tiktoken
        # "text_splitter" - https://github.com/hwchase17/langchain/blob/master/langchain/text_splitter.py
        """
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap    
            if end >= len(text):
                break
                
        return chunks
    
    @staticmethod
    def sentence_based_chunks(text: str, sentences_per_chunk: int = 5) -> List[str]:
        """
        Split text into chunks based on sentences
        
        Args:
            text: Text to split
            sentences_per_chunk: Number of sentences per chunk
            
        Returns:
            List of chunks
        """
        # Split into sentences
        sentences = text.replace('!', '.').replace('?', '.').split('.')
        sentences = [s.strip() for s in sentences if s.strip()]
        
        chunks = []
        for i in range(0, len(sentences), sentences_per_chunk):
            chunk = '. '.join(sentences[i:i+sentences_per_chunk])
            if chunk:
                chunks.append(chunk + '.')
                
        return chunks
    
    @staticmethod
    def paragraph_based_chunks(text: str) -> List[str]:
        paragraphs = text.split('\n\n')
        chunks = [p.strip() for p in paragraphs if p.strip()]
        return chunks


class DocumentProcessor:
    """Class for processing documents"""
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """extract text from PDF file"""
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            raise ValueError(f"error reading PDF file: {str(e)}")
        return text.strip()
    
    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        """extract text from DOCX file"""
        try:
            doc = Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            raise ValueError(f"error reading DOCX file: {str(e)}")
        return text.strip()
    
    @staticmethod
    def extract_text(file_path: str) -> str:
        """extract text from file (supports PDF and DOCX)"""
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.pdf':
            return DocumentProcessor.extract_text_from_pdf(file_path)
        elif file_ext in ['.docx', '.doc']:
            return DocumentProcessor.extract_text_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}. Only PDF and DOCX are supported")


class EmbeddingGenerator:
    """Class for generating embeddings using Gemini API"""
    @staticmethod
    def generate_embedding(text: str) -> List[float]:
        """
        Generate embedding for text using Gemini API
        
        Args:
            text: Text to generate embedding for
            
        Returns:
            Embedding vector
        """
        try:
            result = genai.embed_content(
                model='models/text-embedding-004',
                content=text,
                task_type="retrieval_document"
            )
            
            return result['embedding']
        except Exception as e:
            raise ValueError(f"error creating embedding: {str(e)}")


class DatabaseManager:
    """Class for managing PostgreSQL database"""
    def __init__(self, postgres_url: str):
        """Initialize database connection"""
        self.conn = psycopg2.connect(postgres_url)
        self.ensure_table_exists()
    
    def ensure_table_exists(self):
        """Ensure table exists in database"""
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS document_chunks (
                    id SERIAL PRIMARY KEY,
                    chunk_text TEXT NOT NULL,
                    embedding REAL[] NOT NULL,
                    filename VARCHAR(255) NOT NULL,
                    split_strategy VARCHAR(50) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            self.conn.commit()
    
    def delete_all_chunks(self):
        """Delete all chunks from database and reset ID sequence"""
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM document_chunks;")
            cur.execute("ALTER SEQUENCE document_chunks_id_seq RESTART WITH 1;")
            self.conn.commit()
    
    def insert_chunks(self, chunks: List[dict]):
        """
        Insert chunks into database
        
        Args:
            chunks: List of chunks, each with chunk_text, embedding, filename, split_strategy
        """
        with self.conn.cursor() as cur:
            values = [
                (
                    c['chunk_text'],
                    c['embedding'],
                    c['filename'],
                    c['split_strategy']
                ) for c in chunks
            ]
            execute_values(
                cur,
                """
                INSERT INTO document_chunks (chunk_text, embedding, filename, split_strategy)
                VALUES %s
                """,
                values
            )
            
            self.conn.commit()
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


def process_document(
    file_path: str,
    split_strategy: str = 'fixed_size',
    chunk_size: int = 1000,
    overlap: int = 200,
    sentences_per_chunk: int = 5
):
    """
    Process complete document: extract text, chunk, create embeddings and save to database
    
    Args:
        file_path: Path to document file
        split_strategy: Chunking strategy ('fixed_size', 'sentence', 'paragraph')
        chunk_size: Chunk size (for fixed_size strategy)
        overlap: Overlap (for fixed_size strategy)
        sentences_per_chunk: Number of sentences per chunk (for sentence strategy)
    """
    print(f"Processing file: {file_path}")
    print("Extracting text from file...")
    text = DocumentProcessor.extract_text(file_path)
    print(f"Extracted text with {len(text)} characters")
    
    print(f"Splitting into chunks by strategy: {split_strategy}...")
    if split_strategy == 'fixed_size':
        chunks = TextChunker.fixed_size_chunks(text, chunk_size, overlap)
    elif split_strategy == 'sentence':
        chunks = TextChunker.sentence_based_chunks(text, sentences_per_chunk)
    elif split_strategy == 'paragraph':
        chunks = TextChunker.paragraph_based_chunks(text)
    else:
        raise ValueError(f"Invalid split strategy: {split_strategy}")
    
    print(f"Created {len(chunks)} chunks")
    
    print("Creating embeddings...")
    embedding_gen = EmbeddingGenerator()
    
    filename = os.path.basename(file_path)
    db_manager = DatabaseManager(POSTGRES_URL)
    
    print("Clearing existing chunks from database...")
    db_manager.delete_all_chunks()
    
    chunks_data = []
    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i+1}/{len(chunks)}...", end='\r')
        embedding = embedding_gen.generate_embedding(chunk)
        chunks_data.append({
            'chunk_text': chunk,
            'embedding': embedding,
            'filename': filename,
            'split_strategy': split_strategy
        })
        
        if i + 1 < len(chunks):
            time.sleep(1)
    
    print(f"\nInserting {len(chunks_data)} chunks into database...")
    db_manager.insert_chunks(chunks_data)
    db_manager.close()
    
    print(f"Document indexed successfully!")
    print(f"  File: {filename}")
    print(f"  Number of chunks: {len(chunks_data)}")
    print(f"  Chunking strategy: {split_strategy}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Process documents (PDF/DOCX) and create embeddings in PostgreSQL database'
    )
    parser.add_argument('file_path', help='Path to PDF or DOCX file')
    parser.add_argument(
        '--strategy',
        choices=['fixed_size', 'sentence', 'paragraph'],
        default='fixed_size',
        help='Chunking strategy (default: fixed_size)'
    )
    parser.add_argument(
        '--chunk_size',
        type=int,
        default=1000,
        help='Chunk size for fixed_size strategy (default: 1000)'
    )
    parser.add_argument(
        '--overlap',
        type=int,
        default=200,
        help='Overlap between chunks for fixed_size strategy (default: 200)'
    )
    parser.add_argument(
        '--sentences_per_chunk',
        type=int,
        default=5,
        help='Number of sentences per chunk for sentence strategy (default: 5)'
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file_path):
        print(f"Error: File not found: {args.file_path}")
        sys.exit(1)
    
    try:
        process_document(
            args.file_path,
            split_strategy=args.strategy,
            chunk_size=args.chunk_size,
            overlap=args.overlap,
            sentences_per_chunk=args.sentences_per_chunk
        )
    except Exception as e:
        print(f"error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()

