import os
import tempfile
import time
from pathlib import Path

from src.storage.constants import REPLACE_ATTEMPTS, REPLACE_RETRY_SECONDS, TEMPORARY_FILE_SUFFIX


def replace_with_retries(source: str, target: Path) -> None:
    for attempt in range(1, REPLACE_ATTEMPTS + 1):
        try:
            os.replace(source, target)
            return
        except PermissionError:
            if attempt == REPLACE_ATTEMPTS:
                raise
            time.sleep(REPLACE_RETRY_SECONDS)


def write_text_atomically(path: Path, text: str) -> None:
    file_descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent, prefix=path.name, suffix=TEMPORARY_FILE_SUFFIX
    )
    try:
        with os.fdopen(file_descriptor, "w", encoding="utf-8", newline="\n") as temporary_file:
            temporary_file.write(text)
        replace_with_retries(temporary_name, path)
    finally:
        if os.path.exists(temporary_name):
            os.remove(temporary_name)
