import pdfplumber
from pdfplumber.ctm import CTM
import json

# Function to group characters by their skewness
def group_characters_by_skewness(pdf_path, output_json_path):
    skewness_dict = {}

    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            # Get the page rotation
            page_rotation = page.rotation or 0  # Default to 0 if no rotation is specified

            for char in page.chars:
                # Extract the transformation matrix and calculate skewness
                char_matrix = char.get("matrix")
                if not char_matrix:
                    continue
                char_ctm = CTM(*char_matrix)
                char_skewness = round(char_ctm.skew_x + page_rotation, 2)  # Add page rotation to character skewness

                # Group characters by skewness
                if char_skewness not in skewness_dict:
                    skewness_dict[char_skewness] = []
                skewness_dict[char_skewness].append({
                    "text": char.get("text"),
                    "fontname": char.get("fontname"),
                    "size": char.get("size"),
                    "x0": char.get("x0"),
                    "x1": char.get("x1"),
                    "y0": char.get("y0"),
                    "y1": char.get("y1"),
                    "page_number": page.page_number
                })

    # Save the result as a JSON file
    with open(output_json_path, "w") as json_file:
        json.dump(skewness_dict, json_file, indent=4)

    print(f"Characters grouped by skewness saved to {output_json_path}")

# Example usage
pdf_path = "C:/Users/Sneha.Mandal/python-test-folder/TestPdfs/singletestpdf00.pdf"  # Path to the PDF
output_json_path = "characters_by_skewness.json"  # Output JSON file
group_characters_by_skewness(pdf_path, output_json_path)