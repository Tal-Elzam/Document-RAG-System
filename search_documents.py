"""
search_documents.py
Script for searching documents using embeddings and cosine similarity
"""

import os
import sys
from typing import List, Tuple
import argparse

from dotenv import load_dotenv
import psycopg2
import numpy as np
import google.generativeai as genai
from sklearn.metrics.pairwise import cosine_similarity

# Load environment variables
load_dotenv()

# Load settings from .env
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
POSTGRES_URL = os.getenv('POSTGRES_URL')

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not defined in .env file")
if not POSTGRES_URL:
    raise ValueError("POSTGRES_URL not defined in .env file")

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)


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
            # Create embedding
            result = genai.embed_content(
                model='models/text-embedding-004',
                content=text,
                task_type="retrieval_query"
            )
            
            return result['embedding']
        except Exception as e:
            raise ValueError(f"Error creating embedding: {str(e)}")


class DatabaseSearch:
    """Class for searching in database"""
    
    def __init__(self, postgres_url: str):
        """Initialize database connection"""
        self.conn = psycopg2.connect(postgres_url)
    
    def _calculate_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors using sklearn
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Cosine similarity value (between -1 and 1)
        """
        # Convert to numpy arrays and reshape for sklearn
        vec1_array = np.array(vec1).reshape(1, -1)
        vec2_array = np.array(vec2).reshape(1, -1)
        
        # Calculate cosine similarity using sklearn
        similarity = cosine_similarity(vec1_array, vec2_array)[0][0]
        return float(similarity)
    
    def search_similar_chunks(
        self,
        query_embedding: List[float],
        top_k: int = 5
    ) -> List[Tuple[dict, float]]:
        """
        Search for chunks most similar to query
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            
        Returns:
            List of tuples of (chunk_dict, similarity_score)
        """
        with self.conn.cursor() as cur:
            # Get all chunks from database
            cur.execute("""
                SELECT id, chunk_text, embedding, filename, split_strategy, created_at
                FROM document_chunks
            """)
            
            rows = cur.fetchall()
            
            # Calculate cosine similarity for each chunk
            results = []
            for row in rows:
                chunk_id, chunk_text, embedding, filename, split_strategy, created_at = row
                
                # Convert embedding to list format if needed
                if isinstance(embedding, (list, tuple)):
                    chunk_embedding = list(embedding)
                else:
                    # If embedding is in different format, try to convert
                    chunk_embedding = list(embedding) if hasattr(embedding, '__iter__') else []
                
                if not chunk_embedding:
                    continue
                
                # Calculate cosine similarity
                similarity = self._calculate_similarity(query_embedding, chunk_embedding)
                
                results.append((
                    {
                        'id': chunk_id,
                        'chunk_text': chunk_text,
                        'filename': filename,
                        'split_strategy': split_strategy,
                        'created_at': created_at
                    },
                    similarity
                ))
            
            # Sort by similarity (highest to lowest)
            results.sort(key=lambda x: x[1], reverse=True)
            
            # Return top_k results
            return results[:top_k]
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


def search_documents(query: str, top_k: int = 5):
    """
    Search documents by text query
    
    Args:
        query: Text query
        top_k: Number of results to return (default: 5)
    """
    print(f"Searching: '{query}'")
    print("-" * 60)
    
    # 1. Create embedding for query
    print("Creating embedding for query...")
    embedding_gen = EmbeddingGenerator()
    query_embedding = embedding_gen.generate_embedding(query)
    
    # 2. Search in database
    print("Searching in database...")
    db_search = DatabaseSearch(POSTGRES_URL)
    results = db_search.search_similar_chunks(query_embedding, top_k)
    db_search.close()
    
    # 3. Display results
    if not results:
        print("No results found in database.")
        return
    
    print(f"\nFound {len(results)} similar chunks:\n")
    
    for i, (chunk_data, similarity) in enumerate(results, 1):
        print(f"{'='*60}")
        print(f"Result #{i} (similarity: {similarity:.4f})")
        print(f"File: {chunk_data['filename']}")
        print(f"Split strategy: {chunk_data['split_strategy']}")
        print(f"ID: {chunk_data['id']}")
        print(f"\nChunk:")
        print(f"{chunk_data['chunk_text'][:500]}..." if len(chunk_data['chunk_text']) > 500 else chunk_data['chunk_text'])
        print()


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Search documents using embeddings and cosine similarity'
    )
    parser.add_argument('query', help='Text query for search')
    parser.add_argument(
        '--top_k',
        type=int,
        default=5,
        help='Number of results to return (default: 5)'
    )
    
    args = parser.parse_args()
    
    try:
        search_documents(args.query, args.top_k)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()

