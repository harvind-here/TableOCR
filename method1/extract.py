import os
from pathlib import Path
import cv2
import io
from google.cloud import vision
from Table_detection_using_Transformers.fast_api.table_extraction import Table_extraction

def detect_text(image_path):
    client = vision.ImageAnnotatorClient()
    with io.open(image_path, 'rb') as f:
        content = f.read()
    image = vision.Image(content=content)
    response = client.document_text_detection(image=image)
    if response.error.message:
        raise Exception(response.error.message)
    return response.full_text_annotation.text.strip()

def extract_table_text(detected_image_path, extractions_dir):
    # Extract text with Google Cloud Vision
    extracted_text = detect_text(str(detected_image_path))
    extraction_filename = Path(detected_image_path).stem + "_extracted.txt"
    extraction_filepath = os.path.join(extractions_dir, extraction_filename)
    with open(extraction_filepath, "w", encoding="utf8") as f:
        f.write(extracted_text)
    return extraction_filepath

def process_pages():
    PAGES_DIR = "pages/"
    OUTPUTS_DIR = "outputs/"
    EXTRACTIONS_DIR = "extractions/"
    
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    os.makedirs(EXTRACTIONS_DIR, exist_ok=True)
    
    for image_path in Path(PAGES_DIR).glob("*.png"):
        print(f"Processing {image_path}")
        # Perform table detection using the cloned repo class
        detector = Table_extraction(str(image_path), OUTPUTS_DIR)
        detected_image_path = detector.get_results()
        print(f"Table detection output saved to: {detected_image_path}")
        
        # Perform table extraction on the detected table image using Google Vision OCR
        extraction_filepath = extract_table_text(detected_image_path, EXTRACTIONS_DIR)
        print(f"Table extraction text saved to: {extraction_filepath}")

if __name__ == "__main__":
    process_pages()