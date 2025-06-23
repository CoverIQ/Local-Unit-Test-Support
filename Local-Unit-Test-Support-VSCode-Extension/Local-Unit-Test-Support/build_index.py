import os
import logging
from pathlib import Path
import argparse

from rag_retrieval import get_code_files, get_embedding, save_to_faiss
from ast_parser import extract_code_blocks

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def build_index(repo_path: str, index_path: str = "index.faiss", meta_path: str = "metadata.json"):
    """Build FAISS index and metadata for a repository."""
    logger.info(f"Building index for repository: {repo_path}")
    
    # Get all code files
    code_files = get_code_files(repo_path)
    logger.info(f"Found {len(code_files)} code files")
    
    # Extract code blocks
    code_blocks = {}
    for file in code_files:
        code_block = extract_code_blocks(file, repo_path)
        if code_block:
            code_blocks.update(code_block)
    
    logger.info(f"Extracted {len(code_blocks)} code blocks")
    
    if not code_blocks:
        logger.error("No code blocks were extracted from the repository")
        raise ValueError("No code blocks found in repository")

    # Create embeddings
    logger.info("Creating embeddings")
    embeddings = []
    for block in code_blocks.values():
        try:
            embedding = get_embedding(block["code"])
            embeddings.append(embedding)
        except Exception as e:
            logger.error(f"Failed to get embedding for block {block['symbol_name']}: {str(e)}")
            continue
            
    if not embeddings:
        logger.error("No embeddings were created")
        raise ValueError("Failed to create any embeddings")
        
    logger.info(f"Created {len(embeddings)} embeddings")
    
    # Save to FAISS and metadata
    save_to_faiss(embeddings, code_blocks, index_path, meta_path)
    logger.info(f"Index saved to {index_path}")
    logger.info(f"Metadata saved to {meta_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build FAISS index and metadata for a repository")
    parser.add_argument("repo_path", help="Path to the repository")
    parser.add_argument("--index", default="index.faiss", help="Path to save FAISS index (default: index.faiss)")
    parser.add_argument("--meta", default="metadata.json", help="Path to save metadata (default: metadata.json)")
    
    args = parser.parse_args()
    
    build_index(args.repo_path, args.index, args.meta) 