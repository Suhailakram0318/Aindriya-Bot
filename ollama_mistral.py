# 3_ollama_mistral.py
from ollama import Client

client = Client()

def get_llm_response(context, question):
    prompt = f"""You are a helpful assistant.
Context:
{context}

Question: {question}
Answer:"""

    response = client.chat(
        model="mistral",
        messages=[{"role": "user", "content": prompt}]
    )
    return response['message']['content']
