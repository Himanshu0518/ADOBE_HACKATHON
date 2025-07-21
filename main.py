import fitz
import json
import re
import numpy as np
import pandas as pd
import joblib
from nltk.corpus import stopwords

# 📚 Load multilingual stopwords once
all_stopwords = set()
for lang in stopwords.fileids():
    all_stopwords.update(stopwords.words(lang))

# 🔍 Load model
clf = joblib.load("hackathon_model.joblib")

# 📘 Label mapping
label_map = {
    np.int64(0): 'Unlabeled', # Body texts
    np.int64(1): 'H1',
    np.int64(2): 'H2',
    np.int64(3): 'H3',
    np.int64(4): 'TITLE'
}

# 🔢 Numbering level
def compute_numbering_level(text):
    match = re.match(r"^(\d+(\.\d+)+)", text.strip())
    if match:
        return match.group(1).count('.') + 1
    elif re.match(r"^\d+\.", text.strip()):
        return 1
    return 0

# ❌ Advanced multilingual noise filter
# (Your existing imports and global variables)

# ❌ Advanced multilingual noise filter (Enhanced)
def is_likely_noise(text):
    text = text.strip()
    text_lower = text.lower()

    if not text or len(text) < 3:
        return True
    
    # Existing number/dot only and [number] patterns
    if re.fullmatch(r"[\d.]+", text):
        return True
    if re.match(r"^\[\d+\]$", text):
        return True

    # New: Check for author list patterns (common in first page)
    # This is a heuristic and might need tuning based on specific PDFs
    if re.search(r'^\w+\s\w+(\s[A-Z]\.)?(\*|†|‡)?$', text) and len(text.split()) < 5:
        return True

    # Existing figure/table, arxiv, doi, email, institution names
    if re.search(r'\bfigure\b|\btable\b|\breference\b|\bappendix\b', text_lower):
        return True
    if any(w in text_lower for w in ['arxiv', 'doi', '@', '.com', '.edu', 'university', 'institute', 'gmail', 'google', 'brain', 'proceedings', 'journal', 'conference']):
        return True
    
    # New: Detect common mathematical/equation patterns
    if re.search(r'^((\(?\w+\)?\s*[\+\-\*/=<>≤≥]\s*\w+\(?\w+\)?)|(\w+\s*=\s*\w+[\+\-\*/].*?))$', text.replace(" ", "")):
        return True
    
    # New: Very short lines that are likely just single words or fragments not serving as headings (e.g., column headers)
    if len(text.split()) <= 2 and not text.istitle() and not text.isupper():
        return True

    # Stopword-based filter
    words = re.findall(r'\w+', text_lower)
    if words:
        stop_count = sum(1 for w in words if w in all_stopwords)
        if stop_count / len(words) > 0.8:
            return True

    return False

def is_invalid_heading(text):
    """
    Remove headings that are very likely to be garbage or misclassified.
    """
    text = text.strip().lower()

    # Filter based on bad patterns (existing and enhanced)
    if len(text) < 3:
        return True
    if text in {"<eos>", "√dk", "abstract", "introduction", "conclusion", "references", "appendix", "acknowledgements"}: # Add common section names that might be misclassified as lower headings
        return True
    
    # Enhanced number/symbol only filter
    if re.fullmatch(r"[\d\.\-\–—=~_\[\]()+\-*/^%\\.,\s]+", text) and sum(c.isalpha() for c in text) < 2:
        return True
    
    # Existing very short alpha like "B", "P"
    if re.match(r"^[a-zA-Z]{1,2}$", text):
        return True
    
    # Existing mostly math/code
    if re.match(r"^[a-z0-9\[\]()+=/*^%\\.-]+$", text):
        return True
    
    # Too few actual letters (re-evaluate threshold)
    if sum(c.isalpha() for c in text) < 4 and len(text.split()) > 1: # Increased threshold, and consider word count
        return True

    # Ends with ".", not likely a proper heading (and short length)
    if text.endswith(".") and len(text.split()) < 6: # Slightly increased word count for this rule
        return True
        
    # New: Check for lines that are predominantly digits and punctuation, even if not fully numeric
    if re.fullmatch(r"[\d\s\W]+", text) and sum(c.isalpha() for c in text) == 0:
        return True

    return False

# (Your existing convert_types, extract_headings, and main execution block)

# 🔄 Convert numpy to JSON
def convert_types(obj):
    if isinstance(obj, dict):
        return {k: convert_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_types(i) for i in obj]
    elif isinstance(obj, (np.integer, pd.Int64Dtype, pd.Int32Dtype)):
        return int(obj)
    elif isinstance(obj, (np.floating, pd.Float64Dtype)):
        return float(obj)
    else:
        return obj

# 📌 Main function
def extract_headings(pdf_path, output_path):
    doc = fitz.open(pdf_path)
    lines = []

    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if "lines" not in b:
                continue
            for l in b["lines"]:
                spans = l["spans"]
                if not spans:
                    continue

                spans.sort(key=lambda s: s["bbox"][0])
                line_text = ""
                prev_end = 0
                fonts = []
                word_count = 0
                gap_threshold = 30

                if len(spans) <= 4:
                    for span in spans:
                        x_start = span["bbox"][0]
                        if prev_end and x_start - prev_end > gap_threshold:
                            line_text += " "
                        text = span["text"].strip()
                        if not text:
                            continue
                        line_text += text
                        prev_end = span["bbox"][2]
                        fonts.append((span["size"], "Bold" in span["font"], span["font"]))
                        word_count += len(text.split())
                else:
                    for span in spans:
                        text = span["text"].strip()
                        if not text:
                            continue
                        line_text += text + " "
                        fonts.append((span["size"], "Bold" in span["font"], span["font"]))
                        word_count += len(text.split())

                clean_text = line_text.strip()
                if not clean_text:
                    continue

                avg_font_size = sum(f[0] for f in fonts) / len(fonts)
                is_bold = any(f[1] for f in fonts)
                y_positions = [span["bbox"][1] for span in spans]
                line_spacing = abs(max(y_positions) - min(y_positions)) if len(y_positions) > 1 else 0

                x0 = spans[0]["bbox"][0]
                x_center = (spans[0]["bbox"][0] + spans[-1]["bbox"][2]) / 2
                page_width = page.rect.width
                is_centered = int(page_width * 0.3 < x_center < page_width * 0.7)

                numbering_level = compute_numbering_level(clean_text)

                features = pd.DataFrame([{
                    "font_size": avg_font_size,
                    "numbering_level": numbering_level,
                    "x_position": x0,
                    "line_spacing": line_spacing,
                    "num_words": word_count,
                    "is_centered": is_centered
                }])

                pred = clf.predict(features)[0]
                label = label_map.get(pred, "Unlabeled")
                
                if label != "Unlabeled" and not is_likely_noise(clean_text) and not is_invalid_heading(clean_text):

                    lines.append({
                        "level": label,
                        "text": clean_text,
                        "page": page_num + 1
                    })

    title = ""
    for item in lines:
        if item["level"] == "TITLE" and item["page"] == 1:
            title = item["text"]
            break

    outline = [entry for entry in lines if entry["level"] != "TITLE"]

    if not title and not outline:
        print("⚠️ No valid headings or title found. Output not saved.")
        return

    result = {
        "title": title,
        "outline": outline
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(convert_types(result), f, indent=2, ensure_ascii=False)

    print(f"✅ Extracted outline saved to {output_path}")

# 🟢 Run
if __name__ == "__main__":
    extract_headings(
        "input/attention_all_you_need.pdf",
        "output/output.json"
    )
