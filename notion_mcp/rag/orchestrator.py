from .vector_db import NotionVectorDB
from .indexer import DocumentChunker
from typing import List, Dict, Any, Optional
import structlog

logger = structlog.get_logger(__name__)


class RAGOrchestrator:
    """
    Orchestrates the RAG lifecycle: Indexing and Searching.
    """

    def __init__(self, db_path: str = "./.lancedb"):
        self.vector_db = NotionVectorDB(db_path)
        self.chunker = DocumentChunker()

    async def index_pages(self, pages: List[Dict[str, Any]]):
        """Chunk and index a list of Notion pages."""
        all_chunks = []
        for page in pages:
            chunks = self.chunker.chunk_page(page)
            all_chunks.extend(chunks)

        if all_chunks:
            self.vector_db.upsert_chunks(all_chunks)
            logger.info(
                "RAG Index updated",
                pages_processed=len(pages),
                chunks_added=len(all_chunks),
            )

    async def semantic_search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Find relevant Notion context for a query."""
        return self.vector_db.search(query, limit=limit)
