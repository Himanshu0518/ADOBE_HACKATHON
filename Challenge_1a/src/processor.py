# src/processor.py

import fitz
import joblib
import os
import pandas as pd
from src.config import Config
from src.utils import compute_numbering_level, is_likely_noise

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

    def extract_headings(self, pdf_path):
        doc = fitz.open(pdf_path)
        lines = []
        largest_font_line = {"text": "", "size": 0.0, "page": 1, "is_bold": False, "is_centered": False}
        
        title = "" 
        curr_font_size = 0.0
        prev_y =  0.0 

        for page_num, page in enumerate(doc):
            blocks = page.get_text("dict")["blocks"]
            for b in blocks:
                
                if "lines" not in b:
                    continue

                for l in b["lines"]:
                   # print(l)
                    spans = l["spans"]
                    if not spans:
                        continue

                    spans.sort(key=lambda s: s["bbox"][0])
                    
                    line_text = ""
                    prev_end = 0
                    fonts = []
                    word_count = 0
                    gap_threshold = 10

                    if len(spans) <= 4:
                        for span in spans:
                            x_start = span["bbox"][0]
                            if prev_end and x_start - prev_end > gap_threshold:
                                line_text += " "
                            text = span["text"].strip()
                            print(text,len(text),span["size"],span["bbox"])
                            
                            if not text:
                                continue
                            
                            line_text += text
                            prev_end = span["bbox"][2]
                            fonts.append((span["size"], "Bold" in span["font"], span["font"]))
                            word_count += len(text.split())
                    else:
                        for span in spans:
                            text = span["text"].strip()
                            print(text,len(text),span["size"])
                            if not text:
                                continue
                            line_text += text + " "
                            fonts.append((span["size"], "Bold" in span["font"], span["font"]))
                            word_count += len(text.split())

                    if span["size"] > curr_font_size and page_num == 0 and not is_likely_noise(text):
                                curr_font_size = span["size"]
                                curr_font_size = span["size"]
                                prev_y = span["bbox"][1]
                                title = text
                    if span["size"] == curr_font_size and abs(span["bbox"][1] - prev_y) < 8 and not is_likely_noise(text) and text != title:                             
                                prev_y = span["bbox"][1]
                                title += " " + text

                  #  print(title)
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
                    
                    curr_res = {
                        "level": label,
                        "text": clean_text,
                        "page": page_num + 1
                    }

                    if (label != "Unlabeled" or avg_font_size > 12) and not is_likely_noise(clean_text) and curr_res not in lines:
                        if label != "Unlabeled":
                            lines.append(curr_res)

                    # Enhanced fallback detection for title line
                    if page_num == 0 and (
                        avg_font_size > largest_font_line["size"] or
                        (avg_font_size == largest_font_line["size"] and is_centered and is_bold)
                    ) and len(clean_text.split()) >= 3:
                        largest_font_line = {
                            "text": clean_text,
                            "size": avg_font_size,
                            "page": 1,
                            "is_bold": is_bold,
                            "is_centered": is_centered
                        }

        
        for item in lines:
            if item["level"] == "TITLE" and item["text"].strip() != title.strip():
                item["label"] = "H1"
                break
            if  item["text"].strip() == title.strip():
                item["level"] = "Unlabeled"
                break

        outline = [entry for entry in lines if entry["level"] != "TITLE" and entry["level"] != "Unlabeled"]

        # Fallback: use largest font line from page 1 if no title found
        if not title and largest_font_line["text"]:
            title = largest_font_line["text"]

        # Secondary fallback: use first H1
        if not title:
            for entry in outline:
                if entry["level"].upper() == "H1":
                    title = entry["text"]
                    break

        # Final fallback: use first outline entry
        if not title and outline:
            title = outline[0]["text"]

        result = {
            "title": title,
            "outline": outline
        }

        return result