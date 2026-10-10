import sys
sys.path.insert(0, ".")

import config
from src.corpus.chunk_file import save_chunks
from src.corpus.chunking import chunk_document
from src.corpus.constants import CORPUS_DOCUMENTS, SKIPPED_PAGES_BY_DOCUMENT
from src.corpus.pdf import read_document_lines
from src.corpus.sections import split_into_sections


def main() -> None:
    chunks = []
    for document in CORPUS_DOCUMENTS:
        skipped_pages = SKIPPED_PAGES_BY_DOCUMENT.get(document, set())
        lines = read_document_lines(config.SOURCE_PDF_DIR.joinpath(document), skipped_pages)
        sections = split_into_sections(lines)
        document_chunks = chunk_document(document, sections)
        chunks += document_chunks
        print(f"{document}: {len(lines)} lines, {len(sections)} sections, {len(document_chunks)} chunks")

    save_chunks(chunks, config.CHUNKS_PATH)
    print(f"Saved {len(chunks)} chunks to {config.CHUNKS_PATH}")


if __name__ == "__main__":
    main()
