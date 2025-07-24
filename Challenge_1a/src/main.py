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
    input_output_pairs = Config.get_input_output_files()
    if not input_output_pairs:
        print("No PDF files found in the input directory.")
        return

   
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
    
    for input_path, output_path in input_output_pairs:
        try:
            result = pdf_processor.extract_headings(input_path)
        except FileNotFoundError as e:
            print(f"Error: {e}")
            print(f"Please ensure the PDF file '{output_path}' exists.")
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

     #   print(f"Processed {input_path} -> {output_path}")

print("All PDF files processed successfully.")

if __name__ == "__main__":
    main()