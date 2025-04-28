# faiss_index.py
import os
import numpy as np
import faiss
import pickle

VECTOR_DB_DIR = "vector_db"

def create_index() -> str:
    embeddings = np.load(os.path.join(VECTOR_DB_DIR, "embeddings.npy"))
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    faiss.write_index(index, os.path.join(VECTOR_DB_DIR, "index.faiss"))
    return "✅ FAISS index created and saved successfully."

def load_index_and_chunks():
    index = faiss.read_index(os.path.join(VECTOR_DB_DIR, "index.faiss"))
    with open(os.path.join(VECTOR_DB_DIR, "chunks.pkl"), "rb") as f:
        chunks = pickle.load(f)
    return index, chunks
