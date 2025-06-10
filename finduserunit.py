import os
from pypdf import PdfReader

def get_pdf_user_unit(file_path):
    """
    Extract the user unit from the first page of a PDF using PyPDF.
    :param file_path: Path to the PDF file.
    :return: User unit (float).
    """
    try:
        # Open the PDF file
        pdf_reader = PdfReader(file_path)
        
        # Check if the document has at least one page
        if len(pdf_reader.pages) == 0:
            raise ValueError("The PDF file has no pages.")
        
        # Access the first page
        first_page = pdf_reader.pages[0]
        
        # Get the user unit
        user_unit = first_page.user_unit
        
        print(f"The user unit of '{os.path.basename(file_path)}' is: {user_unit}")
        return user_unit

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except ValueError as ve:
        print(f"Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred with file '{file_path}': {e}")

def process_folder(folder_path):
    """
    Process all PDF files in a folder and find their user units.
    :param folder_path: Path to the folder containing PDF files.
    """
    if not os.path.exists(folder_path):
        print(f"Error: The folder '{folder_path}' does not exist.")
        return

    # Iterate through all files in the folder
    for file_name in os.listdir(folder_path):
        if file_name.lower().endswith(".pdf"):  # Check if the file is a PDF
            file_path = os.path.join(folder_path, file_name)
            get_pdf_user_unit(file_path)

# Example usage
if __name__ == "__main__":
    folder_path = "C:\\Users\\Sneha.Mandal\\Downloads\\DRAWINGSHEETSPDFS"  # Replace with your folder path
    process_folder(folder_path)