import os
import requests
import numpy as np
import pickle
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from sentence_transformers import SentenceTransformer

VECTOR_DB_DIR = "vector_db"
CHUNK_SIZE = 500
os.makedirs(VECTOR_DB_DIR, exist_ok=True)

embedder = SentenceTransformer("all-MiniLM-L6-v2")

def chunk_text(text, size=CHUNK_SIZE):
    return [text[i:i + size] for i in range(0, len(text), size)]

def extract_text_from_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")

    for script_or_style in soup(["script", "style", "noscript"]):
        script_or_style.extract()

    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)

def crawl_website(base_url: str, max_pages: int = 10):
    visited = set()
    to_visit = [base_url]
    all_text = ""

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        if url in visited:
            continue

        try:
            response = requests.get(url, timeout=5)
            if response.status_code != 200:
                continue
            visited.add(url)

            text = extract_text_from_html(response.content)
            all_text += text + "\n"

            soup = BeautifulSoup(response.content, "html.parser")
            for link_tag in soup.find_all("a", href=True):
                href = link_tag.get("href")
                full_url = urljoin(base_url, href)

                # Only crawl the same domain
                if urlparse(full_url).netloc == urlparse(base_url).netloc:
                    if full_url not in visited and full_url not in to_visit:
                        to_visit.append(full_url)
        except Exception as e:
            print(f"Error visiting {url}: {e}")
            continue

    return all_text

def process_url_content(url: str) -> str:
    try:
        full_text = crawl_website(url, max_pages=10)  # limit to 10 pages for safety
        chunks = chunk_text(full_text)
        embeddings = embedder.encode(chunks, convert_to_numpy=True)

        np.save(os.path.join(VECTOR_DB_DIR, "embeddings.npy"), embeddings)
        with open(os.path.join(VECTOR_DB_DIR, "chunks.pkl"), "wb") as f:
            pickle.dump(chunks, f)

        return f"✅ Crawled and processed {len(chunks)} chunks from the website."
    except Exception as e:
        raise Exception(f"Failed to process URL: {e}")
