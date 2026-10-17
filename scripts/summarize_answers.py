import sys
sys.path.insert(0, ".")

import config
from src.corpus.chunk_file import load_chunks
from src.corpus.constants import CORPUS_DOCUMENTS
from src.corpus.pdf import extract_page_texts
from src.eval.answer_judge import load_judgments
from src.eval.answer_metrics import (
    cites_any_expected_section,
    compute_risk_coverage,
    find_coverage_at_precision,
    is_answered,
    is_citation_correct,
    summarize_answers,
)
from src.eval.b_set import load_b_set
from src.eval.constants import RISK_COVERAGE_PRINTED_POINTS, SYSTEM_NAMES, TARGET_PRECISION
from src.eval.evaluation_context import build_evaluation_context
from src.eval.qa_dataset import load_qa_items
from src.eval.schemas.answer_summary import AnswerSummary
from src.eval.schemas.b_set_item import BSetItem
from src.pipeline.answer_file import load_answers
from src.pipeline.schemas.generated_answer import GeneratedAnswer

CITATION_CHECKS = {"text": is_citation_correct, "any §": cites_any_expected_section}


def format_quality(summary: AnswerSummary) -> str:
    answered = max(summary.answered, 1)
    return (
        f"answered {summary.answered / summary.questions:.2f} | correct {summary.correct / answered:.2f}"
        f" | partially {summary.partially_correct / answered:.2f} | cited text {summary.citation_correct / answered:.2f},"
        f" any § {summary.citation_any_section / answered:.2f}, all § {summary.citation_all_sections / answered:.2f}"
    )


def format_good_answers_and_cost(summary: AnswerSummary) -> str:
    answered = max(summary.answered, 1)
    return (
        f"correct+cited text {summary.correct_and_cited / answered:.2f} of answered,"
        f" {summary.correct_and_cited / summary.questions:.2f} of all"
        f" | correct+cited any § {summary.correct_and_any_section_cited / answered:.2f} of answered,"
        f" {summary.correct_and_any_section_cited / summary.questions:.2f} of all"
        f" | LLM calls {summary.mean_llm_calls:.2f} | tokens {summary.mean_input_tokens:.0f}+{summary.mean_output_tokens:.0f}"
        f" | LLM {summary.mean_llm_seconds:.1f} s | reranked {summary.mean_reranked_candidates:.1f}"
    )


def select_b_ids(
    b_items: list[BSetItem], answers: dict[str, GeneratedAnswer], answerable: bool, languages: set[str]
) -> list[str]:
    return [
        item.id
        for item in b_items
        if item.answerable == answerable and item.language in languages and item.id in answers
    ]


def main() -> None:
    b_items = load_b_set(config.B_SET_PATH) if config.B_SET_PATH.exists() else []
    context = build_evaluation_context(
        load_qa_items(config.PREPARED_QA_PATH),
        b_items,
        load_chunks(config.CHUNKS_PATH),
        {document: extract_page_texts(config.SOURCE_PDF_DIR.joinpath(document)) for document in CORPUS_DOCUMENTS},
    )
    for system_name in SYSTEM_NAMES:
        answers_path = config.answers_path(system_name)
        if not answers_path.exists():
            continue
        answers = load_answers(answers_path)
        judgments = load_judgments(config.judgments_path(system_name))
        fulop_ids = [question_id for question_id in answers if question_id in context.qa_items_by_id]
        all_languages = {item.language for item in b_items}
        b_groups = [("B", all_languages), *((f"B {language}", {language}) for language in sorted(all_languages))]
        answerable_groups = [("Fulop eval", fulop_ids)] + [
            (f"{group_name} answerable", select_b_ids(b_items, answers, True, languages))
            for group_name, languages in b_groups
        ]
        print(f"== {system_name}")
        for group_name, question_ids in answerable_groups:
            if question_ids:
                summary = summarize_answers(question_ids, answers, judgments, context)
                print(f"  {group_name} ({len(question_ids)}): {format_quality(summary)}")
                print(f"      {format_good_answers_and_cost(summary)}")
        for group_name, languages in b_groups:
            unanswerable_ids = select_b_ids(b_items, answers, False, languages)
            if unanswerable_ids:
                abstained = sum(not is_answered(answers[question_id]) for question_id in unanswerable_ids)
                print(f"  {group_name} unanswerable ({len(unanswerable_ids)}): abstained {abstained / len(unanswerable_ids):.2f}")
        for check_name, citation_check in CITATION_CHECKS.items():
            points = compute_risk_coverage(list(answers), answers, judgments, context, citation_check)
            coverage = find_coverage_at_precision(points, TARGET_PRECISION)
            curve = ", ".join(
                f"{point.coverage:.2f}:{point.precision:.2f}"
                for point in points[:: max(len(points) // RISK_COVERAGE_PRINTED_POINTS, 1)]
            )
            print(
                f"  risk-coverage, citation {check_name}: coverage at precision >= {TARGET_PRECISION}: {coverage:.2f}"
                f" | coverage:precision {curve}"
            )


if __name__ == "__main__":
    main()
