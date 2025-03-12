import pdfplumber

# Path to the PDF file
pdf_path = "C:/Users/Sneha.Mandal/python-test-folder/CPU SCHEDULING PROCESS.pdf"

# The word you want to find
word_to_find = "CPU"

# Open the PDF file
with pdfplumber.open(pdf_path) as pdf:
    # Select the first page
    p0 = pdf.pages[0]
    
    # Convert the page to an image
    im = p0.to_image(resolution=150)
    
    # Extract words from the page
    words = p0.extract_words()
    
    # Filter the words to highlight
    words_to_highlight = [word for word in words if word['text'] == word_to_find]
    
    # Draw rectangles around the filtered words
    im.draw_rects(words_to_highlight, fill=None, stroke="red", stroke_width=2)
    
    # Show the image with the highlighted word
    im.show()

    # pdf_path = "path/to/your/pdf.pdf"

# # The word you want to find
# word_to_find = "CPU"

# # Open the PDF file
# with pdfplumber.open(pdf_path) as pdf:
#     # Select the first page
#     p0 = pdf.pages[0]
    
#     # Extract words from the page
#     words = p0.extract_words()
    
#     # Find and print the coordinates of the word to find
#     for word in words:
#         if word['text'] == word_to_find:
#            print(f"Found '{word_to_find}' at coordinates: (x0: {word['x0']}, y0: {word['top']}, x1: {word['x1']}, y1: {word['bottom']})")