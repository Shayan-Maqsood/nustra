import json
import os
import sys
import traceback
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer


CHUNKS_FILE = "data/processed/chunks.json"
INDEX_FILE  = "data/chroma_db/index.faiss"
META_FILE   = "data/chroma_db/metadata.json"
MODEL_NAME  = "all-MiniLM-L6-v2"
BATCH_SIZE  = 64

os.makedirs("data/chroma_db", exist_ok=True)


def load_chunks():
    print(f"\nStep 4: Loading chunks from {CHUNKS_FILE}...")
    if not os.path.exists(CHUNKS_FILE):
        print(f"  ERROR: File not found: {CHUNKS_FILE}")
        sys.exit(1)
    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    print(f"  Chunks loaded: {len(chunks)}")
    return chunks


def embed_chunks(chunks, model):
    print(f"\nStep 5: Embedding {len(chunks)} chunks...")
    print(f"  Batch size: {BATCH_SIZE}")

    texts = [c["text"] for c in chunks]
    all_embeddings = []
    total_batches = (len(texts) - 1) // BATCH_SIZE + 1

    for i in range(0, len(texts), BATCH_SIZE):
        try:
            batch = texts[i:i + BATCH_SIZE]
            embeddings = model.encode(batch, show_progress_bar=False)
            all_embeddings.append(embeddings)
            batch_num = i // BATCH_SIZE + 1
            done = min(i + BATCH_SIZE, len(texts))
            print(f"  Batch {batch_num}/{total_batches} done — {done}/{len(texts)} chunks embedded")
        except Exception as e:
            print(f"  ERROR in batch {i // BATCH_SIZE + 1}: {e}")
            traceback.print_exc()
            sys.exit(1)

    result = np.vstack(all_embeddings).astype("float32")
    print(f"\n  Embedding shape: {result.shape}")
    return result


def build_faiss_index(embeddings):
    print(f"\nStep 6: Building FAISS index...")
    try:
        dim = embeddings.shape[1]
        index = faiss.IndexFlatIP(dim)
        faiss.normalize_L2(embeddings)
        index.add(embeddings)
        print(f"  FAISS index built — {index.ntotal} vectors, {dim} dimensions")
        return index
    except Exception as e:
        print(f"  ERROR building FAISS index: {e}")
        traceback.print_exc()
        sys.exit(1)


def save(index, chunks):
    print(f"\nStep 7: Saving index and metadata...")
    try:
        faiss.write_index(index, INDEX_FILE)
        print(f"  Index saved    : {INDEX_FILE}")
    except Exception as e:
        print(f"  ERROR saving FAISS index: {e}")
        traceback.print_exc()
        sys.exit(1)

    try:
        metadata = [
            {
                "title": c["title"],
                "source": c["source"],
                "text": c["text"]
            }
            for c in chunks
        ]
        with open(META_FILE, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        print(f"  Metadata saved : {META_FILE}")
    except Exception as e:
        print(f"  ERROR saving metadata: {e}")
        traceback.print_exc()
        sys.exit(1)


def main():
    print("\n" + "="*50)
    print(" NUSTra Embedder")
    print("="*50)

    print("\nStep 4: Loading model...")
    try:
        model = SentenceTransformer(MODEL_NAME)
        print("  Model loaded OK")
    except Exception as e:
        print(f"  ERROR loading model: {e}")
        traceback.print_exc()
        sys.exit(1)

    chunks = load_chunks()
    embeddings = embed_chunks(chunks, model)
    index = build_faiss_index(embeddings)
    save(index, chunks)

    print("\n" + "="*50)
    print(f" All done! NUST knowledge base is ready.")
    print(f" {index.ntotal} chunks indexed and searchable.")
    print("="*50 + "\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {e}")
        traceback.print_exc()
        sys.exit(1)