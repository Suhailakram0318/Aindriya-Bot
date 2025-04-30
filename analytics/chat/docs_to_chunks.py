# docs_to_chunks.py
import os
import tempfile
import numpy as np
import pickle
from typing import List
from sentence_transformers import SentenceTransformer
from fastapi import UploadFile
import fitz  # PyMuPDF
from docx import Document

VECTOR_DB_DIR = "vector_db"
CHUNK_SIZE = 500
os.makedirs(VECTOR_DB_DIR, exist_ok=True)

embedder = SentenceTransformer("all-MiniLM-L6-v2")

def chunk_text(text, size=CHUNK_SIZE):
    return [text[i:i + size] for i in range(0, len(text), size)]

def extract_text(file_path, ext):
    if ext == ".pdf":
        with fitz.open(file_path) as doc:
            return "\n".join(page.get_text() for page in doc)
    elif ext == ".docx":
        doc = Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs)
    elif ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

async def process_uploaded_files(files: List[UploadFile]) -> str:
    all_chunks = []
    all_embeddings = []

    for file in files:
        ext = os.path.splitext(file.filename)[1].lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        content = extract_text(tmp_path, ext)
        os.remove(tmp_path)

        if content:
            chunks = chunk_text(content)
            embeddings = embedder.encode(chunks, convert_to_numpy=True)
            all_chunks.extend(chunks)
            all_embeddings.extend(embeddings)

    np.save(os.path.join(VECTOR_DB_DIR, "embeddings.npy"), all_embeddings)
    with open(os.path.join(VECTOR_DB_DIR, "chunks.pkl"), "wb") as f:
        pickle.dump(all_chunks, f)

    return f"✅ Processed {len(all_chunks)} chunks from the uploaded files."

def process_plain_text(plain_text: str) -> str:
    chunks = chunk_text(plain_text)
    embeddings = embedder.encode(chunks, convert_to_numpy=True)

    np.save(os.path.join(VECTOR_DB_DIR, "embeddings.npy"), embeddings)
    with open(os.path.join(VECTOR_DB_DIR, "chunks.pkl"), "wb") as f:
        pickle.dump(chunks, f)

    return f"✅ Processed {len(chunks)} chunks from the plain text."
