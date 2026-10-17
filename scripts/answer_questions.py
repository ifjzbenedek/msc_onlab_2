import argparse
import sys
from functools import partial
sys.path.insert(0, ".")

import config
from src.eval.question_sets import collect_answer_questions
from src.llm.cli_client import ModelCallFailed, verify_subscription_login
from src.llm.constants import MAX_CONSECUTIVE_FAILURES, MAX_PARALLEL_MODEL_CALLS
from src.llm.parallel import complete_in_parallel
from src.pipeline.answer_file import load_answers, save_answers
from src.pipeline.baseline import generate_answer
from src.pipeline.crag import answer_with_crag
from src.pipeline.critic import answer_with_critic
from src.retrieval.reranker import save_new_scores
from src.retrieval.system import load_retrieval_system

ANSWER_FUNCTIONS = {
    "baseline": partial(generate_answer, prompt_path=config.ANSWER_PROMPT_PATH),
    "crag": partial(answer_with_crag, prompt_path=config.ANSWER_PROMPT_PATH),
    "full": partial(
        answer_with_critic,
        answer_prompt_path=config.ANSWER_PROMPT_PATH,
        critic_prompt_path=config.CRITIC_PROMPT_PATH,
    ),
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--system", choices=list(ANSWER_FUNCTIONS), required=True)
    system_name = parser.parse_args().system
    answer_function = ANSWER_FUNCTIONS[system_name]
    answers_path = config.answers_path(system_name)

    verify_subscription_login()
    system = load_retrieval_system(
        config.CHUNKS_PATH, config.DENSE_INDEX_PATH, config.EMBED_MODEL, config.RERANK_MODEL, config.RERANK_SCORES_PATH
    )
    answers = load_answers(answers_path)
    questions = collect_answer_questions(config.PREPARED_QA_PATH, config.TEST_IDS_PATH, config.B_SET_PATH)
    tasks = {
        question_id: partial(answer_function, system, question)
        for question_id, question in questions.items()
        if question_id not in answers
    }
    saved_score_count = len(system.score_cache)
    consecutive_failures = 0
    for question_id, future in complete_in_parallel(tasks, MAX_PARALLEL_MODEL_CALLS):
        progress = f"{len(answers) + 1}/{len(questions)} {question_id}"
        try:
            generated = future.result()
        except ModelCallFailed as error:
            consecutive_failures += 1
            print(f"{progress} failed: {error}")
            if consecutive_failures == MAX_CONSECUTIVE_FAILURES:
                raise
            continue
        consecutive_failures = 0
        answers[question_id] = generated
        save_answers(answers, answers_path)
        with system.lock:
            saved_score_count = save_new_scores(system.score_cache, saved_score_count, config.RERANK_SCORES_PATH)
        print(f"{progress} answerable={generated.answerable} confidence={generated.confidence:.2f}")
    print(f"Saved {len(answers)} answers to {answers_path}")


if __name__ == "__main__":
    main()
