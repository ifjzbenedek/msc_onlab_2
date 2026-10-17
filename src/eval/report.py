from src.eval.schemas.recall_result import RecallResult


def format_rates(rates: dict[int, float]) -> str:
    return " ".join(f"{rate:.2f}" for rate in rates.values())


def format_recall(result: RecallResult) -> str:
    return (
        f"text {format_rates(result.text)} | any § {format_rates(result.any_section)}"
        f" | all § {format_rates(result.all_sections)}"
    )
