
# workflow - pages -> table detection by the open source repo --> outputs -> googlevision ocr --> extractions -> txt to excel --> excel

import os
from pathlib import Path
import cv2
import io
import numpy as np
import pandas as pd
from google.cloud import vision
from Table_detection_using_Transformers.fast_api.table_extraction import Table_extraction

def detect_text_bytes(image_bytes):
    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=image_bytes)
    response = client.document_text_detection(image=image)
    if response.error.message:
        raise Exception(response.error.message)
    return response.full_text_annotation.text.strip()

def extract_cells_from_table(detected_image_path):
    # Load the detected table image
    img = cv2.imread(detected_image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Invert the image and binarize it
    _, binary = cv2.threshold(~gray, 128, 255, cv2.THRESH_BINARY)

    # Detect horizontal lines
    horizontal = binary.copy()
    cols = horizontal.shape[1]
    horizontal_size = max(1, cols // 20)
    horizontal_structure = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontal_size, 1))
    horizontal = cv2.erode(horizontal, horizontal_structure, iterations=1)
    horizontal = cv2.dilate(horizontal, horizontal_structure, iterations=1)

    # Detect vertical lines
    vertical = binary.copy()
    rows = vertical.shape[0]
    vertical_size = max(1, rows // 20)
    vertical_structure = cv2.getStructuringElement(cv2.MORPH_RECT, (1, vertical_size))
    vertical = cv2.erode(vertical, vertical_structure, iterations=1)
    vertical = cv2.dilate(vertical, vertical_structure, iterations=1)

    mask = cv2.add(horizontal, vertical)

    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    cells = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w < 20 or h < 20:
            continue
        cells.append((x, y, x + w, y + h))
        
    cell_data = []
    for bbox in cells:
        x1, y1, x2, y2 = bbox
        cell_roi = img[y1:y2, x1:x2]
        success, encoded_img = cv2.imencode('.png', cell_roi)
        if not success:
            text = ""
        else:
            cell_bytes = encoded_img.tobytes()
            text = detect_text_bytes(cell_bytes)
        cell_data.append((bbox, text))
    return cell_data

def group_cells_into_table(cell_data, row_threshold=20):
    # Sort cells by y (top) then x (left)
    cell_data.sort(key=lambda item: (item[0][1], item[0][0]))
    
    rows = []
    current_row = []
    for cell in cell_data:
        bbox, text = cell
        x1, y1, x2, y2 = bbox
        if not current_row:
            current_row.append(cell)
        else:
            ref_y = current_row[0][0][1]
            if abs(y1 - ref_y) < row_threshold:
                current_row.append(cell)
            else:
                current_row.sort(key=lambda item: item[0][0])
                rows.append(current_row)
                current_row = [cell]
    if current_row:
        current_row.sort(key=lambda item: item[0][0])
        rows.append(current_row)
    table_data = [[cell[1] for cell in row] for row in rows]
    return table_data

def process_pages():
    PAGES_DIR = "pages/"
    OUTPUTS_DIR = "outputs/"
    EXTRACTIONS_DIR = "extractions/"
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    os.makedirs(EXTRACTIONS_DIR, exist_ok=True)
    
    for image_path in Path(PAGES_DIR).glob("*.png"):
        print(f"Processing page: {image_path}")

        detector = Table_extraction(str(image_path), OUTPUTS_DIR)
        detected_image_path = detector.get_results()
        print(f"Detected table image saved to: {detected_image_path}")
        

        cell_data = extract_cells_from_table(detected_image_path)
        
        table_data = group_cells_into_table(cell_data)
        
        page_excel = Path(image_path).stem + "_table.xlsx"
        excel_path = os.path.join(EXTRACTIONS_DIR, page_excel)
        df = pd.DataFrame(table_data)
        df.to_excel(excel_path, index=False, header=False)
        print(f"Extracted table saved to: {excel_path}")

if __name__ == "__main__":
    process_pages()