import random
from collections import defaultdict
from pathlib import Path

from src.eval.constants import (
    COVER_AND_TOC_PAGES,
    DEV_QUESTIONS_PER_STRATUM,
    SPLIT_SEED,
    TEST_QUESTIONS_PER_STRATUM,
)
from src.eval.schemas.qa_item import QAItem

type Stratum = tuple[str, str]


def comes_from_cover_or_toc(qa_item: QAItem) -> bool:
    cover_and_toc_pages = COVER_AND_TOC_PAGES.get(qa_item.source_document, set())
    item_pages = {page for chunk in qa_item.expected_chunks for page in chunk.spanned_pages}
    return item_pages <= cover_and_toc_pages


def stratum_of(qa_item: QAItem) -> Stratum:
    return qa_item.source_document, qa_item.difficulty


def draw_stratified_splits(qa_items: list[QAItem]) -> tuple[list[str], list[str]]:
    ids_by_stratum: defaultdict[Stratum, list[str]] = defaultdict(list)
    for qa_item in qa_items:
        ids_by_stratum[stratum_of(qa_item)].append(qa_item.id)
    dev_end = DEV_QUESTIONS_PER_STRATUM
    test_end = dev_end + TEST_QUESTIONS_PER_STRATUM
    random_generator = random.Random(SPLIT_SEED)
    dev_ids: list[str] = []
    test_ids: list[str] = []
    for stratum in sorted(ids_by_stratum):
        shuffled_ids = sorted(ids_by_stratum[stratum])
        random_generator.shuffle(shuffled_ids)
        dev_ids += shuffled_ids[:dev_end]
        test_ids += shuffled_ids[dev_end:test_end]
    return sorted(dev_ids), sorted(test_ids)


def save_id_list(ids: list[str], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(ids) + "\n", encoding="utf-8", newline="\n")
