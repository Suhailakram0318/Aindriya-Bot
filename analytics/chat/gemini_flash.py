# gemini_flash.py
import os
import google.generativeai as genai
import numpy as np
from sentence_transformers import SentenceTransformer

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

def get_llm_response(index, chunks, question: str, history: list = None) -> str:
    question_embedding = embedder.encode([question], convert_to_numpy=True)[0]

    # ✅ Correct unpacking
    distances, indices = index.search(np.array([question_embedding]), k=3)

    # ✅ Now use indices properly
    context = "\n".join([chunks[i] for i in indices[0] if i != -1])

    conversation_history = ""
    if history:
        for pair in history:
            conversation_history += f"User: {pair['user']}\nAssistant: {pair['assistant']}\n"

    prompt = f"""You are a helpful assistant.
Context:
{context}

{conversation_history}
User: {question}
Assistant:"""

    response = model.generate_content(prompt)
    return response.text.strip()
