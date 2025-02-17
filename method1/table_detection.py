# Python
import os
from pathlib import Path
from Table_detection_using_Transformers.fast_api.table_extraction import Table_extraction

def process_pages():
    PAGES_DIR = "pages/"
    OUTPUTS_DIR = "outputs/"
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    
    for image_path in Path(PAGES_DIR).glob("*.png"):
        print(f"Processing {image_path}")
        detector = Table_extraction(str(image_path), OUTPUTS_DIR)
        result_image = detector.get_results()
        print(f"Table-detection output saved to: {result_image}")

if __name__ == "__main__":
    process_pages()