# hf_mistral.py
import os
from dotenv import load_dotenv
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch

# Load the Hugging Face token from .env
load_dotenv()
hf_token = os.getenv("HF_TOKEN")

model_name = "mistralai/Mistral-7B-Instruct-v0.1"

tokenizer = AutoTokenizer.from_pretrained(model_name, use_auth_token=hf_token)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="auto",
    torch_dtype=torch.float16,
    use_auth_token=hf_token
)

generator = pipeline("text-generation", model=model, tokenizer=tokenizer)

def get_llm_response(context, question):
    prompt = f"""<|system|>\nYou are a helpful assistant.\n<|user|>\nContext:\n{context}\n\nQuestion: {question}\n<|assistant|>"""

    response = generator(
        prompt,
        max_new_tokens=256,
        do_sample=True,
        temperature=0.7,
        pad_token_id=tokenizer.eos_token_id
    )[0]["generated_text"]

    return response[len(prompt):].strip()
