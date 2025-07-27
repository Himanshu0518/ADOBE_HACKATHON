
# ✅ CELL 2: Imports and Setup
import os
import time
import json
from pdfminer.high_level import extract_text
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer, util
import numpy as np
from pathlib import Path
import re

print("Setup complete ✅")

# ✅ CELL 3: Configuration
BASE_PATH = "."  # ← Set to current directory
PDF_FOLDER_NAME = "PDFs"
INPUT_JSON = "challenge1b_input.json"
OUTPUT_JSON = "challenge1b_output.json"
MODEL_NAME = os.path.join(BASE_PATH, "models", "specter2")

# Ensure completely offline mode with fallback message
model_required_files = ["config.json", "pytorch_model.bin", "tokenizer.json"]
if not Path(MODEL_NAME).exists() or not all(Path(MODEL_NAME, f).exists() for f in model_required_files):
    raise FileNotFoundError(
        f"❌ Model not found in '{MODEL_NAME}'. Please download it manually from Hugging Face:\n"
        f"https://huggingface.co/allenai/specter2_base and place the files inside 'Challenge_1b/models/specter2/'"
    )

model = SentenceTransformer(MODEL_NAME, device='cpu')

# ✅ CELL 4: Discover Collections
collections = [d for d in os.listdir(BASE_PATH) if os.path.isdir(os.path.join(BASE_PATH, d)) and d.startswith("Collection")]
print(f"Found {len(collections)} collections:", collections)

# ✅ CELL 5: Utilities
def extract_chunks_from_pdf(pdf_path, chunk_size=180):
    text = extract_text(pdf_path)
    words = text.split()
    return [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

def bm25_top_chunks(query, chunks, meta_info, top_k=60):
    bm25 = BM25Okapi([chunk.lower().split() for chunk in chunks])
    query_tokens = query.lower().split()
    scores = bm25.get_scores(query_tokens)
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
    return [(chunks[i], meta_info[i]) for i in top_indices]

def rerank_chunks(query, candidate_chunks):
    texts = [chunk[0] for chunk in candidate_chunks]
    chunk_embeddings = model.encode(texts, convert_to_tensor=True, show_progress_bar=False)
    query_embedding = model.encode(query, convert_to_tensor=True, show_progress_bar=False)
    cos_scores = util.pytorch_cos_sim(query_embedding, chunk_embeddings)[0]
    top_results = np.argsort(-cos_scores.cpu().numpy())
    return top_results, cos_scores

def smart_title(text):
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    words = text.strip().split()
    return ' '.join(words[:6]).capitalize() if len(words) >= 6 else 'Untitled Section'

def clean_refined_text(text):
    return re.sub(r'\s+', ' ', text).strip()[:420] + ('...' if len(text) > 420 else '')

def create_output_json(ranked_indices, candidates, scores, persona, job):
    output = {
        "metadata": {
            "input_documents": list(set([meta["document"] for _, meta in candidates])),
            "persona": persona,
            "job_to_be_done": job,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        },
        "extracted_sections": [],
        "subsection_analysis": []
    }
    doc_counter = {}
    for idx in ranked_indices:
        chunk_text, meta = candidates[idx]
        doc = meta["document"]
        if doc_counter.get(doc, 0) >= 2:
            continue
        doc_counter[doc] = doc_counter.get(doc, 0) + 1
        rank = len(output["extracted_sections"]) + 1
        output["extracted_sections"].append({
            "document": doc,
            "section_title": smart_title(chunk_text),
            "importance_rank": rank,
            "page_number": meta["page_number"]
        })
        output["subsection_analysis"].append({
            "document": doc,
            "refined_text": clean_refined_text(chunk_text),
            "page_number": meta["page_number"]
        })
        if rank == 6:
            break
    return output

# ✅ CELL 6: Process Each Collection
for collection in collections:
    print(f"\n🔍 Processing collection: {collection}")
    col_path = os.path.join(BASE_PATH, collection)
    pdf_dir = os.path.join(col_path, PDF_FOLDER_NAME)
    input_json_path = os.path.join(col_path, INPUT_JSON)
    output_json_path = os.path.join(col_path, OUTPUT_JSON)

    with open(input_json_path) as f:
        input_data = json.load(f)

    persona = input_data["persona"]["role"]
    job = input_data["job_to_be_done"]["task"]
    persona_job_text = f"{persona}. Job: {job}"

    all_chunks = []
    all_meta = []

    for doc in input_data["documents"]:
        filename = doc["filename"]
        full_path = os.path.join(pdf_dir, filename)
        chunks = extract_chunks_from_pdf(full_path)
        for idx, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            all_meta.append({"document": filename, "page_number": idx + 1})

    print(f"Total chunks: {len(all_chunks)}")

    start_time = time.time()
    bm25_top = bm25_top_chunks(persona_job_text, all_chunks, all_meta)
    rerank_indices, scores = rerank_chunks(persona_job_text, bm25_top)
    final_json = create_output_json(rerank_indices, bm25_top, scores, persona, job)

    with open(output_json_path, "w") as f:
        json.dump(final_json, f, indent=2)

    print(f"✅ Output saved to {output_json_path}")
    print(f"⏱️ Time taken: {time.time() - start_time:.2f} seconds")
