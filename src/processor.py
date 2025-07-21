# src/processor.py

import fitz
import joblib
import os
import pandas as pd
import fitz
from src.config import Config
from src.utils import compute_numbering_level,is_likely_noise,is_invalid_heading

class PDFProcessor:
    """
    Core class for extracting headings and names from a PDF document.
    """
    def __init__(self, model_path, label_map):
        """
        Initializes the PDFProcessor with the classification model, label mapping, and text filters.
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at: {model_path}")
        self.clf = joblib.load(model_path)
        self.label_map = label_map
        

    def extract_headings(self,pdf_path):
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

                    pred = self.clf.predict(features)[0]
                    label = self.label_map.get(pred, "Unlabeled")

                    if label != "Unlabeled" and not is_likely_noise(clean_text):
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
        return result