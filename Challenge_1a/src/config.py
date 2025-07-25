# pdf_parser/config.py

import numpy as np
import pandas as pd
from nltk.corpus import stopwords
import os
from from_root import from_root # This imports the function 'from_root'

# Call the from_root function once to get the actual root path string
# and store it in a variable.
PROJECT_ROOT = from_root() 
INPUT_DIR = os.path.join(PROJECT_ROOT, "input")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")

print(f"Project root path: {PROJECT_ROOT}")
class Config:
    """
    Centralized configuration parameters for the PDF parsing application.
    """
    # NLTK Stopwords
    STOPWORDS_LANGS = stopwords.fileids() # All available NLTK languages

    # Model and Labeling
    # Use the PROJECT_ROOT variable here
    MODEL_PATH = os.path.join(PROJECT_ROOT ,"model","hackathon_model.joblib")
    LABEL_MAP = {
        np.int64(0): 'Unlabeled', # Body texts
        np.int64(1): 'H1',
        np.int64(2): 'H2',
        np.int64(3): 'H3',
        np.int64(4): 'TITLE'
    }
    INPUT_DIR = INPUT_DIR
    OUTPUT_DIR = OUTPUT_DIR
    
    # Text Processing and Feature Extraction
    GAP_THRESHOLD = 30
    CENTERED_X_THRESHOLD_RATIO = (0.3, 0.7) # (min_ratio, max_ratio) for x_center

    # Noise and Invalid Heading Filtering Thresholds
    NOISE_STOPWORD_RATIO_THRESHOLD = 0.8
    MIN_TEXT_LENGTH = 3 # Minimum characters for any valid text line
    MIN_ALPHA_COUNT_FOR_HEADING = 4 # Minimum alphabetic characters for a valid heading
    MIN_WORD_COUNT_FOR_HEADING_ENDS_WITH_DOT = 6 # If heading ends with '.', needs more words


    @staticmethod
    def get_input_output_files():
        """
        Scans the input directory for all PDF files and returns a list of
        (input_file_path, output_file_path) tuples with .json extension.
        """
        return [(os.path.join(Config.INPUT_DIR, "file06.pdf"),
                 os.path.join(Config.OUTPUT_DIR, "file06.json"))]
    
        # input_output_pairs = []
        # for file in os.listdir(Config.INPUT_DIR):
        #     if file.lower().endswith(".pdf"):
        #         input_path = os.path.join(Config.INPUT_DIR, file)
        #         json_filename = os.path.splitext(file)[0] + ".json"
        #         output_path = os.path.join(Config.OUTPUT_DIR, json_filename)
        #         input_output_pairs.append((input_path, output_path))
        # return input_output_pairs

