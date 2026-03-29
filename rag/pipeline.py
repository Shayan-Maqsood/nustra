import ollama
from rag.retriever import Retriever

MODEL_NAME = "qwen2.5:3b"

SYSTEM_PROMPT = "You are NUSTra. Answer using ONLY the given context in 1-2 sentences. If not in context, say you don't know."

class RAGPipeline:
    def __init__(self):
        print("Initializing NUSTra RAG Pipeline...")
        self.retriever = Retriever()
        print("Pipeline ready!\n")

    def build_prompt(self, query, chunks):
        best_chunk = chunks[0]['text'].split()[:60]
        context = " ".join(best_chunk)

        return f"Context: {context}\n\nQ: {query}\n\nAnswer:"

    def is_relevant(self, query, chunks):
        if not chunks:
            return False
        if chunks[0]["score"] < 0.5:
            return False
        return True

    def ask(self, query, top_k=3):
        chunks = self.retriever.retrieve(query, top_k=top_k)
        chunks = [c for c in chunks if c["score"] >= 0.4]

        if not self.is_relevant(query, chunks):
            yield "I don't have that specific information. For accurate details, please visit nust.edu.pk or contact the NUST admissions office."
            return

        prompt = self.build_prompt(query, chunks)

        stream = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt}
            ],
            stream=True,
            keep_alive="1h",
            options={
                "num_predict": 200,
                "temperature": 0.0,  
                "num_ctx": 256,     
            }
        )

        for chunk in stream:
            token = chunk["message"].get("content", "")
            if token:
                yield token

    def ask_with_sources(self, query, top_k=3):
        chunks = self.retriever.retrieve(query, top_k=top_k)
        sources = list(set([c["source"] for c in chunks]))
        return chunks, sources