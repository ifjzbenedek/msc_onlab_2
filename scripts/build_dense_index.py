import sys
import time
sys.path.insert(0, ".")

import config
from src.corpus.chunk_file import load_chunks
from src.retrieval.dense import embed_texts, load_embedding_model, save_dense_index, select_device


def main() -> None:
    chunks = load_chunks(config.CHUNKS_PATH)
    model = load_embedding_model(config.EMBED_MODEL, select_device())
    start = time.perf_counter()
    embeddings = embed_texts(model, [chunk.text for chunk in chunks])
    elapsed = time.perf_counter() - start
    save_dense_index(chunks, embeddings, config.DENSE_INDEX_PATH)
    print(f"Embedded {len(chunks)} chunks on {select_device()} in {elapsed:.1f} s, shape {embeddings.shape}")
    print(f"Saved to {config.DENSE_INDEX_PATH}")


if __name__ == "__main__":
    main()
