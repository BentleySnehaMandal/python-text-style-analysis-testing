
import pdfplumber

def find_pdf_scale_using_characters(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        first_page = pdf.pages[0]
        width = first_page.width
        height = first_page.height
        print(f"Page width: {width}")
        print(f"Page height: {height}")
        
        # Extract the bounding box of the first character
        first_char = first_page.chars[0]
        char_width = first_char['width']
        char_height = first_char['height']
        print(f"First character width: {char_width}")
        print(f"First character height: {char_height}")
        
        # Calculate the scale based on the character dimensions relative to the page dimensions
        scale_width = char_width / width
        scale_height = char_height / height
        
        # Calculate a single scale value as the average of scale_width and scale_height
        scale = (scale_width + scale_height) / 2
        print(f"Scale: {scale}")



# Example usage
pdf_path = "C:\\Users\\Sneha.Mandal\\Downloads\\SNEHA25.pdf"
find_pdf_scale_using_characters(pdf_path)

