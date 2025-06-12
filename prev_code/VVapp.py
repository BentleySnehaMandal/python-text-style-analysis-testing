import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pdfplumber
import json
import os
import re
from pdfminer.psparser import PSLiteral
import webcolors
from pdfplumber.ctm import CTM
from PIL import Image, ImageDraw, ImageFont
import math
import fitz

# Function to calculate skewness angle from the transformation matrix
def calculate_skew_angle(matrix):
    skew_angle = round(math.degrees(math.atan2(matrix[1], matrix[0])), 2)
    return skew_angle



# Helper function to get the color name from RGB
def get_color_name_from_rgb(color):
    if color is None or not isinstance(color, tuple) or len(color) != 3:
        return "Invalid Color"  # Handle invalid color values
    try:
        return webcolors.rgb_to_name(color)
    except ValueError:
        # If exact match is not found, return the closest color name
        try:
            return f"Closest Match: {webcolors.rgb_to_name(webcolors.rgb_to_hex(color))}"
        except Exception:
            return "Invalid Color"  # Handle unexpected errors
    

def normalize_color_to_rgb(color):
    if color is None:
        # Treat null colors as black
        return (0, 0, 0)  # RGB for black        
    if len(color) == 1:  # DeviceGray
        gray_value = int(color[0] * 255)  
        return (gray_value, gray_value, gray_value)
    if len(color) == 3:  # DeviceRGB
        r, g, b = [int(c * 255) for c in color]  
        return (r, g, b)
    if len(color) == 4:  # DeviceCMYK
        c, m, y, k = color
        r = int(255 * (1 - c) * (1 - k))
        g = int(255 * (1 - m) * (1 - k))
        b = int(255 * (1 - y) * (1 - k))
        return (r, g, b)
    if len(color) == 3 and isinstance(color[0], (int, float)) and -128 <= color[1] <= 127 and -128 <= color[2] <= 127:
   
        return None  # Exclude Lab colors
    return None


import webcolors
from pdfplumber.ctm import CTM
from PIL import Image, ImageDraw, ImageFont
import math
import fitz

# Function to calculate skewness angle from the transformation matrix
def calculate_skew_angle(matrix):
    skew_angle = round(math.degrees(math.atan2(matrix[1], matrix[0])), 2)
    return skew_angle



# Helper function to get the color name from RGB
def get_color_name_from_rgb(color):
    if color is None or not isinstance(color, tuple) or len(color) != 3:
        return "Invalid Color"  # Handle invalid color values
    try:
        return webcolors.rgb_to_name(color)
    except ValueError:
        # If exact match is not found, return the closest color name
        try:
            return f"Closest Match: {webcolors.rgb_to_name(webcolors.rgb_to_hex(color))}"
        except Exception:
            return "Invalid Color"  # Handle unexpected errors
    

def normalize_color_to_rgb(color):
    if color is None:
        # Treat null colors as black
        return (0, 0, 0)  # RGB for black        
    if len(color) == 1:  # DeviceGray
        gray_value = int(color[0] * 255)  
        return (gray_value, gray_value, gray_value)
    if len(color) == 3:  # DeviceRGB
        r, g, b = [int(c * 255) for c in color]  
        return (r, g, b)
    if len(color) == 4:  # DeviceCMYK
        c, m, y, k = color
        r = int(255 * (1 - c) * (1 - k))
        g = int(255 * (1 - m) * (1 - k))
        b = int(255 * (1 - y) * (1 - k))
        return (r, g, b)
    if len(color) == 3 and isinstance(color[0], (int, float)) and -128 <= color[1] <= 127 and -128 <= color[2] <= 127:
   
        return None  # Exclude Lab colors
    return None



# Function to classify styles
def classify_styles(char_info):
    # Remove font subset prefix
    fontname = re.sub(r'^[A-Z]{6}\+', '', char_info['fontname'])
    size = char_info['size']
    rounded_size = round(size)
    stroking_color_rgb = normalize_color_to_rgb(char_info['stroking_color'])
    non_stroking_color_rgb = normalize_color_to_rgb(char_info['non_stroking_color'])
    stroking_color_name = get_color_name_from_rgb(stroking_color_rgb)
    non_stroking_color_name = get_color_name_from_rgb(non_stroking_color_rgb)

    if stroking_color_name is None or non_stroking_color_name is None:
        return None


    size = char_info['size']
    rounded_size = round(size)
    stroking_color_rgb = normalize_color_to_rgb(char_info['stroking_color'])
    non_stroking_color_rgb = normalize_color_to_rgb(char_info['non_stroking_color'])
    stroking_color_name = get_color_name_from_rgb(stroking_color_rgb)
    non_stroking_color_name = get_color_name_from_rgb(non_stroking_color_rgb)

    if stroking_color_name is None or non_stroking_color_name is None:
        return None


    return (
        fontname,
        rounded_size,
        # tuple(char_info['stroking_color']) if char_info['stroking_color'] else None,
        stroking_color_name,
        non_stroking_color_name,
        # tuple(char_info['non_stroking_color']) if char_info['non_stroking_color'] else None,
        'bold' in fontname.replace("-", "").replace("_", "").replace("+", "").replace(" ","").lower(),
        'italic' in fontname.replace("-", "").replace("_", "").replace("+", "").replace(" ","").lower(),
        rounded_size,
        # tuple(char_info['stroking_color']) if char_info['stroking_color'] else None,
        stroking_color_name,
        non_stroking_color_name,
        # tuple(char_info['non_stroking_color']) if char_info['non_stroking_color'] else None,
        'bold' in fontname.replace("-", "").replace("_", "").replace("+", "").replace(" ","").lower(),
        'italic' in fontname.replace("-", "").replace("_", "").replace("+", "").replace(" ","").lower(),
    )

