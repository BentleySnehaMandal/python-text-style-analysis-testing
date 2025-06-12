import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pdfplumber
import json
import os
import re
import math
from collections import Counter
import webcolors
from pdfminer.psparser import PSLiteral


# Function to calculate skewness angle from the transformation matrix
def calculate_skew_angle(matrix):
    skew_angle = round(math.degrees(math.atan2(matrix[1], matrix[0])), 2)
    return skew_angle




# Function to normalize font names
def normalize_fontname(fontname):
    """
    Normalize font names by removing font subsetting and special characters, and converting to lowercase.
    """
    # Remove font subsetting prefix (e.g., "ABCDE+Arial" -> "Arial")
    normalized_fontname = re.sub(r'^[A-Z]{6}\+', '', fontname)
    # Remove special characters and convert to lowercase
    return normalized_fontname.replace("-", "").replace("_", "").replace("+", "").replace(" ", "").lower()


# Helper function to normalize colors to RGB
def normalize_color_to_rgb(color, color_space):
    if color is None:
        return (0, 0, 0)  # Treat null colors as black

    if color_space == "DeviceGray":
        if len(color) == 1:
            gray_value = int(color[0] * 255)
            return (gray_value, gray_value, gray_value)
        else:
            return (0, 0, 0)

    if color_space == "DeviceRGB":
        if len(color) == 3:
            r, g, b = [int(c * 255) for c in color]
            return (r, g, b)
        else:
            scaled_color = [int(c * 255) for c in color]
            while len(scaled_color) < 3:
                scaled_color.append(0)
            return tuple(scaled_color[:3])

    if color_space == "DeviceCMYK":
        if len(color) == 4:
            c, m, y, k = color
            r = int(255 * (1 - c) * (1 - k))
            g = int(255 * (1 - m) * (1 - k))
            b = int(255 * (1 - y) * (1 - k))
            return (r, g, b)
        else:
            return None

    return None


# Helper function to get the color name from RGB
def get_color_name_from_rgb(color):
    if color is None or not isinstance(color, tuple) or len(color) != 3:
        return "Invalid Color"
    try:
        return webcolors.rgb_to_name(color)
    except ValueError:
        try:
            return f"Closest Match: {webcolors.rgb_to_name(webcolors.rgb_to_hex(color))}"
        except Exception:
            return "Invalid Color"


# Function to classify styles
def classify_styles(char_info):
    fontname = normalize_fontname(char_info['fontname'])
    size = char_info['size']

    # Apply bucketing logic for font size
    bucket_size = 3
    lower_bound = math.floor(size / bucket_size) * bucket_size
    middle_value = lower_bound + (bucket_size / 2)
    rounded_size = round(middle_value)

    color_space = char_info.get('ncs', None)
    stroking_color_rgb = normalize_color_to_rgb(char_info['stroking_color'], color_space)
    non_stroking_color_rgb = normalize_color_to_rgb(char_info['non_stroking_color'], color_space)
    stroking_color_name = get_color_name_from_rgb(stroking_color_rgb)
    non_stroking_color_name = get_color_name_from_rgb(non_stroking_color_rgb)

    return (
        fontname,
        rounded_size,
        stroking_color_name,
        non_stroking_color_name,
        'bold' in fontname,
        'italic' in fontname,
    )


