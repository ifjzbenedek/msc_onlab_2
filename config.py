import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT.joinpath(".env"))

DATASET_DIR = ROOT.joinpath(os.getenv("DATASET_DIR", "../hybrid_rag_qa_dataset")).resolve()
DATA_DIR = ROOT.joinpath("data")

RAW_QA_PATH = DATASET_DIR.joinpath("qa_retrieval_2197.json")
SOURCE_PDF_DIR = DATASET_DIR.joinpath("pdf")

PREPARED_QA_PATH = DATA_DIR.joinpath("eval", "qa_retrieval.json")

SPLITS_DIR = DATA_DIR.joinpath("splits")
DEV_IDS_PATH = SPLITS_DIR.joinpath("dev.txt")
TEST_IDS_PATH = SPLITS_DIR.joinpath("test.txt")
EXCLUDED_IDS_PATH = SPLITS_DIR.joinpath("excluded.txt")

LLM_CLI = os.getenv("LLM_CLI", "")
LLM_MODEL = os.getenv("LLM_MODEL", "")
LLM_WORKERS = int(os.getenv("LLM_WORKERS", "4"))

EMBED_MODEL = os.getenv("EMBED_MODEL", "BAAI/bge-m3")
RERANK_MODEL = os.getenv("RERANK_MODEL", "BAAI/bge-reranker-v2-m3")
