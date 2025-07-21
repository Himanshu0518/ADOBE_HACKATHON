# main.py

import json
import os
from src.config import Config
from src.utils import  convert_types
from src.processor import PDFProcessor

def main():
    """
    Main function to run the PDF heading extraction process.
    """
    pdf_path = Config.DEFAULT_PDF_INPUT
    output_path = Config.DEFAULT_JSON_OUTPUT

    print(f"Starting PDF heading extraction for: {pdf_path}")

    # Load resources and initialize processor
    try:
       
        pdf_processor = PDFProcessor(Config.MODEL_PATH, Config.LABEL_MAP)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print(f"Please ensure '{Config.MODEL_PATH}' exists in the current directory.")
        return
    except Exception as e:
        print(f"An unexpected error occurred during initialization: {e}")
        return

    # Extract headings
    try:
        result = pdf_processor.extract_headings(pdf_path)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print(f"Please ensure the PDF file '{pdf_path}' exists.")
        return
    except Exception as e:
        print(f"An unexpected error occurred during heading extraction: {e}")
        return

    if not result["title"] and not result["outline"]:
        print("⚠️ No valid headings or title found. Output not saved.")
        return

    # Save output
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(convert_types(result), f, indent=2, ensure_ascii=False)
        print(f"✅ Extracted outline saved to {output_path}")
    except IOError as e:
        print(f"Error saving output to {output_path}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while saving: {e}")

if __name__ == "__main__":
    main()