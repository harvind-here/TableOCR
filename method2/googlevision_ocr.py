# I used Cloud document AI processor
# I got this code implementation from the google cloud document AI documentation
# I used Document AI API endpoint, which is a REST API that extracts structured information from documents.

from typing import Optional
from google.api_core.client_options import ClientOptions
from google.cloud import documentai  # type: ignore

# TO DO(developer): Uncomment these variables before running the sample.
project_id = "internassignment-450706"
location = "us"  # Format is "us" or "eu"
processor_id = "****************"  # Create processor before running sample
file_path = "pages/pages.pdf"
mime_type = "application/pdf"  # Refer to https://cloud.google.com/document-ai/docs/file-types for supported file types
# field_mask = "text,entities,pages.pageNumber" .
processor_version_id = "pretrained-ocr-v2.0-2023-06-02"

def process_document_sample(
    project_id: str,
    location: str,
    processor_id: str,
    file_path: str,
    mime_type: str,
    field_mask: Optional[str] = None,
    processor_version_id: Optional[str] = None,
) -> None:
    # Use the correct API endpoint without trailing spaces.
    opts = ClientOptions(api_endpoint="https://us-documentai.googleapis.com/v1/projects/*********/locations/us/processors/158212c00******:process") # as it is cost dependent i hide the api endpoint :)
    
    client = documentai.DocumentProcessorServiceClient(client_options=opts)
    
    if processor_version_id:
        name = client.processor_version_path(
            project_id, location, processor_id, processor_version_id
        )
    else:
        name = client.processor_path(project_id, location, processor_id)
    
    print("Reading file:", file_path)
    with open(file_path, "rb") as image_file:
        image_content = image_file.read()
    
    raw_document = documentai.RawDocument(content=image_content, mime_type=mime_type)
    
    process_options = documentai.ProcessOptions(
        individual_page_selector=documentai.ProcessOptions.IndividualPageSelector(pages=[1])
    )
    print("Sending processing request...")
    
    request = documentai.ProcessRequest(
        name=name,
        raw_document=raw_document,
        field_mask=field_mask,
        process_options=process_options,
    )
    
    result = client.process_document(request=request)
    print("Processing finished.")
    
    document = result.document
    # print("The document contains the following text:")
    # print(document.text)
    # document.txt should be obtaining but it was too slow when requested from endpoint so i directly used the processor in cloud itself and exported as json (document.json)

if __name__ == "__main__":
    process_document_sample(project_id, location, processor_id, file_path, mime_type)