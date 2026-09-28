import sys
sys.path.insert(0, ".")

import config
from src.corpus.pdf import extract_page_texts
from src.eval.duplicates import merge_duplicate_questions
from src.eval.overlap import find_boilerplate_ngrams
from src.eval.page_spans import add_spanned_pages
from src.eval.qa_dataset import load_qa_items, save_qa_items
from src.eval.splits import comes_from_cover_or_toc, draw_stratified_splits, save_id_list


def main() -> None:
    raw_items = load_qa_items(config.RAW_QA_PATH)
    qa_items = merge_duplicate_questions(raw_items)

    documents = sorted({qa_item.source_document for qa_item in qa_items})
    page_texts_by_document = {
        document: extract_page_texts(config.SOURCE_PDF_DIR.joinpath(document))
        for document in documents
    }
    ignored_ngrams_by_document = {
        document: find_boilerplate_ngrams(page_texts)
        for document, page_texts in page_texts_by_document.items()
    }
    add_spanned_pages(qa_items, page_texts_by_document, ignored_ngrams_by_document)

    excluded_ids = [qa_item.id for qa_item in qa_items if comes_from_cover_or_toc(qa_item)]
    eligible_items = [qa_item for qa_item in qa_items if not comes_from_cover_or_toc(qa_item)]
    dev_ids, test_ids = draw_stratified_splits(eligible_items)

    save_qa_items(qa_items, config.PREPARED_QA_PATH)
    save_id_list(dev_ids, config.DEV_IDS_PATH)
    save_id_list(test_ids, config.TEST_IDS_PATH)
    save_id_list(excluded_ids, config.EXCLUDED_IDS_PATH)

    print(f"Questions: {len(raw_items)} -> {len(qa_items)} after merging duplicates")
    print(f"Excluded (cover and table of contents): {len(excluded_ids)}")
    print(f"Dev: {len(dev_ids)}, test: {len(test_ids)}")


if __name__ == "__main__":
    main()
