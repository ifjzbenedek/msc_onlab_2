import sys
from collections import Counter
sys.path.insert(0, ".")

import config
from src.eval.question_sets import collect_answer_questions
from src.pipeline.crag import find_top_score, retrieve_with_crag
from src.retrieval.reranker import save_new_scores
from src.retrieval.system import load_retrieval_system


def main() -> None:
    system = load_retrieval_system(
        config.CHUNKS_PATH, config.DENSE_INDEX_PATH, config.EMBED_MODEL, config.RERANK_MODEL, config.RERANK_SCORES_PATH
    )
    questions = collect_answer_questions(config.PREPARED_QA_PATH, config.TEST_IDS_PATH, config.B_SET_PATH)
    saved_score_count = len(system.score_cache)
    decisions: Counter[str] = Counter()
    for position, (question_id, question) in enumerate(questions.items(), start=1):
        retrieval = retrieve_with_crag(system, question)
        saved_score_count = save_new_scores(system.score_cache, saved_score_count, config.RERANK_SCORES_PATH)
        decisions[retrieval.decision] += 1
        print(
            f"{position}/{len(questions)} {question_id} {retrieval.decision}"
            f" top {find_top_score(retrieval.ranked):.3f} expansions {retrieval.expansions}"
        )
    print(f"CRAG decisions: {dict(decisions)}")


if __name__ == "__main__":
    main()
