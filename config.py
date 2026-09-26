import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

DATASET_DIR = (ROOT / os.getenv("DATASET_DIR", "../hybrid_rag_qa_dataset")).resolve()
DATA_DIR = ROOT / "data"

LLM_CLI = os.getenv("LLM_CLI", "")
LLM_MODEL = os.getenv("LLM_MODEL", "")
LLM_WORKERS = int(os.getenv("LLM_WORKERS", "4"))

EMBED_MODEL = os.getenv("EMBED_MODEL", "BAAI/bge-m3")
RERANK_MODEL = os.getenv("RERANK_MODEL", "BAAI/bge-reranker-v2-m3")
