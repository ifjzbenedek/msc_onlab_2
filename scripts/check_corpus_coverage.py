import statistics
import sys
sys.path.insert(0, ".")

import config
from src.corpus.chunk_file import load_chunks
from src.corpus.constants import CORPUS_DOCUMENTS
from src.corpus.pdf import extract_page_texts
from src.eval.constants import LETTER_WORD_PATTERN, MIN_PASSAGE_COVERAGE
from src.eval.corpus_coverage import build_corpus_ngrams, measure_corpus_coverage
from src.eval.overlap import find_boilerplate_ngrams
from src.eval.qa_dataset import load_qa_items
from src.eval.splits import load_id_list


def main() -> None:
    chunks = load_chunks(config.CHUNKS_PATH)
    qa_items = load_qa_items(config.PREPARED_QA_PATH)
    excluded_ids = set(load_id_list(config.EXCLUDED_IDS_PATH))
    sampled_ids = set(load_id_list(config.DEV_IDS_PATH)) | set(load_id_list(config.TEST_IDS_PATH))

    for document in CORPUS_DOCUMENTS:
        corpus_ngrams = build_corpus_ngrams([chunk for chunk in chunks if chunk.document == document])
        page_texts = extract_page_texts(config.SOURCE_PDF_DIR.joinpath(document))
        ignored_ngrams = find_boilerplate_ngrams(page_texts, LETTER_WORD_PATTERN)
        coverage_by_id = {
            qa_item.id: measure_corpus_coverage(qa_item, corpus_ngrams, ignored_ngrams)
            for qa_item in qa_items
            if qa_item.source_document == document and qa_item.id not in excluded_ids
        }
        low_ids = sorted(qa_id for qa_id, coverage in coverage_by_id.items() if coverage < MIN_PASSAGE_COVERAGE)
        low_sampled_ids = [qa_id for qa_id in low_ids if qa_id in sampled_ids]
        median_coverage = statistics.median(coverage_by_id.values())
        print(f"{document}: {len(coverage_by_id)} questions, median coverage {median_coverage:.2f}")
        print(f"  below {MIN_PASSAGE_COVERAGE}: {len(low_ids)}, of which in dev/test: {low_sampled_ids}")


if __name__ == "__main__":
    main()
