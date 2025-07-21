# pdf_parser/utils.py

import re
import json
import numpy as np
import pandas as pd
from nltk.corpus import stopwords

def load_stopwords(languages):
    """Loads multilingual stopwords from NLTK."""
    all_stopwords = set()
    for lang in languages:
        all_stopwords.update(stopwords.words(lang))
    return all_stopwords

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
    all_stopwords = load_stopwords(stopwords.fileids())
   
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

