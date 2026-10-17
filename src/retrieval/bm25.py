from rank_bm25 import BM25Okapi

from src.corpus.schemas.chunk import Chunk
from src.retrieval.constants import BM25_TOKEN_PATTERN, BM25_TOKEN_PREFIX_LENGTH


def tokenize_for_bm25(text: str) -> list[str]:
    return [word[:BM25_TOKEN_PREFIX_LENGTH] for word in BM25_TOKEN_PATTERN.findall(text.lower())]


def build_bm25_index(chunks: list[Chunk]) -> BM25Okapi:
    return BM25Okapi([tokenize_for_bm25(chunk.text) for chunk in chunks])


def search_bm25(index: BM25Okapi, chunks: list[Chunk], query: str, top_k: int) -> list[Chunk]:
    scores = index.get_scores(tokenize_for_bm25(query))
    ranked_positions = sorted(range(len(chunks)), key=lambda position: scores[position], reverse=True)
    return [chunks[position] for position in ranked_positions[:top_k]]
