import hashlib
import json
from collections.abc import Callable
from functools import partial
from pathlib import Path

import torch
from sentence_transformers import CrossEncoder

from src.corpus.schemas.chunk import Chunk
from src.retrieval.constants import GPU_DEVICE, RERANK_BATCH_SIZE, RERANK_MAX_TOKENS
from src.retrieval.dense import select_device
from src.retrieval.hybrid import Search
from src.storage.files import write_text_atomically


def load_reranker(model_name: str) -> CrossEncoder:
    device = select_device()
    reranker = CrossEncoder(model_name, device=device, max_length=RERANK_MAX_TOKENS)
    if device == GPU_DEVICE:
        reranker.model.half()
        torch.cuda.empty_cache()
    return reranker


def build_score_key(query: str, chunk: Chunk) -> str:
    key_text = json.dumps([query, chunk.id, chunk.text], ensure_ascii=False)
    return hashlib.sha256(key_text.encode("utf-8")).hexdigest()


def load_score_cache(path: Path) -> dict[str, float]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_score_cache(score_cache: dict[str, float], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    merged_cache = load_score_cache(path) | score_cache
    write_text_atomically(path, json.dumps(merged_cache))


def save_new_scores(score_cache: dict[str, float], saved_score_count: int, path: Path) -> int:
    if len(score_cache) > saved_score_count:
        save_score_cache(score_cache, path)
    return len(score_cache)


def score_candidates(
    reranker: CrossEncoder, query: str, candidates: list[Chunk], score_cache: dict[str, float]
) -> list[float]:
    keys = [build_score_key(query, chunk) for chunk in candidates]
    missing = [(key, chunk) for key, chunk in zip(keys, candidates) if key not in score_cache]
    if missing:
        scores = reranker.predict([(query, chunk.text) for _, chunk in missing], batch_size=RERANK_BATCH_SIZE)
        score_cache.update({key: float(score) for (key, _), score in zip(missing, scores)})
    return [score_cache[key] for key in keys]


def rank_with_scores(
    reranker: CrossEncoder, query: str, candidates: list[Chunk], score_cache: dict[str, float]
) -> list[tuple[Chunk, float]]:
    scores = score_candidates(reranker, query, candidates, score_cache)
    return sorted(zip(candidates, scores), key=lambda pair: pair[1], reverse=True)


def rerank(
    reranker: CrossEncoder, query: str, candidates: list[Chunk], score_cache: dict[str, float], top_k: int
) -> list[Chunk]:
    ranked = rank_with_scores(reranker, query, candidates, score_cache)
    return [chunk for chunk, _ in ranked[:top_k]]


def search_reranked(
    candidate_search: Callable[[str], list[Chunk]],
    reranker: CrossEncoder,
    score_cache: dict[str, float],
    query: str,
    top_k: int,
) -> list[Chunk]:
    return rerank(reranker, query, candidate_search(query), score_cache, top_k)


def search_and_save_scores(
    search: Search, score_cache: dict[str, float], score_cache_path: Path, query: str, top_k: int
) -> list[Chunk]:
    saved_score_count = len(score_cache)
    results = search(query, top_k)
    save_new_scores(score_cache, saved_score_count, score_cache_path)
    return results


def build_saving_reranked_search(
    candidate_search: Callable[[str], list[Chunk]],
    reranker: CrossEncoder,
    score_cache: dict[str, float],
    score_cache_path: Path,
) -> Search:
    reranked_search = partial(search_reranked, candidate_search, reranker, score_cache)
    return partial(search_and_save_scores, reranked_search, score_cache, score_cache_path)
