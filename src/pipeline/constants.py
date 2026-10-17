from src.retrieval.constants import RERANK_CANDIDATE_COUNT

ANSWER_CONTEXT_CHUNK_COUNT = 3
LLM_CALLS_PER_ANSWER = 1
LLM_CALLS_PER_CRITIC = 1
HIGH_RELIABILITY = "high"
MEDIUM_RELIABILITY = "medium"
HIGH_RELIABILITY_MIN_CONFIDENCE = 0.5
RELATED_CHUNK_COUNT = 1

CRAG_CORRECT_THRESHOLD = 0.05
CRAG_INCORRECT_THRESHOLD = 0.01
EXPANDED_CANDIDATE_COUNTS = (20, 30)
CRAG_CANDIDATE_COUNTS = (RERANK_CANDIDATE_COUNT, *EXPANDED_CANDIDATE_COUNTS)
CORRECT_DECISION = "correct"
AMBIGUOUS_DECISION = "ambiguous"
INCORRECT_DECISION = "incorrect"

FULL_SUPPORT = "full"
PARTIAL_SUPPORT = "partial"
NO_SUPPORT = "none"
CRITIC_CONFIDENCE_FACTORS = {FULL_SUPPORT: 1.0, PARTIAL_SUPPORT: 0.5, NO_SUPPORT: 0.0}
CRITIC_USER_PROMPT_TEMPLATE = "Kérdés:\n{question}\n\nVálasz:\n{answer}\n\nA hivatkozott szabályzat-részletek:\n\n{context}"
CRITIC_SCHEMA = {
    "type": "object",
    "properties": {
        "support": {"type": "string", "enum": [FULL_SUPPORT, PARTIAL_SUPPORT, NO_SUPPORT]},
        "reason": {"type": "string"},
    },
    "required": ["support", "reason"],
    "additionalProperties": False,
}

ANSWER_USER_PROMPT_TEMPLATE = "Kérdés:\n{question}\n\nSzabályzat-részletek:\n\n{context}"
CONTEXT_BLOCK_TEMPLATE = "[{chunk_id}]\n{text}"
CONTEXT_BLOCK_SEPARATOR = "\n\n"
CHUNK_HEADER_SEPARATOR = "\n"

ANSWER_SCHEMA = {
    "type": "object",
    "properties": {
        "answerable": {"type": "boolean"},
        "answer": {"type": "string"},
        "cited_chunk_ids": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["answerable", "answer", "cited_chunk_ids"],
    "additionalProperties": False,
}
