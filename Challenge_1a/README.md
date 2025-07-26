# 📘 Adobe Hackathon Round 1A – Document Outline Extractor

## 🔍 Challenge Brief

As part of **Round 1A** of Adobe’s *“Connecting the Dots”* Hackathon, the goal is to build a system that extracts a **structured outline** from a raw PDF. This outline includes:

* **Title**
* Headings categorized as **H1**, **H2**, or **H3**
* Each heading’s **page number**

The extracted information must be output in a specific JSON format, and the solution must be containerized using Docker, work offline, and run on CPU-only systems.

---

## 🧠 Approach

Our approach combines layout-aware PDF parsing using `PyMuPDF` with a lightweight **machine learning classifier** that determines heading levels based on structural and typographic features.

### 🔧 Step-by-step Overview

1. **PDF Parsing with PyMuPDF (****`fitz`****)**:

   * Extract all text blocks with position, font size, font name, and bounding boxes.
   * Collect metadata such as line spacing, number of words, and relative x-positions.

2. **Feature Extraction**:
   For each text block, we extract the following features:

   * `font_size`
   * `line_spacing` (gap between current and previous block)
   * `num_words`
   * `x_position` (left margin)
   * `numbering_level` (e.g., starts with “1.”, “1.1”, etc.)

3. **ML-Based Heading Classification**:

   - A lightweight trained classifier (e.g., fine-tuned **XGBoost** model with **Optuna** for hyperparameter tuning) is used to predict heading levels — **H1**, **H2**, **H3** — based on extracted features .
   - This model helps maintain consistency across PDFs with varying layout structures by learning the patterns.

4. **Title Extraction**:

   * The largest non-repetitive text block on the **first page** is selected as the **title**.

5. **JSON Output**:

   * The result is formatted as:

   ```json
   {
     "title": "Sample Title",
     "outline": [
       { "level": "H1", "text": "Chapter 1", "page": 2 },
       { "level": "H2", "text": "Section 1.1", "page": 3 }
     ]
   }
   ```

---

## 🚀 How to Run

### 1. Clone the Repository

```bash
git https://github.com/Himanshu0518/ADOBE_HACKATHON.git
cd ADOBE_HACKATHON
cd Challenge_1a 
```

### 2. Build Docker Image

```bash
docker build --platform linux/amd64 -t adobe-hackathon .
```

### 3. Run Docker Container

```bash
docker run --rm -v ${PWD}/input:/app/input -v ${PWD}/output:/app/output --network none adobe-hackathon
```

> 📁 `/Challenge_1a/input`: place your `.pdf` files here
> 📁 `/Challenge_1a/output`: `.json` files will be generated here

---

## 📂 Input/Output Format

* **Input**: PDF files (up to 50 pages), placed in the `/input` folder.
* **Output**: Corresponding `.json` files with the extracted outline, saved in the `/output` folder.

---

## 📌 Constraints & Compatibility

| Constraint           | Status ✅ |
| -------------------- | -------- |
| Runs offline         | ✅        |
| CPU-only execution   | ✅        |
| Model size < 200MB   | ✅        |
| Execution time < 10s | ✅        |
| Docker (linux/amd64) | ✅        |
| multilingual         | ✅        |
---

## 📚 Libraries & Dependencies

* Python 3.10
* [`PyMuPDF`](https://pymupdf.readthedocs.io/) (`fitz`) — PDF parsing
* `scikit-learn` — ML model inference
* `joblib` — For loading the trained model
* `numpy`, `pandas` — Feature processing
* `json`, `os`, `re` — Core modules

---

## 📁 Project Structure

```

├── Challenge_1a/
│   ├── input/                      # Input PDFs
│   ├── output/                     # Output JSONs
│   ├── model/                      # Trained ML model (joblib)
│   ├── src/                        # Source files (e.g., config, utils)
│   ├── from_root.py                # Entry script
│   ├── Dockerfile                  # Docker setup
│   ├── requirements.txt            # Dependencies
│   └── README.md                   # Documentation

```

---

## 🧪 Example Output

For `document.pdf`, the tool generates `document.json`:

```json
{
  "title": "Understanding AI",
  "outline": [
    { "level": "H1", "text": "Introduction", "page": 1 },
    { "level": "H2", "text": "What is AI?", "page": 2 },
    { "level": "H3", "text": "History of AI", "page": 3 }
  ]
}
```

---

## 📊 Model Performance


### 📊 Classification Report

| Label   | Precision | Recall | F1-Score | Support |
|:--------|----------:|-------:|---------:|--------:|
| body    |     0.97  |  0.91  |    0.94  |      32 |
| H1      |     0.88  |  0.97  |    0.92  |      30 |
| H2      |     0.89  |  0.84  |    0.86  |      19 |
| H3      |     0.67  |  0.67  |    0.67  |       9 |
| title   |     0.80  |  0.80  |    0.80  |       5 |
|         |           |        |          |         |
| **Accuracy**     |        |        |  **0.88** |      95 |
| **Macro Avg**    |     0.84  |  0.84  |    0.84  |      95 |
| **Weighted Avg** |     0.89  |  0.88  |    0.88  |      95 |


### 📈 Learning Curve

![Learning Curve](https://github.com/Himanshu0518/Assets/raw/main/learning_curve.png)


## 📁 Dataset Used

* Custom-labeled dataset of 120 PDFs from academic reports, tech manuals, and public documents
* Features extracted: `font_size`, `line_spacing`, `num_words`, `x_position`, `numbering_level`
* Labeled manually for heading levels (H1, H2, H3)
* Not publicly released due to copyright sensitivity


## 📝 Known Limitations

* ❌ Scanned or image-based PDFs are not supported (OCR planned in future)
* ❌ Minor misclassification may occur with inconsistent fonts or exotic layouts
* ❌ semantic similarity not implemented due to time and size constraints
* ❌ Model may be a bit overfitted due to lack of data 

---

## 💡 Future Work

* Explore OCR fallback for scanned PDFs
* Improve model with more training data for generalization

---


> ✨ This project was built for Adobe India Hackathon 2025 - Round 1A
