#!/usr/bin/env python3
"""
Embedding Generation Script for Course Creation Assistant

This script generates embeddings from textual data using OpenAI's text-embedding-3-large model
and stores them in Pinecone for semantic search and retrieval.

Usage:
    python scripts/generate_embeddings.py --data-type prompts
    python scripts/generate_embeddings.py --data-type custom --input-file data.txt
    python scripts/generate_embeddings.py --text "Your custom text here"
"""

import argparse
from dataclasses import dataclass
import glob
import json
import os
from pathlib import Path
import sys
import time
from typing import List, Dict, Any, Optional
import logging
import unicodedata
import re


from docx import Document
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

BASE_DIR = Path(__file__).resolve().parent
BASE_DIR.joinpath("logs").mkdir(exist_ok=True)
LOG_DIR = BASE_DIR.joinpath("logs")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'embedding_generation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class EmbeddingData:
    """Data structure for embedding information"""
    id: str
    text: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None

class EmbeddingGenerator:
    """Main class for generating and storing embeddings"""
    
    def __init__(self):
        """Initialize OpenAI and Pinecone clients"""
        # Initialize OpenAI client (direct OpenAI API)
        self.openai_client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Initialize Pinecone client
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        
        # Configuration
        self.embedding_model = "text-embedding-3-large"
        self.embedding_dimension = 3072  # dimension for text-embedding-3-large
        self.index_name = os.getenv("PINECONE_INDEX_NAME", "course-assistant-embeddings")
        self.batch_size = 100
        
        # Initialize Pinecone index
        self._initialize_pinecone_index()
    
    def _sanitize_id(self, text: str) -> str:
        """Sanitize text to create ASCII-only IDs for Pinecone"""
        # Normalize unicode characters to ASCII equivalents
        ascii_text = unicodedata.normalize('NFD', text)
        ascii_text = ascii_text.encode('ascii', 'ignore').decode('ascii')
        
        # Replace spaces and special characters with underscores
        ascii_text = re.sub(r'[^a-zA-Z0-9_-]', '_', ascii_text)
        
        # Remove multiple consecutive underscores
        ascii_text = re.sub(r'_+', '_', ascii_text)
        
        # Remove leading/trailing underscores
        ascii_text = ascii_text.strip('_')
        
        # Ensure the ID is not empty and doesn't start with a number
        if not ascii_text or ascii_text[0].isdigit():
            ascii_text = f"id_{ascii_text}"
        
        return ascii_text

    def _initialize_pinecone_index(self):
        """Initialize or connect to Pinecone index"""
        try:
            # Check if index exists
            existing_indexes = [index.name for index in self.pc.list_indexes()]
            
            if self.index_name not in existing_indexes:
                logger.info(f"Creating new Pinecone index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.embedding_dimension,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region=os.getenv("PINECONE_REGION", "us-east-1")
                    )
                )
                # Wait for index to be ready
                while not self.pc.describe_index(self.index_name).status['ready']:
                    time.sleep(1)
            
            # Connect to index
            self.index = self.pc.Index(self.index_name)
            logger.info(f"Connected to Pinecone index: {self.index_name}")
            
        except Exception as e:
            logger.error(f"Error initializing Pinecone index: {e}")
            raise
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text using OpenAI"""
        try:
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text,
                encoding_format="float"
            )
            return response.data[0].embedding
        
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts in batch"""
        try:
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=texts,
                encoding_format="float"
            )
            return [data.embedding for data in response.data]
        
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise
    
    def process_embeddings(self, embedding_data_list: List[EmbeddingData]) -> None:
        """Process and store embeddings in Pinecone"""
        logger.info(f"Processing {len(embedding_data_list)} embeddings...")
        
        # Process in batches
        for i in range(0, len(embedding_data_list), self.batch_size):
            batch = embedding_data_list[i:i + self.batch_size]
            
            # Generate embeddings for batch
            texts = [item.text for item in batch]
            embeddings = self.generate_embeddings_batch(texts)
            
            # Prepare vectors for Pinecone
            vectors = []
            for j, item in enumerate(batch):
                vectors.append({
                    "id": item.id,
                    "values": embeddings[j],
                    "metadata": {
                        **item.metadata,
                        "text": item.text[:1000],  # Store first 1000 chars in metadata
                        "text_length": len(item.text)
                    }
                })
            
            # Upsert to Pinecone
            try:
                self.index.upsert(vectors=vectors)
                logger.info(f"Successfully stored batch {i//self.batch_size + 1}")
                
                # Rate limiting - avoid hitting API limits
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error storing batch {i//self.batch_size + 1}: {e}")
                raise
    
    def embed_prompts_from_file(self) -> None:
        """Extract and embed all prompts from the prompts.py file"""
        logger.info("Extracting prompts from prompts.py...")
        
        try:
            # Import prompts module
            from app import prompts
            
            embedding_data_list = []
            
            # Get all prompt variables
            prompt_vars = [attr for attr in dir(prompts) if attr.endswith('_prompt')]
            
            for prompt_var in prompt_vars:
                prompt_content = getattr(prompts, prompt_var)
                
                # Create embedding data with sanitized ID
                sanitized_id = self._sanitize_id(f"prompt_{prompt_var}")
                embedding_data = EmbeddingData(
                    id=sanitized_id,
                    text=prompt_content,
                    metadata={
                        "type": "prompt",
                        "prompt_name": prompt_var,
                        "source": "prompts.py",
                        "original_id": f"prompt_{prompt_var}"
                    }
                )
                embedding_data_list.append(embedding_data)
            
            logger.info(f"Found {len(embedding_data_list)} prompts to embed")
            self.process_embeddings(embedding_data_list)
            
        except Exception as e:
            logger.error(f"Error processing prompts: {e}")
            raise
    
    def embed_custom_text(self, text: str, text_id: Optional[str] = None) -> None:
        """Embed a single custom text"""
        if not text_id:
            text_id = f"custom_{int(time.time())}"
        
        # Sanitize the ID
        sanitized_id = self._sanitize_id(text_id)
        
        embedding_data = EmbeddingData(
            id=sanitized_id,
            text=text,
            metadata={
                "type": "custom",
                "source": "manual_input",
                "original_id": text_id
            }
        )
        
        self.process_embeddings([embedding_data])
        logger.info(f"Successfully embedded custom text with ID: {sanitized_id}")
    
    def embed_from_file(self, file_path: str) -> None:
        """Embed text content from a file"""
        logger.info(f"Embedding content from file: {file_path}")
        
        try:
            file_ext = Path(file_path).suffix.lower()
            if file_ext == ".txt":
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            elif file_ext == ".docx":
                content = self._read_docx(file_path)
            else:
                logger.warning(f"Unsupported file type: {file_path}")
                return
            
            # Split content into chunks if it's too large
            chunks = self._split_text(content, max_length=8000)
            
            embedding_data_list = []
            for i, chunk in enumerate(chunks):
                # Create sanitized ID for the file chunk
                file_stem = Path(file_path).stem
                original_id = f"file_{file_stem}_chunk_{i}"
                sanitized_id = self._sanitize_id(original_id)
                
                embedding_data = EmbeddingData(
                    id=sanitized_id,
                    text=chunk,
                    metadata={
                        "type": "file_content",
                        "source_file": file_path,
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "original_id": original_id,
                        "original_filename": file_stem
                    }
                )
                embedding_data_list.append(embedding_data)
            
            self.process_embeddings(embedding_data_list)
            
        except Exception as e:
            logger.error(f"Error embedding file {file_path}: {e}")
            raise
    
    def _split_text(self, text: str, max_length: int = 8000) -> List[str]:
        """Split text into chunks of maximum length"""
        if len(text) <= max_length:
            return [text]
        
        chunks = []
        current_chunk = ""
        sentences = text.split('. ')
        
        for sentence in sentences:
            if len(current_chunk + sentence) <= max_length:
                current_chunk += sentence + '. '
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + '. '
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def query_similar(self, query_text: str, top_k: int = 3) -> List[Dict]:
        """Query for similar embeddings"""
        try:
            # Generate embedding for query
            query_embedding = self.generate_embedding(query_text)
            
            # Search in Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            return [
                {
                    "id": match.id,
                    "score": match.score,
                    "metadata": match.metadata
                }
                for match in results.matches
            ]
            
        except Exception as e:
            logger.error(f"Error querying similar embeddings: {e}")
            raise
    
    def get_index_stats(self) -> Dict:
        """Get statistics about the Pinecone index"""
        try:
            stats = self.index.describe_index_stats()
            return {
                "total_vectors": stats.total_vector_count,
                "dimension": stats.dimension,
                "index_fullness": stats.index_fullness
            }
        except Exception as e:
            logger.error(f"Error getting index stats: {e}")
            return {}
        
        
    def _read_docx(self, file_path: str) -> str:
        """Read content from a .docx file"""
        doc = Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return "\n".join(full_text)

