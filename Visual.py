import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pdfplumber
import json
import os
import re
from pdfminer.psparser import PSLiteral

# Function to classify styles
def classify_styles(char_info):
    # Remove font subset prefix
    fontname = re.sub(r'^[A-Z]{6}\+', '', char_info['fontname'])
    return (
        fontname,
        round(char_info['size']),
        tuple(char_info['stroking_color']) if char_info['stroking_color'] else None,
        tuple(char_info['non_stroking_color']) if char_info['non_stroking_color'] else None
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

# Function to generate JSON report for a single PDF
def generate_report(pdf_path):
    chars_list = []
    image_chars_list = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            images = page.images
            for char in page.chars:
                char_info = {
                    'fontname': char.get('fontname'),
                    'size': char.get('size'),
                    'stroking_color': char.get('stroking_color'),
                    'non_stroking_color': char.get('non_stroking_color'),
                    'x0': char.get('x0'),
                    'x1': char.get('x1'),
                    'y0': char.get('y0'),
                    'y1': char.get('y1')
                }
                if any(is_char_in_image(char, image) for image in images):
                    image_chars_list.append(classify_styles(char_info))
                else:
                    chars_list.append(classify_styles(char_info))

    # Use sets to store unique styles
    unique_text_styles_set = set(chars_list)
    unique_image_styles_set = set(image_chars_list)

    # Convert the sets to dictionaries with style_01, style_02, etc.
    unique_text_styles = {}
    unique_image_styles = {}
    style_key_map = {}
    for i, style in enumerate(unique_text_styles_set, start=1):
        style_key = f"style_{i:02d}"
        fontname, size, stroking_color, non_stroking_color = style
        unique_text_styles[style_key] = {
            'fontname': fontname,
            'size': size,
            'stroking_color': list(stroking_color) if stroking_color else None,
            'non_stroking_color': list(non_stroking_color) if non_stroking_color else None
        }
        normalized_fontname = fontname.replace("-", "").replace("_", "").replace("+", "").lower()
        if 'bold' in normalized_fontname:
            unique_text_styles[style_key]['is_Bold'] = True
        if 'italic' in normalized_fontname:
            unique_text_styles[style_key]['is_Italic'] = True
        style_key_map[style] = style_key

    for i, style in enumerate(unique_image_styles_set, start=len(unique_text_styles_set) + 1):
        style_key = f"style_{i:02d}"
        fontname, size, stroking_color, non_stroking_color = style
        unique_image_styles[style_key] = {
            'fontname': fontname,
            'size': size,
            'stroking_color': list(stroking_color) if stroking_color else None,
            'non_stroking_color': list(non_stroking_color) if non_stroking_color else None
        }
        normalized_fontname = fontname.replace("-", "").replace("_", "").replace("+", "").lower()
        if 'bold' in normalized_fontname:
            unique_image_styles[style_key]['is_Bold'] = True
        if 'italic' in normalized_fontname:
            unique_image_styles[style_key]['is_Italic'] = True
        style_key_map[style] = style_key

    # Create dictionaries to count the frequency of each style
    text_style_frequency = {}
    image_style_frequency = {}
    for style in chars_list:
        style_key = style_key_map[style]
        if style_key in text_style_frequency:
            text_style_frequency[style_key] += 1
        else:
            text_style_frequency[style_key] = 1

    for style in image_chars_list:
        style_key = style_key_map[style]
        if style_key in image_style_frequency:
            image_style_frequency[style_key] += 1
        else:
            image_style_frequency[style_key] = 1

    # Create a JSON object
    result = {
        # "unique_styles_count": len(unique_text_styles) + len(unique_image_styles),
        "unique_styles_in_text": len(unique_text_styles),
        "unique_styles_in_images": len(unique_image_styles),
        "unique_text_styles": unique_text_styles,
        "unique_image_styles": unique_image_styles,
        "sorted_text_style_frequency": dict(sorted(text_style_frequency.items(), key=lambda item: item[1], reverse=True)),
        "sorted_image_style_frequency": dict(sorted(image_style_frequency.items(), key=lambda item: item[1], reverse=True))
    }

    # Save the JSON object to a file
    result_filename = f"result_{os.path.basename(pdf_path).replace('.pdf', '')}.json"
    with open(result_filename, "w") as json_file:
        json.dump(result, json_file, indent=4)

    print(f"JSON object saved to {result_filename}")

    return result

# Function to display the report in the UI
def display_report(report):
    # unique_styles_count_label.config(text=f"Unique Styles Count: {report['unique_styles_count']}")
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

# unique_styles_count_label = tk.Label(root, text="Unique Styles Count: ")
# unique_styles_count_label.pack(pady=10)

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