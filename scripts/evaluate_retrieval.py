import argparse
import sys
from functools import partial
sys.path.insert(0, ".")

import config
from src.corpus.chunk_file import load_chunks
from src.corpus.constants import CORPUS_DOCUMENTS
from src.corpus.pdf import extract_page_texts
from src.eval.constants import (
    LETTER_WORD_PATTERN,
    ORIGINAL_QUESTION_STYLE,
    QUESTION_VARIANT_STYLES,
    RECALL_CUTOFFS,
    RERANKED_EVALUATION_STYLES,
)
from src.eval.corpus_coverage import build_corpus_ngrams
from src.eval.overlap import find_boilerplate_ngrams
from src.eval.qa_dataset import load_qa_items
from src.eval.question_variants import load_question_variants
from src.eval.report import format_recall
from src.eval.retrieval_metrics import build_ngrams_by_section, find_expected_sections, measure_recall
from src.eval.schemas.qa_item import QAItem
from src.eval.splits import draw_evaluation_subset, load_id_list
from src.retrieval.bm25 import build_bm25_index, search_bm25
from src.retrieval.constants import CPU_DEVICE
from src.retrieval.dense import load_dense_index, load_embedding_model, search_dense
from src.retrieval.hybrid import search_candidates
from src.retrieval.reranker import build_saving_reranked_search, load_reranker, load_score_cache


def build_questions(
    split_items: list[QAItem], variants: dict[str, dict[str, str]], style: str
) -> list[tuple[QAItem, str]]:
    return [
        (qa_item, qa_item.question if style == ORIGINAL_QUESTION_STYLE else variants[qa_item.id][style])
        for qa_item in split_items
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--search", action="append", help="run only this search, can be repeated")
    selected_searches = parser.parse_args().search
    chunks = load_chunks(config.CHUNKS_PATH)
    qa_items = {qa_item.id: qa_item for qa_item in load_qa_items(config.PREPARED_QA_PATH)}
    variants = load_question_variants(config.QUESTION_VARIANTS_PATH)
    ngrams_by_chunk = {chunk.id: build_corpus_ngrams([chunk]) for chunk in chunks}
    ngrams_by_section = build_ngrams_by_section(chunks, ngrams_by_chunk)
    ignored_ngrams_by_document = {
        document: find_boilerplate_ngrams(
            extract_page_texts(config.SOURCE_PDF_DIR.joinpath(document)), LETTER_WORD_PATTERN
        )
        for document in CORPUS_DOCUMENTS
    }
    embedding_model = load_embedding_model(config.EMBED_MODEL, CPU_DEVICE)
    dense_embeddings = load_dense_index(config.DENSE_INDEX_PATH, chunks)
    bm25_search = partial(search_bm25, build_bm25_index(chunks), chunks)
    dense_search = partial(search_dense, embedding_model, dense_embeddings, chunks)
    reranker = load_reranker(config.RERANK_MODEL)
    score_cache = load_score_cache(config.RERANK_SCORES_PATH)
    hybrid_reranked_search = build_saving_reranked_search(
        partial(search_candidates, [bm25_search, dense_search]), reranker, score_cache, config.RERANK_SCORES_PATH
    )
    dense_reranked_search = build_saving_reranked_search(
        partial(search_candidates, [dense_search]), reranker, score_cache, config.RERANK_SCORES_PATH
    )
    test_items = [qa_items[qa_id] for qa_id in load_id_list(config.TEST_IDS_PATH)]
    evaluation_items = [qa_items[qa_id] for qa_id in draw_evaluation_subset(test_items)]
    expected_sections_by_id = {
        qa_item.id: find_expected_sections(
            qa_item, ngrams_by_section, ignored_ngrams_by_document[qa_item.source_document]
        )
        for qa_item in evaluation_items
    }
    evaluation_plan = (
        ({"hybrid+rerank": hybrid_reranked_search}, RERANKED_EVALUATION_STYLES),
        ({"dense+rerank": dense_reranked_search}, RERANKED_EVALUATION_STYLES),
        ({"BM25": bm25_search, "dense": dense_search}, (ORIGINAL_QUESTION_STYLE, *QUESTION_VARIANT_STYLES)),
    )
    cutoffs = " ".join(f"R@{cutoff}" for cutoff in RECALL_CUTOFFS)

    for searches, styles in evaluation_plan:
        for search_name, search in searches.items():
            if selected_searches and search_name not in selected_searches:
                continue
            print(f"== {search_name}, eval ({len(evaluation_items)} questions), columns: {cutoffs}")
            for style in styles:
                questions = build_questions(evaluation_items, variants, style)
                result = measure_recall(
                    questions, search, ngrams_by_chunk, ignored_ngrams_by_document, expected_sections_by_id
                )
                print(f"  {style:20} {format_recall(result)}")


if __name__ == "__main__":
    main()
