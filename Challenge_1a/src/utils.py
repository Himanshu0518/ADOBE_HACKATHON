# pdf_parser/utils.py

import re
import json
import numpy as np
import pandas as pd
from nltk.corpus import stopwords

# ✅ Load multilingual stopwords only once globally
all_stopwords = set()
for lang in stopwords.fileids():
    all_stopwords.update(stopwords.words(lang))

def load_stopwords(languages):
    """(Optional) Loads multilingual stopwords from NLTK (if needed separately)."""
    all_sw = set()
    for lang in languages:
        all_sw.update(stopwords.words(lang))
    return all_sw

def compute_numbering_level(text):
    match = re.match(r"^(\d+(\.\d+)+)", text.strip())
    if match:
        return match.group(1).count('.') + 1
    elif re.match(r"^\d+\.", text.strip()):
        return 1
    return 0

def convert_types(obj):
    """Converts numpy types to standard Python types for JSON serialization."""
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

def is_likely_noise(text):
    text = text.strip()
    text_lower = text.lower()

    # Empty or very short text
    if not text or len(text) < 3:
        return True

    #  Divider lines (dashes, equals, stars, underscores)
    if re.match(r"^[\-=_*~]{3,}$", text):
        return True


    # Starts with bracket (often inline references like “[1]”, “(c)”)
    if text.startswith("(") or text.startswith("["):
        return True

  
    if any(w in text_lower for w in ['arxiv', 'doi', '@', '.com', '.edu', 'university',
                                     'institute', 'gmail', 'google', 'brain', 'proceedings',
                                     ]):
        return True

    # Math-like
    if re.search(r'^((\(?\w+\)?\s*[\+\-\*/=<>≤≥]\s*\w+\(?\w+\)?)|(\w+\s*=\s*\w+[\+\-\*/].*?))$',
                 text.replace(" ", "")):
        return True

  

    ignore_chars = set(" -&’'.,")
    symbol_heavy_chars = [c for c in text if not c.isalpha() and c not in ignore_chars]
    if len(symbol_heavy_chars) / len(text) > 0.5:
        return True

    # Stopword-heavy lines
    words = re.findall(r'\w+', text_lower)
    if words:
        stop_count = sum(1 for w in words if w in all_stopwords)
        if stop_count / len(words) > 0.8:
            return True

    # Common page/footer junk
    if any(token in text_lower for token in ["page", "copyright", "www.", "http"]):
        return True

    return False
