import json
from pathlib import Path

from src.corpus.schemas.chunk import Chunk


def save_chunks(chunks: list[Chunk], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    records = [chunk.model_dump() for chunk in chunks]
    json_text = json.dumps(records, ensure_ascii=False, indent=2)
    path.write_text(json_text, encoding="utf-8", newline="\n")


def load_chunks(path: Path) -> list[Chunk]:
    records = json.loads(path.read_text(encoding="utf-8"))
    return [Chunk(**record) for record in records]
