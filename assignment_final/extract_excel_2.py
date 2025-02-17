import os
import time
# os.environ["IOPATH_CACHE"] = r"C:\Users\harvi\Codebases\table_ocr\assignment_final\iopath_cache"
# os.environ["TORCH_HOME"] = r"C:\Users\harvi\Codebases\table_ocr\assignment_final\torch_cache"
# os.environ["XDG_CACHE_HOME"] = r"C:\Users\harvi\Codebases\table_ocr\assignment_final\torch_cache"
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import cv2
import io
import numpy as np
import pandas as pd
import layoutparser as lp
from google.cloud import vision

# Google Vision OCR function
def detect_text_bytes(image_bytes):
    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=image_bytes)
    response = client.document_text_detection(image=image)
    if response.error.message:
        raise Exception(response.error.message)
    return response.full_text_annotation.text.strip()

# Extract cell bounding boxes using Hough line detection
def process_cell(bbox, cell_roi):
    success, encoded_img = cv2.imencode('.png', cell_roi)
    if not success:
        return (bbox, "")
    cell_bytes = encoded_img.tobytes()
    text = detect_text_bytes(cell_bytes)
    return (bbox, text)

def extract_cells_hough(table_img):
    gray = cv2.cvtColor(table_img, cv2.COLOR_BGR2GRAY)
    # Smooth and detect edges.
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    edges = cv2.Canny(blurred, 50, 150, apertureSize=3)

    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=50, maxLineGap=5)
    if lines is None:
        return []

    horiz_lines = []
    vert_lines = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        if abs(y2-y1) < abs(x2-x1) * 0.5:
            horiz_lines.append((x1, y1, x2, y2))
        elif abs(x2-x1) < abs(y2-y1) * 0.5:
            vert_lines.append((x1, y1, x2, y2))
    
    if not horiz_lines or not vert_lines:
        return []
    h_ys = [ (y1+y2)/2 for (x1, y1, x2, y2) in horiz_lines ]
    v_xs = [ (x1+x2)/2 for (x1, y1, x2, y2) in vert_lines ]
    
    h_ys = sorted(h_ys)
    v_xs = sorted(v_xs)
    
    def cluster_coords(coords, thresh=10):
        clusters = []
        current = []
        for c in coords:
            if not current or abs(c - current[-1]) < thresh:
                current.append(c)
            else:
                clusters.append(int(sum(current)/len(current)))
                current = [c]
        if current:
            clusters.append(int(sum(current)/len(current)))
        return clusters

    row_lines = cluster_coords(h_ys)
    col_lines = cluster_coords(v_xs)

    cells = []
    for i in range(len(row_lines)-1):
        for j in range(len(col_lines)-1):
            x1 = col_lines[j]
            y1 = row_lines[i]
            x2 = col_lines[j+1]
            y2 = row_lines[i+1]
            if (x2-x1) > 10 and (y2-y1) > 10:
                cells.append((x1, y1, x2, y2))
    return cells

# Extract cells from table image using Hough method and OCR
def extract_cells_from_table_img(table_img):
    cell_bboxes = extract_cells_hough(table_img)
    cell_data = []

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [
            executor.submit(process_cell, bbox, table_img[bbox[1]:bbox[3], bbox[0]:bbox[2]])
            for bbox in cell_bboxes
        ]
        for future in futures:
            cell_data.append(future.result())
    return cell_data

# Build table grid using cell bounding boxes (grid from intersections)
def build_table_from_cells(cell_data):
    centers = []
    for bbox, text in cell_data:
        x1, y1, x2, y2 = bbox
        centers.append(((x1+x2)//2, (y1+y2)//2, text))
    
    y_centers = sorted([cy for cx, cy, txt in centers])
    row_clusters = []
    current = []
    for v in y_centers:
        if not current or abs(v - current[-1]) < 10:
            current.append(v)
        else:
            row_clusters.append(int(sum(current)/len(current)))
            current = [v]
    if current:
        row_clusters.append(int(sum(current)/len(current)))

    x_centers = sorted([cx for cx, cy, txt in centers])
    col_clusters = []
    current = []
    for v in x_centers:
        if not current or abs(v - current[-1]) < 10:
            current.append(v)
        else:
            col_clusters.append(int(sum(current)/len(current)))
            current = [v]
    if current:
        col_clusters.append(int(sum(current)/len(current)))
    
    table = {}
    for cx, cy, text in centers:
        row_idx = min(range(len(row_clusters)), key=lambda i: abs(cy - row_clusters[i]))
        col_idx = min(range(len(col_clusters)), key=lambda i: abs(cx - col_clusters[i]))
        table[(row_idx, col_idx)] = text

    n_rows = len(row_clusters)
    n_cols = len(col_clusters)
    table_list = []
    for i in range(n_rows):
        row = []
        for j in range(n_cols):
            row.append(table.get((i, j), ""))
        table_list.append(row)
    return table_list


# Use LayoutParser to detect table regions in a page image.
def detect_tables_with_layoutparser(image):
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    model = lp.PaddleDetectionLayoutModel(
        "lp://TableBank/ppyolov2_r50vd_dcn_365e",  # TableBank model
        device="gpu"
    )
    layout = model.detect(image_rgb)
    print("Detected layout blocks:")
    for block in layout:
        print(f"Type: {block.type}, Coordinates: {block.coordinates}")
    table_blocks = [block for block in layout if block.type.lower() == 'table']
    return table_blocks

# Main processing function for page images
def process_pages():
    PAGES_DIR = "assignment_final/pages/"
    EXTRACTIONS_DIR = "assignment_final/extractions/"
    os.makedirs(EXTRACTIONS_DIR, exist_ok=True)
    
    for image_path in Path(PAGES_DIR).glob("*.png"):
        start_time = time.time()
        
        print(f"Processing page: {image_path}")
        image = cv2.imread(str(image_path))
        
        table_regions = detect_tables_with_layoutparser(image)
        if not table_regions:
            print("No table region detected on this page, skipping...")
            continue
        
        page_excel = Path(image_path).stem + "_tables.xlsx"
        excel_path = os.path.join(EXTRACTIONS_DIR, page_excel)
        with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
            for idx, block in enumerate(table_regions):
                x1, y1, x2, y2 = map(int, block.coordinates)
                table_img = image[y1:y2, x1:x2]
                
                cell_data = extract_cells_from_table_img(table_img)
                table_data = build_table_from_cells(cell_data)
                
                df = pd.DataFrame(table_data)
                sheet_name = f"Table_{idx+1}"
                if df.empty:
                    df = pd.DataFrame([[""]])
                df.to_excel(writer, sheet_name=sheet_name, index=False, header=False)
                print(f"Extracted table {idx+1} from page {image_path.stem} into sheet '{sheet_name}'")
        elapsed = time.time() - start_time
        print(f"Excel file saved to: {excel_path}")
        print(f"Time taken to process page {image_path.stem}: {elapsed:.2f} seconds\n")

if __name__ == "__main__":
    process_pages()