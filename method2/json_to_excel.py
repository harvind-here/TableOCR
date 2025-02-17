import json
import pandas as pd

def parse_document(document_json):
    tables_list = []
    pages = document_json.get("pages", [])
    
    # For each page, iterate over any found tables
    for page in pages:
        tables = page.get("tables", [])
        for table in tables:
            table_data = []
            # Process header rows if present
            header_rows = table.get("headerRows", [])
            for row in header_rows:
                row_data = []
                for cell in row.get("cells", []):
                    text = cell.get("layout", {}).get("textAnchor", {}).get("content", "")
                    row_data.append(text)
                table_data.append(row_data)
            if body_rows:
                body_rows = table.get("bodyRows", [])
                for row in body_rows:
                    row_data = []
                    for cell in row.get("cells", []):
                        text = cell.get("layout", {}).get("textAnchor", {}).get("content", "")
                        row_data.append(text)
                    table_data.append(row_data)
            if table_data:
                tables_list.append(table_data)
    return tables_list

def export_tables_to_excel(tables, excel_path):
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        for idx, table in enumerate(tables):
            df = pd.DataFrame(table)
            sheet_name = f"Page-{idx}_Table1"
            df.to_excel(writer, sheet_name=sheet_name, index=False, header=False)
    print(f"Excel file saved to {excel_path}")

def main():
    # I use the parse_document function to extract tables from the JSON document.
    json_file = r"c:/Users/harvi/Downloads/document.json"
    try:
        with open(json_file, "r", encoding="utf8") as f:
            document_json = json.load(f)
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return

    tables = parse_document(document_json)
    if not tables:
        print("No tables detected in the JSON document.")
        return

    export_tables_to_excel(tables, excel_path="table_extraction_excel/")

if __name__ == "__main__":
    main()