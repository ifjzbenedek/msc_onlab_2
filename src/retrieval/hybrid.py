from collections.abc import Callable

from src.corpus.schemas.chunk import Chunk
from src.retrieval.constants import RERANK_CANDIDATE_COUNT

type Search = Callable[[str, int], list[Chunk]]


def collect_candidates(rankings: list[list[Chunk]]) -> list[Chunk]:
    candidates: list[Chunk] = []
    seen_ids: set[str] = set()
    for ranking in rankings:
        for chunk in ranking:
            if chunk.id not in seen_ids:
                seen_ids.add(chunk.id)
                candidates.append(chunk)
    return candidates


def search_candidates(
    searches: list[Search], query: str, candidate_count: int = RERANK_CANDIDATE_COUNT
) -> list[Chunk]:
    candidates_per_search = candidate_count // len(searches)
    return collect_candidates([search(query, candidates_per_search) for search in searches])
