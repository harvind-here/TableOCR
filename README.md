# Image Documents to Excel Converter

## Introduction

A solution for Image documents to Excel format. Ideal for Table extraction. Accuracy is reliable for non handwritten tables. But for handwritten reliable to some extent (lighting conditions, shades should be minimized, works better if scanned document). But table layout/structure is preserved in either case :)

This project provides multiple methods to extract table structures from image documents and export the results into Excel files. Choose the method that best fits your needs:

- **assignment_final:** Uses LayoutParser with a deep learning model (TableBank) for table detection.
- **method1:** Uses a YOLOv8-based approach for table extraction with Transformers.
- **method2:** Implements an OCR-based approach for table detection and extraction.

## Project Structure
```
.  
├── assignment_final  
│   ├── scripts  
│   │   ├── pdf2img.py  # Convert PDF files to PNG images  
│   │   ├── extract_excel_2.py  # Detect tables and export as Excel files  
│   │   └── (other support modules)  
│   ├── outputs  # Store extracted tables, images, or results  
│   ├── extractions  # Store intermediate extraction files  
│   ├── models  
│   │   ├── yolov8m-table-extraction.pt  # Pre-trained model weight  
│   │   └── (other model-related files)  
│   ├── method1  
│   │   ├── Table_detection_using_Transformers  
│   │   ├── scripts  # Support scripts for method1  
│   │   ├── outputs  
│   │   └── extractions  
│   ├── method2  
│   │   ├── table_detection_ocr  # Alternative table detection scripts  
│   │   ├── table_extraction_excel  # Modules for table extraction into Excel  
│   │   ├── scripts  # Support scripts for method2  
│   │   ├── outputs  
│   │   └── extractions  
├── .gitignore  
└── README.md  # Add a README for project documentation  
```
## Prerequisites

->GCP
-> Google Cloud SDK

## Installation Guidelines

### Common Setup

1. **Clone the Repository and Create a Virtual Environment**

   ```bash
   git clone https://github.com/yourusername/table_ocr.git
   cd table_ocr
   conda create -n table_ocr python=3.12
   ```

2. **Activate the Virtual Environment**

On Windows:
On Linux/MacOS:
Install Required Python Packages

The project uses several libraries including LayoutParser, PaddlePaddle (or paddlepaddle-gpu for GPU acceleration), OpenCV, pdf2image, pandas, and openpyxl.

Note: For GPU acceleration, install the GPU-enabled PaddlePaddle version (ensure compatibility with your CUDA version):

Environment Variables and Credentials

Use google cloud vision API for OCR, download the credentials, make sure you have google cloud SDK. and then set env var to the credential file path. 

Specific Instructions for Each Method

### assignment\_final Method

**Purpose:** Uses LayoutParser with TableBank deep learning model for table detection.

#### Setup Instructions:

1. Navigate to the `assignment_final` directory:
   ```bash
   cd assignment_final
   ```
2. Convert PDF pages to images:
   ```bash
   python scripts/pdf2img.py input.pdf output_folder/
   ```
3. Extract tables from images and export to Excel:
   ```bash
   python scripts/extract_excel_2.py output_folder/ extracted_tables.xlsx
   ```
4. Adjust parameters (e.g., DPI or model device "cpu"/"gpu") within the scripts as needed.

---

### Method1 (YOLOv8 & Transformers Based)

**Purpose:** Uses a YOLOv8-based approach coupled with Transformers for table detection.

#### Setup Instructions:

1. Navigate to the `method1` directory:
   ```bash
   cd method1
   ```
2. Ensure that the pre-trained model weights (e.g., `yolov8m-table-extraction.pt`) are in place.
3. Install any additional dependencies if a separate `requirements.txt` exists in `method1`:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the main script for `method1`:
   ```bash
   python scripts/detect_tables.py input_image.jpg extracted_tables.xlsx
   ```
5. Output (extraction results, logs, etc.) will be stored in `extractions/` and `outputs/`.

---

### Method2 (OCR-Based Approach)

**Purpose:** Utilizes OCR techniques, cell identification and table structure analysis for extraction.

#### Setup Instructions:

1. Navigate to the `method2` directory:
   ```bash
   cd method2
   ```
2. Install any additional dependencies specified for `method2`:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the main script for `method2`:
   ```bash
   python scripts/ocr_table_extraction.py input_image.jpg extracted_tables.xlsx
   ```
4. Outputs are generated in the `table_extraction_excel/` folder.

### Final (Large-Scale Approach)

**Purpose:** Similar to method1, but support for large scale analysis and conversion.

Thanks to Google Cloud Platform for their $300 free credits...