import sys
import webbrowser
sys.path.insert(0, ".")

import config
from src.corpus.chunk_file import load_chunks
from src.eval.answer_judge import load_judgments
from src.eval.b_set import load_b_set
from src.eval.constants import JUDGE_REVIEW_SYSTEM
from src.eval.evaluation_context import build_text_context
from src.eval.judge_review import build_review_case, build_review_key, draw_review_sample, render_review_page
from src.eval.qa_dataset import load_qa_items
from src.pipeline.answer_file import load_answers
from src.storage.files import write_text_atomically


def main() -> None:
    answers = load_answers(config.answers_path(JUDGE_REVIEW_SYSTEM))
    judgments = load_judgments(config.judgments_path(JUDGE_REVIEW_SYSTEM))
    context = build_text_context(
        load_qa_items(config.PREPARED_QA_PATH),
        load_b_set(config.B_SET_PATH) if config.B_SET_PATH.exists() else [],
        load_chunks(config.CHUNKS_PATH),
    )
    question_ids = draw_review_sample(list(judgments))
    cases = [build_review_case(question_id, answers[question_id], context) for question_id in question_ids]
    template = config.JUDGE_REVIEW_TEMPLATE_PATH.read_text(encoding="utf-8")
    write_text_atomically(config.JUDGE_REVIEW_PAGE_PATH, render_review_page(template, cases, build_review_key(question_ids)))
    print(f"Wrote {len(cases)} cases to {config.JUDGE_REVIEW_PAGE_PATH}")
    webbrowser.open(config.JUDGE_REVIEW_PAGE_PATH.as_uri())


if __name__ == "__main__":
    main()
