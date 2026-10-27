from collections.abc import Callable
from statistics import mean

from src.corpus.schemas.chunk import Chunk
from src.eval.constants import CORRECT_VERDICT, PARTIALLY_CORRECT_VERDICT
from src.eval.evaluation_context import EvaluationContext
from src.eval.retrieval_metrics import (
    SectionKey,
    find_expected_sections,
    finds_all_expected_sections,
    finds_any_expected_section,
    is_retrieval_hit,
)
from src.eval.schemas.answer_summary import AnswerSummary
from src.eval.schemas.judgment import Judgment
from src.eval.schemas.risk_coverage_point import RiskCoveragePoint
from src.pipeline.schemas.generated_answer import GeneratedAnswer

type CitationCheck = Callable[[str, GeneratedAnswer, EvaluationContext], bool]


def is_answered(generated: GeneratedAnswer) -> bool:
    return generated.has_cited_answer()


def is_answerable_question(question_id: str, context: EvaluationContext) -> bool:
    return question_id in context.qa_items_by_id or context.b_items_by_id[question_id].answerable


def find_source_texts(question_id: str, context: EvaluationContext) -> list[str]:
    if question_id in context.qa_items_by_id:
        return [expected.text for expected in context.qa_items_by_id[question_id].expected_chunks]
    return [context.chunks_by_id[chunk_id].text for chunk_id in context.b_items_by_id[question_id].gold_chunk_ids]


def find_cited_chunks(generated: GeneratedAnswer, context: EvaluationContext) -> list[Chunk]:
    return [context.chunks_by_id[chunk_id] for chunk_id in generated.cited_chunk_ids]


def find_cited_texts(generated: GeneratedAnswer, context: EvaluationContext) -> list[str]:
    return [chunk.text for chunk in find_cited_chunks(generated, context)]


def to_section_keys(chunk_ids: list[str], context: EvaluationContext) -> set[SectionKey]:
    return {
        SectionKey(context.chunks_by_id[chunk_id].document, context.chunks_by_id[chunk_id].section)
        for chunk_id in chunk_ids
    }


def find_expected_section_sets(question_id: str, context: EvaluationContext) -> list[set[SectionKey]]:
    if question_id in context.qa_items_by_id:
        qa_item = context.qa_items_by_id[question_id]
        ignored_ngrams = context.ignored_ngrams_by_document[qa_item.source_document]
        return find_expected_sections(qa_item, context.ngrams_by_section, ignored_ngrams)
    return [to_section_keys(context.b_items_by_id[question_id].gold_chunk_ids, context)]


def is_citation_correct(question_id: str, generated: GeneratedAnswer, context: EvaluationContext) -> bool:
    if question_id in context.qa_items_by_id:
        qa_item = context.qa_items_by_id[question_id]
        ignored_ngrams = context.ignored_ngrams_by_document[qa_item.source_document]
        return is_retrieval_hit(qa_item, find_cited_chunks(generated, context), context.ngrams_by_chunk, ignored_ngrams)
    gold_sections = to_section_keys(context.b_items_by_id[question_id].gold_chunk_ids, context)
    return bool(gold_sections & to_section_keys(generated.cited_chunk_ids, context))


def cites_any_expected_section(question_id: str, generated: GeneratedAnswer, context: EvaluationContext) -> bool:
    return finds_any_expected_section(
        find_expected_section_sets(question_id, context), find_cited_chunks(generated, context)
    )


def cites_all_expected_sections(question_id: str, generated: GeneratedAnswer, context: EvaluationContext) -> bool:
    return finds_all_expected_sections(
        find_expected_section_sets(question_id, context), find_cited_chunks(generated, context)
    )


def is_good_answer(
    question_id: str,
    generated: GeneratedAnswer,
    judgments: dict[str, Judgment],
    context: EvaluationContext,
    citation_check: CitationCheck = is_citation_correct,
) -> bool:
    return (
        is_answerable_question(question_id, context)
        and is_answered(generated)
        and question_id in judgments
        and judgments[question_id].verdict == CORRECT_VERDICT
        and citation_check(question_id, generated, context)
    )


def count_passing(
    question_ids: list[str],
    answers: dict[str, GeneratedAnswer],
    context: EvaluationContext,
    citation_check: CitationCheck,
) -> int:
    return sum(citation_check(question_id, answers[question_id], context) for question_id in question_ids)


def summarize_answers(
    question_ids: list[str],
    answers: dict[str, GeneratedAnswer],
    judgments: dict[str, Judgment],
    context: EvaluationContext,
) -> AnswerSummary:
    answered_ids = [question_id for question_id in question_ids if is_answered(answers[question_id])]
    verdicts = [judgments[question_id].verdict for question_id in answered_ids if question_id in judgments]
    return AnswerSummary(
        questions=len(question_ids),
        answered=len(answered_ids),
        correct=verdicts.count(CORRECT_VERDICT),
        partially_correct=verdicts.count(PARTIALLY_CORRECT_VERDICT),
        citation_correct=count_passing(answered_ids, answers, context, is_citation_correct),
        citation_any_section=count_passing(answered_ids, answers, context, cites_any_expected_section),
        citation_all_sections=count_passing(answered_ids, answers, context, cites_all_expected_sections),
        correct_and_cited=sum(is_good_answer(question_id, answers[question_id], judgments, context) for question_id in question_ids),
        correct_and_any_section_cited=sum(
            is_good_answer(question_id, answers[question_id], judgments, context, cites_any_expected_section)
            for question_id in question_ids
        ),
        mean_llm_calls=mean(answers[question_id].llm_calls for question_id in question_ids),
        mean_input_tokens=mean(answers[question_id].input_tokens for question_id in question_ids),
        mean_output_tokens=mean(answers[question_id].output_tokens for question_id in question_ids),
        mean_llm_seconds=mean(answers[question_id].llm_seconds for question_id in question_ids),
        mean_reranked_candidates=mean(len(answers[question_id].retrieved_chunks) for question_id in question_ids),
    )


def compute_risk_coverage(
    question_ids: list[str],
    answers: dict[str, GeneratedAnswer],
    judgments: dict[str, Judgment],
    context: EvaluationContext,
    citation_check: CitationCheck = is_citation_correct,
) -> list[RiskCoveragePoint]:
    answered = sorted(
        (
            (
                answers[question_id].confidence,
                is_good_answer(question_id, answers[question_id], judgments, context, citation_check),
            )
            for question_id in question_ids
            if is_answered(answers[question_id])
        ),
        key=lambda pair: pair[0],
        reverse=True,
    )
    points = []
    good_count = 0
    for answered_count, (confidence, is_good) in enumerate(answered, start=1):
        good_count += is_good
        points.append(
            RiskCoveragePoint(
                threshold=confidence, coverage=answered_count / len(question_ids), precision=good_count / answered_count
            )
        )
    return points


def find_coverage_at_precision(points: list[RiskCoveragePoint], min_precision: float) -> float:
    return max((point.coverage for point in points if point.precision >= min_precision), default=0.0)
