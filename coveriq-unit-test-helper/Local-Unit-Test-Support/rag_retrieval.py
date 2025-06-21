import os
import json
import numpy as np
import faiss
from google import genai
from google.genai.types import EmbedContentConfig
from dotenv import load_dotenv
from pathlib import Path
from typing import List, Dict

def get_embedding(text: str):
    """Get embedding for text using Gemini model."""
    try:
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
            
        client = genai.Client(api_key=api_key)
        response = client.models.embed_content(
            model="text-embedding-004",
            contents=[text],
            config=EmbedContentConfig(
                task_type="RETRIEVAL_QUERY",
            ),
        )
        return response.embeddings[0].values
    except Exception as e:
        print(f"Error getting embedding: {str(e)}")
        raise

def save_to_faiss(embeddings: List, metadata: Dict, save_path: str = "index.faiss", meta_path: str = "metadata.json"):
    """Save embeddings to FAISS index and metadata to JSON file."""
    try:
        if not embeddings:
            raise ValueError("No embeddings provided")
            
        dim = len(embeddings[0])
        index = faiss.IndexFlatL2(dim)
        index.add(np.array(embeddings).astype("float32"))
        faiss.write_index(index, save_path)

        json_metadata = [
            {
                "file_path": key[0],
                "symbol_name": key[1],
                **value
            }
            for key, value in metadata.items()
        ]

        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(json_metadata, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving to FAISS: {str(e)}")
        raise

def get_code_files(repo_path: str, include_pattern: str = "*.py", exclude_dirs: List[str] = ["venv", "__pycache__", "Local-Unit-Test-Support"]) -> List[Path]:
    """Get all Python files in the repository, excluding specified directories."""
    repo = Path(repo_path).resolve()
    code_files = []
    for file in repo.rglob(include_pattern):
        if not any(ex in file.parts for ex in exclude_dirs):
            code_files.append(file)
    return code_files 