# Function to check if a character is within an image's coordinates
def is_char_in_image(char, image):
    return (
        char['x0'] >= image['x0'] and char['x1'] <= image['x1'] and
        char['y0'] >= image['y0'] and char['y1'] <= image['y1']
    )

# Function to convert PSLiteral objects to strings
def convert_psliteral(obj):
    if isinstance(obj, PSLiteral):
        return str(obj)
    return obj

# Function to extract character information from the PDF
def extract_char_info(pdf_path):
    char_list = []
    undetected_styles = []
    undetected_styles = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            for char in page.chars:
                text = char.get('text')
                # if text and (text.isalpha() or text.isdigit()):  # Check if the character is a letter
                if (text and text.isalpha() and char.get('size') > 0):  # Check if the character is a letter and has a positive size
                    char_info = {
                        'fontname': char.get('fontname'),
                        'size': char.get('size'),
                        'stroking_color': char.get('stroking_color'),
                        'non_stroking_color': char.get('non_stroking_color'),
                        'x0': char.get('x0'),
                        'x1': char.get('x1'),
                        'y0': char.get('y0'),
                        'y1': char.get('y1'),
                        'top': char.get('top'),
                        'bottom': char.get('bottom'),
                        'page_number': page_number
                    }
                    classified_style = classify_styles(char_info)
                    if classified_style and classified_style[1]>0:
                        char_list.append(char_info)
                    else:
                        undetected_styles.append(char_info)
    return char_list, undetected_styles

# Function to extract image information from the PDF
def extract_image_info(pdf_path):
    image_info = {}
    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            images = page.images
            image_info[page_number] = [(img['x0'], img['x1'], img['y0'], img['y1']) for img in images]
    return image_info

# Function to classify styles into text styles and image styles
def classify_styles_into_text_and_image(char_list, image_info):
    text_styles = []
    image_styles = []
    for char_info in char_list:
        page_number = char_info['page_number']
        if page_number in image_info:
            is_image_style = any(
                is_char_in_image(char_info, {'x0': img[0], 'x1': img[1], 'y0': img[2], 'y1': img[3]})
                for img in image_info[page_number]
            )
            if is_image_style:
                image_styles.append(char_info)
            else:
                text_styles.append(char_info)
        else:
            text_styles.append(char_info)
    return text_styles, image_styles

# Function to create unique text styles and populate style_location_mapping
def create_unique_text_styles_and_mapping(text_styles):
    unique_text_styles = []
    temp = []
    for char_info in text_styles:
        style = classify_styles(char_info)
        style_dict = {
            'fontname': style[0],
            'size': style[1],
            'stroking_color': style[2],
            'non_stroking_color': style[3],
            'isBold': style[4],
            'isItalic': style[5]
        }
        if style_dict not in unique_text_styles:
            unique_text_styles.append(style_dict)
            temp.append([{'page_no': char_info['page_number'], 'cord_list': [(char_info['x0'], char_info['top'], char_info['x1'], char_info['bottom'])]}])
        else:
            index = unique_text_styles.index(style_dict)
            page_entry = next((entry for entry in temp[index] if entry['page_no'] == char_info['page_number']), None)
            if page_entry:
                page_entry['cord_list'].append((char_info['x0'], char_info['top'], char_info['x1'], char_info['bottom']))
            else:
                temp[index].append({'page_no': char_info['page_number'], 'cord_list': [(char_info['x0'], char_info['top'], char_info['x1'], char_info['bottom'])]})
    return unique_text_styles, temp

