# from PyPDF2 import PdfReader

# def extract_content_stream(pdf_path, page_number=0):
#     """
#     Extract the raw content stream of a PDF page.
#     :param pdf_path: Path to the PDF file.
#     :param page_number: Page number to extract (0-indexed).
#     """
#     reader = PdfReader(pdf_path)
#     page = reader.pages[page_number]
#     content_stream = page.get_contents()
    
#     if content_stream:
#         print("Content Stream:")
#         print(content_stream)
#     else:
#         print("No content stream found for this page.")

# # Path to your PDF file
# pdf_path = pdf_path = "C:/Users/Sneha.Mandal/python-test-folder/TestPdfs/singletestpdf00.pdf"

# # Extract and print the content stream of the first page
# extract_content_stream(pdf_path)

# import fitz  # PyMuPDF

# def extract_content_stream_with_pymupdf(pdf_path, page_number=0):
#     """
#     Extract and print the raw content stream of a PDF page using PyMuPDF.
#     :param pdf_path: Path to the PDF file.
#     :param page_number: Page number to extract (0-indexed).
#     """
#     # Open the PDF
#     pdf_document = fitz.open(pdf_path)
#     page = pdf_document[page_number]

#     # Extract the raw content stream
#     raw_content = page.get_text("rawdict")
#     if raw_content and "stream" in raw_content:
#         print("Raw Content Stream:")
#         print(raw_content["stream"])
#     else:
#         print("No content stream found for this page.")

# # Path to your PDF file
# pdf_path = "C:/Users/Sneha.Mandal/python-test-folder/TestPdfs/singletestpdf00.pdf"

# # Extract and print the content stream of the first page
# extract_content_stream_with_pymupdf(pdf_path)
import pdfplumber
import json

def extract_text_and_chars_to_json(pdf_path, output_json_path, page_number=0):
    """
    Extract text and character details from a PDF page using pdfplumber and save to a JSON file.
    :param pdf_path: Path to the PDF file.
    :param output_json_path: Path to save the JSON file.
    :param page_number: Page number to extract (0-indexed).
    """
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_number]
        
        # Extract text
        extracted_text = page.extract_text()
        
        # Extract character details
        character_details = page.chars
        
        # Prepare data for JSON
        data = {
            "page_number": page_number + 1,
            "extracted_text": extracted_text,
            "character_details": character_details
        }
        
        # Save to JSON file
        with open(output_json_path, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4)
        
        print(f"Data successfully saved to {output_json_path}")

# Path to your PDF file
pdf_path = "C:/Users/Sneha.Mandal/python-test-folder/TestPdfs/singletestpdf00.pdf"

# Path to save the JSON file
output_json_path = "C:/Users/Sneha.Mandal/python-test-folder/extracted_data.json"

# Extract and save text and character details to JSON
extract_text_and_chars_to_json(pdf_path, output_json_path)