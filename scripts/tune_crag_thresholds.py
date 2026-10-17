import sys
from statistics import mean
sys.path.insert(0, ".")

import config
from src.corpus.constants import CORPUS_DOCUMENTS
from src.corpus.pdf import extract_page_texts
from src.eval.constants import (
    ANSWER_CONTEXT_CUTOFF,
    CRAG_EXPANSION_BANDS,
    CRAG_THRESHOLD_GRID,
    CRAG_TUNING_STYLES,
    ORIGINAL_QUESTION_STYLE,
)
from src.eval.evaluation_context import EvaluationContext, build_evaluation_context
from src.eval.qa_dataset import load_qa_items
from src.eval.question_variants import load_question_variants
from src.eval.retrieval_metrics import is_retrieval_hit
from src.eval.schemas.qa_item import QAItem
from src.eval.splits import load_id_list
from src.pipeline.constants import CRAG_CANDIDATE_COUNTS, CRAG_CORRECT_THRESHOLD, EXPANDED_CANDIDATE_COUNTS
from src.pipeline.crag import find_top_score
from src.retrieval.constants import RERANK_CANDIDATE_COUNT
from src.retrieval.reranker import save_new_scores
from src.retrieval.system import RetrievalSystem, load_retrieval_system, retrieve

type Observation = dict[int, tuple[float, bool]]


def measure_top_score_and_hit(
    system: RetrievalSystem, context: EvaluationContext, qa_item: QAItem, question: str, candidate_count: int
) -> tuple[float, bool]:
    ranked = retrieve(system, question, candidate_count)
    top_chunks = [chunk for chunk, _ in ranked[:ANSWER_CONTEXT_CUTOFF]]
    ignored_ngrams = context.ignored_ngrams_by_document[qa_item.source_document]
    return find_top_score(ranked), is_retrieval_hit(qa_item, top_chunks, context.ngrams_by_chunk, ignored_ngrams)


def find_final_result(observation: Observation) -> tuple[float, bool]:
    for candidate_count in CRAG_CANDIDATE_COUNTS:
        if candidate_count in observation and observation[candidate_count][0] >= CRAG_CORRECT_THRESHOLD:
            return observation[candidate_count]
    return observation[max(observation)]


def format_hit_rate(results: list[tuple[float, bool]]) -> str:
    hit_rate = mean(is_hit for _, is_hit in results) if results else 0.0
    return f"{len(results):3} questions, hit rate {hit_rate:.2f}"


def print_threshold_table(title: str, results: list[tuple[float, bool]]) -> None:
    print(title)
    for threshold in CRAG_THRESHOLD_GRID:
        above = [result for result in results if result[0] >= threshold]
        below = [result for result in results if result[0] < threshold]
        print(f"  top score >= {threshold:.2f}: {format_hit_rate(above)} | below: {format_hit_rate(below)}")


def print_expansion_table(observations: list[Observation]) -> None:
    counts = " / ".join(str(candidate_count) for candidate_count in CRAG_CANDIDATE_COUNTS)
    print(f"Expansion effect by base top score, hit@{ANSWER_CONTEXT_CUTOFF} and mean top score with {counts} candidates:")
    for lower, upper in CRAG_EXPANSION_BANDS:
        in_band = [
            observation for observation in observations if lower <= observation[RERANK_CANDIDATE_COUNT][0] < upper
        ]
        if not in_band:
            continue
        hit_rates = " / ".join(
            f"{mean(observation[count][1] for observation in in_band):.2f}" for count in CRAG_CANDIDATE_COUNTS
        )
        top_scores = " / ".join(
            f"{mean(observation[count][0] for observation in in_band):.3f}" for count in CRAG_CANDIDATE_COUNTS
        )
        print(f"  [{lower:.2f}, {upper:.2f}): {len(in_band):3} questions, hit {hit_rates}, top {top_scores}")


def main() -> None:
    system = load_retrieval_system(
        config.CHUNKS_PATH, config.DENSE_INDEX_PATH, config.EMBED_MODEL, config.RERANK_MODEL, config.RERANK_SCORES_PATH
    )
    context = build_evaluation_context(
        load_qa_items(config.PREPARED_QA_PATH),
        [],
        system.chunks,
        {document: extract_page_texts(config.SOURCE_PDF_DIR.joinpath(document)) for document in CORPUS_DOCUMENTS},
    )
    variants = load_question_variants(config.QUESTION_VARIANTS_PATH)
    expansion_limit = CRAG_EXPANSION_BANDS[-1][1]
    saved_score_count = len(system.score_cache)
    observations: list[Observation] = []
    for qa_id in load_id_list(config.DEV_IDS_PATH):
        qa_item = context.qa_items_by_id[qa_id]
        for style in CRAG_TUNING_STYLES:
            question = qa_item.question if style == ORIGINAL_QUESTION_STYLE else variants[qa_id][style]
            observation = {
                RERANK_CANDIDATE_COUNT: measure_top_score_and_hit(
                    system, context, qa_item, question, RERANK_CANDIDATE_COUNT
                )
            }
            if observation[RERANK_CANDIDATE_COUNT][0] < expansion_limit:
                for candidate_count in EXPANDED_CANDIDATE_COUNTS:
                    observation[candidate_count] = measure_top_score_and_hit(
                        system, context, qa_item, question, candidate_count
                    )
            saved_score_count = save_new_scores(system.score_cache, saved_score_count, config.RERANK_SCORES_PATH)
            observations.append(observation)
    base_results = [observation[RERANK_CANDIDATE_COUNT] for observation in observations]
    print(f"{len(observations)} dev questions, hit@{ANSWER_CONTEXT_CUTOFF} overall: {format_hit_rate(base_results)}")
    print_threshold_table(f"Base retrieval ({RERANK_CANDIDATE_COUNT} candidates), split by top score:", base_results)
    print_expansion_table(observations)
    print_threshold_table(
        f"After expanding while the top score < {CRAG_CORRECT_THRESHOLD}, split by the final top score:",
        [find_final_result(observation) for observation in observations],
    )


if __name__ == "__main__":
    main()