# Function to create the JSON report
def generate_report(pdf_path):
    char_list, undetected_styles = extract_char_info(pdf_path)
    char_list, undetected_styles = extract_char_info(pdf_path)
    image_info = extract_image_info(pdf_path)
    text_styles, image_styles = classify_styles_into_text_and_image(char_list, image_info)
    unique_text_styles, temp = create_unique_text_styles_and_mapping(text_styles)

    # Convert the unique styles list to dictionaries with style_01, style_02, etc.
    unique_text_styles_dict = {}
    style_key_map = {}
    for i, style in enumerate(unique_text_styles, start=0):
        style_key = f"style_{i:02d}"
        unique_text_styles_dict[style_key] = style
        style_key_map[(style['fontname'], style['size'], style['stroking_color'], style['non_stroking_color'], style['isBold'], style['isItalic'])] = style_key
        style_key_map[(style['fontname'], style['size'], style['stroking_color'], style['non_stroking_color'], style['isBold'], style['isItalic'])] = style_key

    # Populate style_location_mapping
    style_location_mapping = {}
    for i, style in enumerate(unique_text_styles):
        style_key = f"style_{i:02d}"
        style_location_mapping[style_key] = temp[i]

    # Create dictionaries to count the frequency of each style
    text_style_frequency = {}
    for char_info in text_styles:
        style = classify_styles(char_info)
        style_key = style_key_map[style]
        if style_key in text_style_frequency:
            text_style_frequency[style_key] += 1
        else:
            text_style_frequency[style_key] = 1

    # Create a JSON object
    result = {
        "unique_styles_in_text": len(unique_text_styles),
        "unique_styles_in_images": len(set(classify_styles(char_info) for char_info in image_styles)),
        "unique_text_styles": unique_text_styles_dict,
        "unique_image_styles": {},  # Populate this similarly if needed
        "sorted_text_style_frequency": dict(sorted(text_style_frequency.items(), key=lambda item: item[1], reverse=True)),
        "sorted_image_style_frequency": {},  # Populate this similarly if needed
        "style_location_mapping": style_location_mapping,
        "undetected_styles": undetected_styles 
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
    unique_image_styles_count_label.config(text=f"Unique Styles in Images: {report['unique_styles_in_images']}")
    
    # Populate the dropdown with style keys
    style_keys = list(report['unique_text_styles'].keys()) + list(report['unique_image_styles'].keys())
    style_dropdown['values'] = style_keys
    style_dropdown.current(0)
    
    # Display the most popular text styles
    popular_text_styles_text.delete(1.0, tk.END)
    popular_text_styles_text.insert(tk.END, "Most Popular Text Styles:\n")
    for style_key, freq in report['sorted_text_style_frequency'].items():
        popular_text_styles_text.insert(tk.END, f"{style_key} (Frequency: {freq})\n")

    # Display the most popular image styles
    popular_image_styles_text.delete(1.0, tk.END)
    popular_image_styles_text.insert(tk.END, "Most Popular Image Styles:\n")
    for style_key, freq in report['sorted_image_style_frequency'].items():
        popular_image_styles_text.insert(tk.END, f"{style_key} (Frequency: {freq})\n")

# Function to handle style selection from the dropdown
def on_style_select(event):
    selected_style = style_dropdown.get()
    if selected_style in report['unique_text_styles']:
        style_info = report['unique_text_styles'][selected_style]
        frequency = report['sorted_text_style_frequency'].get(selected_style, 0)
    else:
        style_info = report['unique_image_styles'][selected_style]
        frequency = report['sorted_image_style_frequency'].get(selected_style, 0)
    
    style_info_text.delete(1.0, tk.END)
    style_info_text.insert(tk.END, f"{selected_style} (Frequency: {frequency}):\n")
    for key, value in style_info.items():
        style_info_text.insert(tk.END, f"  {key}: {value}\n")
    
    # Draw rectangles around characters with the selected style
    if selected_style in report['style_location_mapping']:
        for page_entry in report['style_location_mapping'][selected_style]:
            page_number = page_entry['page_no']
            coordinates = page_entry['cord_list']
            with pdfplumber.open(pdf_path) as pdf:
                page = pdf.pages[page_number - 1]
                im = page.to_image(resolution=150)
                im.draw_rects(coordinates, fill=None, stroke="red", stroke_width=2)
                im.show()

# Function to open a file dialog and select a PDF
def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if file_path:
        global report, pdf_path
        pdf_path = file_path
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

unique_image_styles_count_label = tk.Label(root, text="Unique Styles in Images: ")
unique_image_styles_count_label.pack(pady=10)

style_dropdown_label = tk.Label(root, text="Select Style:")
style_dropdown_label.pack(pady=5)

style_dropdown = ttk.Combobox(root)
style_dropdown.pack(pady=5)
style_dropdown.bind("<<ComboboxSelected>>", on_style_select)

style_info_text = tk.Text(root, height=10, width=50)
style_info_text.pack(pady=10)

popular_text_styles_label = tk.Label(root, text="Most Popular Text Styles:")
popular_text_styles_label.pack(pady=5)

popular_text_styles_text = tk.Text(root, height=10, width=50)
popular_text_styles_text.pack(pady=10)

popular_image_styles_label = tk.Label(root, text="Most Popular Image Styles:")
popular_image_styles_label.pack(pady=5)

popular_image_styles_text = tk.Text(root, height=10, width=50)
popular_image_styles_text.pack(pady=10)

# Start the main loop
root.mainloop()