from pydantic import BaseModel


class AnswerSummary(BaseModel):
    questions: int
    answered: int
    correct: int
    partially_correct: int
    citation_correct: int
    citation_any_section: int
    citation_all_sections: int
    correct_and_cited: int
    correct_and_any_section_cited: int
    mean_llm_calls: float
    mean_input_tokens: float
    mean_output_tokens: float
    mean_llm_seconds: float
    mean_reranked_candidates: float
