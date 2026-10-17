import argparse
import sys
from functools import partial
sys.path.insert(0, ".")

import config
from src.corpus.chunk_file import load_chunks
from src.eval.answer_judge import judge_answer, load_judgments, save_judgments
from src.eval.answer_metrics import find_cited_texts, find_source_texts, is_answerable_question, is_answered
from src.eval.b_set import load_b_set
from src.eval.evaluation_context import build_text_context
from src.eval.qa_dataset import load_qa_items
from src.llm.cli_client import ModelCallFailed, verify_subscription_login
from src.llm.constants import MAX_CONSECUTIVE_FAILURES, MAX_PARALLEL_MODEL_CALLS
from src.llm.parallel import complete_in_parallel
from src.pipeline.answer_file import load_answers


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--system", required=True)
    system_name = parser.parse_args().system

    verify_subscription_login()
    answers = load_answers(config.answers_path(system_name))
    judgments_path = config.judgments_path(system_name)
    judgments = load_judgments(judgments_path)
    context = build_text_context(
        load_qa_items(config.PREPARED_QA_PATH),
        load_b_set(config.B_SET_PATH) if config.B_SET_PATH.exists() else [],
        load_chunks(config.CHUNKS_PATH),
    )
    tasks = {
        question_id: partial(
            judge_answer,
            generated.question,
            find_source_texts(question_id, context),
            generated.answer,
            find_cited_texts(generated, context),
            config.JUDGE_PROMPT_PATH,
        )
        for question_id, generated in answers.items()
        if is_answered(generated) and is_answerable_question(question_id, context) and question_id not in judgments
    }
    consecutive_failures = 0
    for position, (question_id, future) in enumerate(complete_in_parallel(tasks, MAX_PARALLEL_MODEL_CALLS), start=1):
        try:
            judgment = future.result()
        except ModelCallFailed as error:
            consecutive_failures += 1
            print(f"{position}/{len(tasks)} {question_id} failed: {error}")
            if consecutive_failures == MAX_CONSECUTIVE_FAILURES:
                raise
            continue
        consecutive_failures = 0
        judgments[question_id] = judgment
        save_judgments(judgments, judgments_path)
        print(f"{position}/{len(tasks)} {question_id} {judgment.verdict}")
    print(f"Saved {len(judgments)} judgments to {judgments_path}")


if __name__ == "__main__":
    main()
