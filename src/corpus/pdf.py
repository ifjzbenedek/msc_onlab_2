from pathlib import Path

import pymupdf


def extract_page_texts(pdf_path: Path) -> list[str]:
    with pymupdf.open(pdf_path) as pdf:
        return [page.get_text() for page in pdf]
