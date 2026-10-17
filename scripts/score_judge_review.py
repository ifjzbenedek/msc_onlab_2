import argparse
import sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, ".")

import config
from src.eval.answer_judge import load_judgments
from src.eval.constants import CORRECT_VERDICT, JUDGE_REVIEW_SYSTEM
from src.eval.judge_review import compute_agreement, compute_cohens_kappa, load_written_verdicts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verdicts", type=Path, default=config.JUDGE_REVIEW_VERDICTS_PATH)
    verdicts_path = parser.parse_args().verdicts
    judgments = load_judgments(config.judgments_path(JUDGE_REVIEW_SYSTEM))
    pairs = [
        (human_verdict, judgments[question_id].verdict)
        for question_id, human_verdict in load_written_verdicts(verdicts_path).items()
    ]
    if not pairs:
        raise SystemExit(f"No verdicts in {verdicts_path}")
    binary_pairs = [(human == CORRECT_VERDICT, judge == CORRECT_VERDICT) for human, judge in pairs]
    print(f"{len(pairs)} reviewed cases (human vs. LLM judge)")
    print(f"  3 levels:       agreement {compute_agreement(pairs):.2f}, Cohen's kappa {compute_cohens_kappa(pairs):.2f}")
    print(
        f"  correct or not: agreement {compute_agreement(binary_pairs):.2f},"
        f" Cohen's kappa {compute_cohens_kappa(binary_pairs):.2f}"
    )
    for (human, judge), count in sorted(Counter(pairs).items()):
        print(f"    human {human:17} judge {judge:17} {count}")


if __name__ == "__main__":
    main()
