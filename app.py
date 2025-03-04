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
        unique_styles_set = {classify_styles(char_info) for char_info in chars_list}

        # Create a dictionary to count the frequency of each style
        style_frequency = {}
        for style in unique_styles_set:
            style_frequency[style] = sum(1 for char_info in chars_list if classify_styles(char_info) == style)

        # Convert unique_styles_set to a dictionary with style_01, style_02, etc.
        unique_styles = {}
        style_key_map = {}
        for i, style in enumerate(unique_styles_set, start=1):
            style_key = f"style_{i:02d}"
            fontname, size, stroking_color, non_stroking_color = style
            unique_styles[style_key] = {
                'fontname': fontname,
                'size': size,
                'stroking_color': list(stroking_color) if stroking_color else None,
                'non_stroking_color': list(non_stroking_color) if non_stroking_color else None
            }
            normalized_fontname = fontname.replace("-", "").replace("_", "").replace("+", "").lower()
            if 'bold' in normalized_fontname:
                unique_styles[style_key]['is_Bold'] = True
            if 'italic' in normalized_fontname:
                unique_styles[style_key]['is_Italic'] = True
            style_key_map[style] = style_key

        # Convert sorted_style_frequency to use style_01, style_02, etc.
        sorted_style_frequency = {style_key_map[style]: freq for style, freq in sorted(style_frequency.items(), key=lambda item: item[1], reverse=True)}

        # Create a JSON object
        result = {
            "unique_styles_count": len(unique_styles),
            "unique_styles": unique_styles,
            "sorted_style_frequency": sorted_style_frequency
        }

        # Save the JSON object to a file
        result_filename = f"result_{pdf_filename.replace('.pdf', '')}.json"
        with open(result_filename, "w") as json_file:
            json.dump(result, json_file, indent=4)

        print(f"JSON object saved to {result_filename}")

        # Clear chars_list for the next PDF
        chars_list.clear()