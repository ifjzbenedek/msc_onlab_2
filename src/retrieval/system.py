import threading
from dataclasses import dataclass, field
from functools import partial
from pathlib import Path

import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder, SentenceTransformer

from src.corpus.chunk_file import load_chunks
from src.corpus.schemas.chunk import Chunk
from src.retrieval.bm25 import build_bm25_index, search_bm25
from src.retrieval.constants import CPU_DEVICE, RERANK_CANDIDATE_COUNT
from src.retrieval.dense import load_dense_index, load_embedding_model, search_dense
from src.retrieval.hybrid import search_candidates
from src.retrieval.reranker import load_reranker, load_score_cache, rank_with_scores


@dataclass
class RetrievalSystem:
    chunks: list[Chunk]
    bm25_index: BM25Okapi
    embedding_model: SentenceTransformer
    dense_embeddings: np.ndarray
    reranker: CrossEncoder
    score_cache: dict[str, float]
    lock: threading.Lock = field(default_factory=threading.Lock)


def load_retrieval_system(
    chunks_path: Path, dense_index_path: Path, embed_model: str, rerank_model: str, score_cache_path: Path
) -> RetrievalSystem:
    chunks = load_chunks(chunks_path)
    return RetrievalSystem(
        chunks=chunks,
        bm25_index=build_bm25_index(chunks),
        embedding_model=load_embedding_model(embed_model, CPU_DEVICE),
        dense_embeddings=load_dense_index(dense_index_path, chunks),
        reranker=load_reranker(rerank_model),
        score_cache=load_score_cache(score_cache_path),
    )


def retrieve(
    system: RetrievalSystem, query: str, candidate_count: int = RERANK_CANDIDATE_COUNT
) -> list[tuple[Chunk, float]]:
    bm25_search = partial(search_bm25, system.bm25_index, system.chunks)
    dense_search = partial(search_dense, system.embedding_model, system.dense_embeddings, system.chunks)
    with system.lock:
        candidates = search_candidates([bm25_search, dense_search], query, candidate_count)
        return rank_with_scores(system.reranker, query, candidates, system.score_cache)