def main():
    """Main function to run the embedding generation script"""
    parser = argparse.ArgumentParser(description="Generate embeddings using OpenAI and store in Pinecone")
    parser.add_argument("--data-type", choices=["prompts", "custom", "file", "dir"], 
                       help="Type of data to embed")
    parser.add_argument("--text", type=str, help="Custom text to embed")
    parser.add_argument("--input-file", type=str, help="Path to input file")
    parser.add_argument("--input-dir", type=str, help="Path to input dir")
    parser.add_argument("--query", type=str, help="Query text to find similar embeddings")
    parser.add_argument("--stats", action="store_true", help="Show index statistics")
    
    args = parser.parse_args()
    
    # Check required environment variables
    required_env_vars = ["OPENAI_API_KEY", "PINECONE_API_KEY"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        return
    
    try:
        # Initialize embedding generator
        generator = EmbeddingGenerator()
        
        if args.stats:
            stats = generator.get_index_stats()
            logger.info(f"Index Statistics: {json.dumps(stats, indent=2)}")
            return
        
        if args.query:
            results = generator.query_similar(args.query)
            logger.info(f"Similar embeddings for '{args.query}':")
            for result in results:
                print(results)
                logger.info(f"  ID: {result['id']}, Score: {result['score']:.4f}")
            return
        
        if args.data_type == "prompts":
            generator.embed_prompts_from_file()
            
        elif args.data_type == "custom" and args.text:
            generator.embed_custom_text(args.text)
            
        elif args.data_type == "file" and args.input_file:
            generator.embed_from_file(args.input_file)
        
        elif args.data_type == 'dir' and args.input_dir:
            _input_dir = Path(args.input_dir).absolute()
            print(_input_dir)
            files = glob.glob(os.path.join(_input_dir, "**"))
            print(files)
            files = [f for f in files if f.lower().endswith((".txt", ".docx"))]
            print(files)
            for file in files:
                # print(file)
                generator.embed_from_file(str(file))
            
        else:
            logger.error("Invalid arguments. Use --help for usage information.")
            return
        
        # Show final statistics
        stats = generator.get_index_stats()
        logger.info(f"Final Index Statistics: {json.dumps(stats, indent=2)}")
        
    except Exception as e:
        logger.error(f"Script execution failed: {e}")
        return

if __name__ == "__main__":
    main() 