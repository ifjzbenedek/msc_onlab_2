from pathlib import Path

import numpy as np
import torch
from sentence_transformers import SentenceTransformer

from src.corpus.schemas.chunk import Chunk
from src.retrieval.constants import CPU_DEVICE, EMBEDDING_BATCH_SIZE, GPU_DEVICE


def select_device() -> str:
    return GPU_DEVICE if torch.cuda.is_available() else CPU_DEVICE


def load_embedding_model(model_name: str, device: str) -> SentenceTransformer:
    model = SentenceTransformer(model_name, device=device)
    return model.half() if device == GPU_DEVICE else model


def embed_texts(model: SentenceTransformer, texts: list[str]) -> np.ndarray:
    embeddings = model.encode(
        texts, batch_size=EMBEDDING_BATCH_SIZE, normalize_embeddings=True, convert_to_numpy=True
    )
    return embeddings.astype(np.float32)


def save_dense_index(chunks: list[Chunk], embeddings: np.ndarray, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(path, chunk_ids=np.array([chunk.id for chunk in chunks]), embeddings=embeddings)


def load_dense_index(path: Path, chunks: list[Chunk]) -> np.ndarray:
    dense_index = np.load(path)
    if list(dense_index["chunk_ids"]) != [chunk.id for chunk in chunks]:
        raise ValueError("The dense index was built from different chunks, rebuild it")
    return dense_index["embeddings"]


def search_dense(
    model: SentenceTransformer, embeddings: np.ndarray, chunks: list[Chunk], query: str, top_k: int
) -> list[Chunk]:
    query_embedding = embed_texts(model, [query])[0]
    ranked_positions = np.argsort(-(embeddings @ query_embedding))[:top_k]
    return [chunks[position] for position in ranked_positions]
