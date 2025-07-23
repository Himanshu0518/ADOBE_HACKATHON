# pdf_parser/config.py

import numpy as np
import pandas as pd
from nltk.corpus import stopwords
import os
from from_root import from_root # This imports the function 'from_root'

# Call the from_root function once to get the actual root path string
# and store it in a variable.
PROJECT_ROOT = from_root() 
print(f"Project root path: {PROJECT_ROOT}")
class Config:
    """
    Centralized configuration parameters for the PDF parsing application.
    """
    # NLTK Stopwords
    STOPWORDS_LANGS = stopwords.fileids() # All available NLTK languages

    # Model and Labeling
    # Use the PROJECT_ROOT variable here
    MODEL_PATH = os.path.join(PROJECT_ROOT ,"hackathon_model.joblib")
    LABEL_MAP = {
        np.int64(0): 'Unlabeled', # Body texts
        np.int64(1): 'H1',
        np.int64(2): 'H2',
        np.int64(3): 'H3',
        np.int64(4): 'TITLE'
    }

    # Text Processing and Feature Extraction
    GAP_THRESHOLD = 30
    CENTERED_X_THRESHOLD_RATIO = (0.3, 0.7) # (min_ratio, max_ratio) for x_center

    # Noise and Invalid Heading Filtering Thresholds
    NOISE_STOPWORD_RATIO_THRESHOLD = 0.8
    MIN_TEXT_LENGTH = 3 # Minimum characters for any valid text line
    MIN_ALPHA_COUNT_FOR_HEADING = 4 # Minimum alphabetic characters for a valid heading
    MIN_WORD_COUNT_FOR_HEADING_ENDS_WITH_DOT = 6 # If heading ends with '.', needs more words

    # Application Paths
    # Use the PROJECT_ROOT variable here
    DEFAULT_PDF_INPUT = os.path.join(PROJECT_ROOT , "input","attention_all_you_need.pdf")
    DEFAULT_JSON_OUTPUT = os.path.join(PROJECT_ROOT ,"output", "output.json")
    
    # These print statements will now work correctly
    print(f"Default PDF input path: {DEFAULT_PDF_INPUT}")
    print(f"Default JSON output path: {DEFAULT_JSON_OUTPUT}")