# Function to extract character information from the PDF
# Function to extract character information from the PDF
def extract_char_info(pdf_path):
    char_list = []
    undetected_styles = []

    with pdfplumber.open(pdf_path) as pdf:
        first_page = pdf.pages[0]  # Get the first page
        first_page_width = first_page.width   # Page width
        first_page_height = first_page.height
        height=max(first_page_width, first_page_height)/72
        width=min(first_page_width, first_page_height)/72
        
        vertical_scaling=height/11.0
        horizontal_scaling=width/8.5

        scaling_factor = (horizontal_scaling + vertical_scaling) / 2


        for page_number, page in enumerate(pdf.pages, start=1):
            for char in page.chars:
                text = char.get('text')
                size = char.get('size')
                matrix = char.get("matrix", [1, 0, 0, 1, 0, 0])  # Default to identity matrix if missing
                stroking_color = char.get('stroking_color')
                non_stroking_color = char.get('non_stroking_color')

                

        #         adv = char.get('adv', None)  # Advance width
        #         width = char.get('width', None)  # Text width
        #         size = char.get('size', None)  # Font size

        #         if adv is not None and width is not None and size is not None and width > 0:
        # # Calculate the scaling factor
        #          scaling_factor = adv / (size * width)
        
        #         else:
        # # Default scaling factor if properties are missing
        #            scaling_factor=1.0
                
                print(f"Scaling Factor: {scaling_factor}")

                if text and size > 0:
                    char_info = {
                        'fontname': char.get('fontname'),
                        'size': size*scaling_factor,  # Apply scaling factor to size
                        'stroking_color': stroking_color,
                        'non_stroking_color': non_stroking_color,
                        'x0': char.get('x0'),
                        'x1': char.get('x1'),
                        'y0': char.get('y0'),
                        'y1': char.get('y1'),
                        'top': char.get('top'),
                        'bottom': char.get('bottom'),
                        'page_number': page_number,
                        'matrix': matrix,
                        'scaling_factor': scaling_factor,  # Add scaling factor
                    }
                    char_list.append(char_info)

    return char_list, undetected_styles


# Function to create unique text styles and populate style_location_mapping
def create_unique_text_styles_and_mapping(text_styles):
    unique_text_styles = []
    scaling_factors = []
    for char_info in text_styles:
        style = classify_styles(char_info)
        style_dict = {
            'fontname': style[0],
            'size': style[1],
            'stroking_color': style[2],
            'non_stroking_color': style[3],
            'isBold': style[4],
            'isItalic': style[5],
        }
        if style_dict not in unique_text_styles:
            unique_text_styles.append(style_dict)
            scaling_factors.append(char_info['scaling_factor'])

    return unique_text_styles, scaling_factors


# Function to create the JSON report
def generate_report(pdf_path):
    char_list, undetected_styles = extract_char_info(pdf_path)
    unique_text_styles, scaling_factors = create_unique_text_styles_and_mapping(char_list)

    # Convert the unique styles list to dictionaries with style_01, style_02, etc.
    unique_text_styles_dict = {}
    for i, style in enumerate(unique_text_styles, start=0):
        style_key = f"style_{i:02d}"
        style['scaling_factor'] = scaling_factors[i]  # Add scaling factor to the style
        unique_text_styles_dict[style_key] = style

    # Create a JSON object
    result = {
        "unique_styles_in_text": len(unique_text_styles),
        "unique_text_styles": unique_text_styles_dict,
        "undetected_styles": undetected_styles,
    }

    # Save the JSON object to a file
    result_filename = f"result_{os.path.basename(pdf_path).replace('.pdf', '')}.json"
    with open(result_filename, "w") as json_file:
        json.dump(result, json_file, indent=4)

    print(f"JSON object saved to {result_filename}")

    return result


# Function to display the report in the UI
def display_report(report):
    unique_text_styles_count_label.config(text=f"Unique Styles in Text: {report['unique_styles_in_text']}")
    style_keys = list(report['unique_text_styles'].keys())
    style_dropdown['values'] = style_keys
    style_dropdown.current(0)


# Function to handle style selection from the dropdown
def on_style_select(event):
    selected_style = style_dropdown.get()
    if selected_style in report['unique_text_styles']:
        style_info = report['unique_text_styles'][selected_style]
        style_info_text.delete(1.0, tk.END)
        for key, value in style_info.items():
            style_info_text.insert(tk.END, f"{key}: {value}\n")


# Function to open a file dialog and select a PDF
def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if file_path:
        global report
        report = generate_report(file_path)
        display_report(report)


# Create the main window
root = tk.Tk()
root.title("PDF Text Styles Analysis Tool")

# Create and place the widgets
open_button = tk.Button(root, text="Open PDF", command=open_file)
open_button.pack(pady=10)

unique_text_styles_count_label = tk.Label(root, text="Unique Styles in Text: ")
unique_text_styles_count_label.pack(pady=10)

style_dropdown_label = tk.Label(root, text="Select Style:")
style_dropdown_label.pack(pady=5)

style_dropdown = ttk.Combobox(root)
style_dropdown.pack(pady=5)
style_dropdown.bind("<<ComboboxSelected>>", on_style_select)

style_info_text = tk.Text(root, height=10, width=50)
style_info_text.pack(pady=10)

# Start the main loop
root.mainloop()