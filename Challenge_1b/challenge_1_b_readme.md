# ✨ Challenge 1b: Multi-Collection PDF Analysis

## 🌍 Overview

A smart document understanding pipeline designed to parse and analyze **multiple PDF collections** (Travel, Recipes, Learning Guides) based on the **user persona** and their **task**. It returns **ranked relevant sections** and **refined summaries** in structured JSON format. Perfect for Hackathon-level AI automation and scalable insights.

---

## 🔹 Why This Approach?

| Component             | Why We Chose It                                                                                                                          |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| **SPECTER2**          | A transformer model specialized in **academic & educational texts**. Delivers high-quality semantic embeddings. Works great **offline**. |
| **BM25 (rank\_bm25)** | Traditional lexical search ensures **keyword-level relevance** and **fast filtering** before expensive model inference.                  |
| **PDFMiner**          | A robust, pure-Python library to **extract text from PDF** files, preserving layout when needed.                                         |
| **Custom Chunking**   | Splits large texts intelligently to feed into transformer models effectively.                                                            |
| **JSON I/O**          | Ensures **structured**, **machine-readable** output for future system integration.                                                       |

---

## 📂 Project Structure

```
Challenge_1b/
├── Collection_1/                    # Travel Planning
│   ├── PDFs/                        # South of France guides
│   ├── challenge1b_input.json       # Input config
│   └── challenge1b_output.json      # Output results
├── Collection_2/                    # Adobe Acrobat Learning
│   ├── PDFs/                        # Acrobat tutorials
│   ├── challenge1b_input.json       # Input config
│   └── challenge1b_output.json      # Output results
├── Collection_3/                    # Recipe Collection
│   ├── PDFs/                        # Cooking guides
│   ├── challenge1b_input.json       # Input config
│   └── challenge1b_output.json      # Output results
├── models/                          # SPECTER2 model (offline)
├── main.py                          # Main code
├── requirements.txt                 # Python dependencies
├── Dockerfile                       # Docker setup
├── approach_explanation.md          # Methodology doc
└── README.md                        # This file
```

---

## 🔍 Use Cases by Collection

### 🌍 Collection 1: Travel Planning

- **Challenge ID:** `round_1b_002`
- **Persona:** Travel Planner
- **Task:** Plan a 4-day group trip to South of France
- **Docs:** 7 travel PDFs

### 📄 Collection 2: Adobe Acrobat Learning

- **Challenge ID:** `round_1b_003`
- **Persona:** HR Professional
- **Task:** Setup fillable forms and training for new hires
- **Docs:** 15 tutorial PDFs

### 🍽️ Collection 3: Recipe Collection

- **Challenge ID:** `round_1b_001`
- **Persona:** Food Contractor
- **Task:** Design a vegetarian buffet menu for corporate dinner
- **Docs:** 9 recipe PDFs

---

## 🔸 Input / Output Format

### ✏️ Input (`challenge1b_input.json`)

```json
{
  "challenge_info": {
    "challenge_id": "round_1b_001",
    "test_case_name": "testcase_3"
  },
  "documents": [
    { "filename": "doc.pdf", "title": "Document Title" }
  ],
  "persona": { "role": "HR Manager" },
  "job_to_be_done": { "task": "Create forms for onboarding" }
}
```

### 📈 Output (`challenge1b_output.json`)

```json
{
  "metadata": {
    "input_documents": ["doc.pdf"],
    "persona": "HR Manager",
    "job_to_be_done": "Create forms for onboarding"
  },
  "extracted_sections": [
    {
      "document": "doc.pdf",
      "section_title": "How to Create Fillable Forms",
      "importance_rank": 1,
      "page_number": 2
    }
  ],
  "subsection_analysis": [
    {
      "document": "doc.pdf",
      "refined_text": "To create a form...",
      "page_number": 2
    }
  ]
}
```

---

## 🚀 How to Run

### Option 1: Local

```bash
# Setup
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Run the main pipeline
python main.py
```

### Option 2: Docker

```bash
docker build -t persona-doc-intel .
docker run --rm -v ${PWD}:/app persona-doc-intel
```

---

## 💼 Deliverables

- `main.py` — Entry script
- `approach_explanation.md` — 300-500 words on design + strategy
- `Dockerfile` — For containerized setup
- `requirements.txt` — Required packages
- Sample I/O JSONs

---

## 🔧 Technologies Used

- `pdfminer.six`
- `rank_bm25`
- `sentence-transformers`
- `transformers`
- `torch`
- Offline model: `allenai/specter2` (Size: \~430MB)

---

## 📅 Timeline Benchmarks

- **Execution Time:** ∼ 45–60 seconds per collection
- **Output Size:** ∼ 5–15 refined sections
- **Model Load:** Offline, no HuggingFace API calls

---

> ✨ This pipeline offers a scalable solution for intelligent document analysis and was optimized for performance, precision, and clarity during the Adobe Hackathon 2025.

---

