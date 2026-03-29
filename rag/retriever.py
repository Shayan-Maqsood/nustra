import json
import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

INDEX_FILE = "data/chroma_db/index.faiss"
META_FILE  = "data/chroma_db/metadata.json"
MODEL_NAME = "all-MiniLM-L6-v2"

class Retriever:
    def __init__(self):
        print("  Loading FAISS index...")
        self.index = faiss.read_index(INDEX_FILE)

        print("  Loading metadata...")
        with open(META_FILE, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)

        print("  Loading embedding model...")
        self.model = SentenceTransformer(MODEL_NAME)
        print("  Retriever ready!\n")

    def retrieve(self, query, top_k=5):
        # Embed the query
        query_vec = self.model.encode([query]).astype("float32")
        faiss.normalize_L2(query_vec)

        # Search FAISS
        scores, indices = self.index.search(query_vec, top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            chunk = self.metadata[idx]
            results.append({
                "text": chunk["text"],
                "source": chunk["source"],
                "title": chunk["title"],
                "score": float(score)
            })

        return results


if __name__ == "__main__":
    retriever = Retriever()

    test_queries = [
        "What are the admission requirements for SEECS?",
        "How much is the fee for BS Computer Science?",
        "What hostel facilities does NUST provide?",
        "Which programs does SMME offer?",
    ]

    for query in test_queries:
        print(f"\n Query: {query}")
        print("-" * 60)
        results = retriever.retrieve(query, top_k=3)
        for i, r in enumerate(results):
            print(f"  [{i+1}] Score: {r['score']:.3f} | {r['title'][:50]}")
            print(f"       {r['text'][:150]}...")