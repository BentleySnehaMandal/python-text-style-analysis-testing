import pdfplumber

def get_page_dimensions(pdf_path):
    """
    Extract the height and width of the first page of a PDF.
    :param pdf_path: Path to the PDF file.
    :return: A tuple containing the width and height of the first page.
    """
    with pdfplumber.open(pdf_path) as pdf:
        first_page = pdf.pages[0]  # Get the first page
        width = first_page.width   # Page width
        height = first_page.height # Page height
        return width, height



def get_page_dimensions(pdf_path):
    """
    Extract the height and width of the first page of a PDF.
    :param pdf_path: Path to the PDF file.
    :return: A tuple containing the width and height of the first pag
    """
    with pdfplumber.open(pdf_path) as pdf:
        first_page = pdf.pages[0]  # Get the first page
        width = first_page.width   # Page width
        height = first_page.height # Page height
        return width/72, height/72

# Example usage
if __name__ == "__main__":
    pdf_path = "C:\\Users\\Sneha.Mandal\\Downloads\\Kimley Horn170088006_DSG_Whitestown_20221110-Sample.pdf"
    
    width, height = get_page_dimensions(pdf_path)
    print(f"Width: {width}, Height: {height}")
    vertical_scaling=height/11.0
    horizontal_scaling=width/8.5

    scaling_factor = (height * width) / (11.0*8.5)
    print(f"Scaling factor: {scaling_factor}") 
          
    # "C:\Users\Sneha.Mandal\Downloads\SNEHAMANDALLARGE.pdf"
    # "C:\Users\Sneha.Mandal\Downloads\Kimley Horn170088006_DSG_Whitestown_20221110-Sample.pdf"