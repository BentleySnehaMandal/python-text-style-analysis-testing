import os
from PyPDF2 import PdfReader, PdfWriter

def split_pdf(input_pdf_path, output_folder, pages_per_split=1):
    """
    Split a multipage PDF into smaller PDFs with a specified number of pages per split.
    
    :param input_pdf_path: Path to the input PDF file.
    :param output_folder: Folder where the split PDFs will be saved.
    :param pages_per_split: Number of pages per split PDF.
    """
   
    os.makedirs(output_folder, exist_ok=True)

   
    reader = PdfReader(input_pdf_path)
    total_pages = len(reader.pages)

   
    for start_page in range(0, total_pages, pages_per_split):
        writer = PdfWriter()
        end_page = min(start_page + pages_per_split, total_pages)

        for page_num in range(start_page, end_page):
            writer.add_page(reader.pages[page_num])

       
        output_pdf_path = os.path.join(output_folder, f"split_{start_page + 1}_to_{end_page}.pdf")
        with open(output_pdf_path, "wb") as output_pdf:
            writer.write(output_pdf)
        print(f"Saved: {output_pdf_path}")


if __name__ == "__main__":
    input_pdf = "C:/Users/Sneha.Mandal/Downloads/Kimley Horn170088006_DSG_Whitestown_20221110-Sample.pdf" 
    output_dir = "C:/Users/Sneha.Mandal/python-test-folder/SINGLESPLIT" 
    pages_per_split = 1
    split_pdf(input_pdf, output_dir, pages_per_split)