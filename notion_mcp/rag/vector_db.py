import lancedb
import numpy as np
import pyarrow as pa
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
import os
import structlog

logger = structlog.get_logger(__name__)


class NotionVectorDB:
    def __init__(
        self, db_path: str = "./.lancedb", model_name: str = "all-MiniLM-L6-v2"
    ):
        self.db_path = db_path
        self.db = lancedb.connect(db_path)
        self.model = SentenceTransformer(model_name)
        self.table_name = "notion_notes"

        # Schema for Notion notes
        self.schema = pa.schema(
            [
                pa.field("id", pa.string()),  # Notion Page ID
                pa.field("title", pa.string()),  # Page Title
                pa.field("content", pa.string()),  # Text Chunk
                pa.field("url", pa.string()),  # Notion URL
                pa.field("last_edited", pa.string()),  # Timestamp
                pa.field("vector", pa.list_(pa.float32(), 384)),  # Embedding vector
            ]
        )

        # Initialize table if it doesn't exist
        try:
            self.db.create_table(self.table_name, schema=self.schema)
            logger.info("LanceDB table created", table=self.table_name)
        except ValueError:
            # Table already exists, which is fine
            logger.debug("LanceDB table already exists", table=self.table_name)

        self.table = self.db.open_table(self.table_name)

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding vector for text."""
        return self.model.encode(text).tolist()

    def upsert_chunks(self, chunks: List[Dict[str, Any]]):
        """Insert or update chunks with embeddings."""
        data = []
        for chunk in chunks:
            vector = self.embed_text(chunk["content"])
            data.append(
                {
                    "id": chunk["id"],
                    "title": chunk["title"],
                    "content": chunk["content"],
                    "url": chunk["url"],
                    "last_edited": chunk["last_edited"],
                    "vector": vector,
                }
            )

        if data:
            # Overwrite for simplicity in this version (or use merge if LanceDB version supports)
            self.table.add(data)
            logger.info("Chunks embedded and stored", count=len(data))

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Perform semantic search."""
        query_vector = self.embed_text(query)
        results = self.table.search(query_vector).limit(limit).to_list()

        # Filter and format for API
        formatted_results = []
        for res in results:
            formatted_results.append(
                {
                    "id": res["id"],
                    "title": res["title"],
                    "content": res["content"],
                    "url": res["url"],
                    "score": res.get("_distance", 0),  # LanceDB returns _distance
                }
            )

        return formatted_results
