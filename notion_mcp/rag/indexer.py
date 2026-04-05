import re
from typing import List, Dict, Any


class DocumentChunker:
    """
    Intelligent document chunker for Notion pages.
    Splits content by blocks while maintaining semantic context.
    """

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_page(self, page_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Split a Notion page into manageable chunks.
        Expects page_data containing 'id', 'title', 'content', 'url', 'last_edited'.
        """
        content = page_data.get("content", "")
        if not content:
            return []

        # Simple overlap-based chunking for text blocks
        # In a more advanced version, we'd preserve block boundaries
        chunks = []
        text_len = len(content)

        start = 0
        while start < text_len:
            end = start + self.chunk_size

            # If we're not at the end, try to find a better breakpoint (newline or period)
            if end < text_len:
                # Look for last newline or period in the last 100 characters of the chunk
                lookback = content[max(0, end - 100) : end]
                last_sentence = re.search(r"[.\n][^.\n]*$", lookback)
                if last_sentence:
                    end = max(0, end - (100 - last_sentence.start()))

            chunk_text = content[start:end].strip()
            if chunk_text:
                chunks.append(
                    {
                        "id": page_data["id"],
                        "title": page_data["title"],
                        "content": chunk_text,
                        "url": page_data["url"],
                        "last_edited": page_data["last_edited"],
                    }
                )

            # Advance with overlap
            start = end - self.chunk_overlap
            if start < 0:
                start = 0
            if end >= text_len:
                break

        return chunks
