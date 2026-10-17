import json
from pathlib import Path

from src.eval.schemas.b_set_item import BSetItem


def load_b_set(path: Path) -> list[BSetItem]:
    records = json.loads(path.read_text(encoding="utf-8"))
    return [BSetItem(**record) for record in records]
