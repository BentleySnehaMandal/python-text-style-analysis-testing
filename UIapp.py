import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pdfplumber
import json
import os
import re

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

# Function to generate JSON report for a single PDF
def generate_report(pdf_path):
    chars_list = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            for char in page.chars:
                char_info = {
                    'fontname': char.get('fontname'),
                    'size': char.get('size'),
                    'stroking_color': char.get('stroking_color'),
                    'non_stroking_color': char.get('non_stroking_color')
                }
                chars_list.append(classify_styles(char_info))

    print(f"Total characters: {len(chars_list)}")
    # Use a set to store unique styles
    unique_styles_set = set(chars_list)
    print(f"Unique styles count: {len(unique_styles_set)}")

    # Convert the set to a dictionary with style_01, style_02, etc.
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

    # Create a dictionary to count the frequency of each style
    style_frequency = {}
    for style in chars_list:
        style_key = style_key_map[style]
        if style_key in style_frequency:
            style_frequency[style_key] += 1
        else:
            style_frequency[style_key] = 1

    # Create a JSON object
    result = {
        "unique_styles_count": len(unique_styles),
        "unique_styles": unique_styles,
        "sorted_style_frequency": dict(sorted(style_frequency.items(), key=lambda item: item[1], reverse=True))
    }

    # Save the JSON object to a file
    result_filename = f"result_{os.path.basename(pdf_path).replace('.pdf', '')}.json"
    with open(result_filename, "w") as json_file:
        json.dump(result, json_file, indent=4)

    print(f"JSON object saved to {result_filename}")

    return result

# Function to display the report in the UI
def display_report(report):
    unique_styles_count_label.config(text=f"Unique Styles Count: {report['unique_styles_count']}")
    
    # Populate the dropdown with style keys
    style_keys = list(report['unique_styles'].keys())
    style_dropdown['values'] = style_keys
    style_dropdown.current(0)
    
    # Display the most popular styles
    popular_styles_text.delete(1.0, tk.END)
    for style_key, freq in report['sorted_style_frequency'].items():
        style_info = report['unique_styles'][style_key]
        popular_styles_text.insert(tk.END, f"{style_key} (Frequency: {freq}):\n")
        for key, value in style_info.items():
            popular_styles_text.insert(tk.END, f"  {key}: {value}\n")
        popular_styles_text.insert(tk.END, "\n")

# Function to handle style selection from the dropdown
def on_style_select(event):
    selected_style = style_dropdown.get()
    style_info = report['unique_styles'][selected_style]
    frequency = report['sorted_style_frequency'][selected_style]
    
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

unique_styles_count_label = tk.Label(root, text="Unique Styles Count: ")
unique_styles_count_label.pack(pady=10)

style_dropdown_label = tk.Label(root, text="Select Style:")
style_dropdown_label.pack(pady=5)

style_dropdown = ttk.Combobox(root)
style_dropdown.pack(pady=5)
style_dropdown.bind("<<ComboboxSelected>>", on_style_select)

style_info_text = tk.Text(root, height=10, width=50)
style_info_text.pack(pady=10)

popular_styles_label = tk.Label(root, text="Most Popular Styles:")
popular_styles_label.pack(pady=5)

popular_styles_text = tk.Text(root, height=10, width=50)
popular_styles_text.pack(pady=10)

# Start the main loop
root.mainloop()