import pdfplumber
import json
import os

# ============================================================================================================================================================================================================
# Extracting text and text styles from PDFs in Python can be achieved using libraries like PyMuPDF (also known as fitz) and pdfminer.six. Below are examples of how to use these libraries:

# 2502GNDPR00.pdf
# C:\Users\Sneha.Mandal\python-test-folder\2502GNDPR00.pdf

# with pdfplumber.open("C:/Users/Sneha.Mandal/python-test-folder/2502GNDPR00.pdf") as pdf:
#     # first_page = pdf.pages[0]
#     # print(first_page)
#     # # print(pdf.pages)
#     # # print(first_page)
#     # print(first_page.chars[0])
#     for page in pdf.pages:
#         chars_list.append(page.chars)

# print(len(chars_list[0]))
# # print(len(chars_list))
# ==========================================================================================================================================================================================

import pdfplumber
import json
import os

chars_list = []

# Directory containing the PDFs
pdf_dir = "TestPdfs"

# Iterate over each PDF in the directory
for pdf_filename in os.listdir(pdf_dir):
    if pdf_filename.endswith(".pdf"):
        pdf_path = os.path.join(pdf_dir, pdf_filename)
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                for char in page.chars:
                    char_info = {
                        'fontname': char.get('fontname'),
                        'size': char.get('size'),
                        'height': char.get('height'),
                        'width': char.get('width'),
                        'stroking_color': char.get('stroking_color'),
                        'non_stroking_color': char.get('non_stroking_color')
                    }
                    chars_list.append(char_info)

        # Function to classify styles
        def classify_styles(char_info):
            return (
                char_info['fontname'],
                round(char_info['size']),
                tuple(char_info['stroking_color']) if char_info['stroking_color'] else None,
                tuple(char_info['non_stroking_color']) if char_info['non_stroking_color'] else None
            )

        # Create a set of unique styles
        unique_styles = {classify_styles(char_info) for char_info in chars_list}

        # Create a dictionary to count the frequency of each style
        style_frequency = {}
        for style in unique_styles:
            style_frequency[style] = sum(1 for char_info in chars_list if classify_styles(char_info) == style)

        sorted_style_frequency = dict(sorted(style_frequency.items(), key=lambda item: item[1], reverse=True))

        # Convert unique_styles back to a list of dictionaries
        unique_styles = [
            {
                'fontname': style[0],
                'size': style[1],
                'stroking_color': list(style[2]) if style[2] else None,
                'non_stroking_color': list(style[3]) if style[3] else None
            }
            for style in unique_styles
        ]

        sorted_style_frequency_str_keys = {str(key): value for key, value in sorted_style_frequency.items()}

        # Create a JSON object
        result = {
            "unique_styles_count": len(unique_styles),
            "unique_styles": unique_styles,
            "sorted_style_frequency": sorted_style_frequency_str_keys
        }

        # Save the JSON object to a file
        result_filename = f"result__new{pdf_filename.replace('.pdf', '')}.json"
        with open(result_filename, "w") as json_file:
            json.dump(result, json_file, indent=4)

        print(f"JSON object saved to {result_filename}")

        # Clear chars_list for the next PDF
        chars_list.clear()