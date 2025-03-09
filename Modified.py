import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pdfplumber
import json
import os
import re

# Step 1: Extract all the characters
def extract_characters(pdf_path):
    chars_list = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            for char in page.chars:
                fontname = re.sub(r'^[A-Z]{6}\+', '', char.get('fontname'))
                char_info = {
                    'page_number': page.page_number,
                    'text': char.get('text'),
                    'fontname': fontname,
                    'size': round(char.get('size')),
                    'x0': char.get('x0'),
                    'x1': char.get('x1'),
                    'y0': char.get('y0'),
                    'y1': char.get('y1'),
                    'stroking_color': char.get('stroking_color'),
                    'non_stroking_color': char.get('non_stroking_color')
                }
                chars_list.append(char_info)
    return chars_list

# Step 2: Extract all the images
def extract_images(pdf_path):
    img_dict = {}
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            for img in page.images:
                img_info = (img.get('x0'), img.get('x1'), img.get('y0'), img.get('y1'))
                if page.page_number not in img_dict:
                    img_dict[page.page_number] = []
                img_dict[page.page_number].append(img_info)
    return img_dict

# Step 3: Separate characters for image_text_styles and character_text_styles
def separate_text_styles(chars_list, img_dict):
    character_text_styles = []
    image_text_styles = []
    for char in chars_list:
        page_no = char['page_number']
        if page_no in img_dict:
            is_image_text = False
            for img_coords in img_dict[page_no]:
                if (img_coords[0] <= char['x0']  and char['x1'] <= img_coords[1] and img_coords[2] <= char['y0']  and img_coords[3] >= char['y1'] ):
                    is_image_text = True
                    break
            if is_image_text:
                image_text_styles.append(char)
            else:
                character_text_styles.append(char)
        else:
            character_text_styles.append(char)
    return character_text_styles, image_text_styles

# Step 4: Combine characters into words
def combine_characters_to_words(character_text_styles):
    words_list = []
    current_word = []
    for char in character_text_styles:
        if char['text'] == ' ':
            if current_word:
                words_list.append(current_word)
                current_word = []
        else:
            current_word.append(char)
    if current_word:
        words_list.append(current_word)
    
    word_style_list = []
    for word_chars in words_list:
        word_text = ''.join([char['text'] for char in word_chars])
        word_info = {
            'page_no': word_chars[0]['page_number'],
            'text': word_text,
            'fontname': word_chars[0]['fontname'],
            'size': round(word_chars[0]['size']),
            'x0': word_chars[0]['x0'],
            'x1': word_chars[-1]['x1'],
            'y0': min(char['y0'] for char in word_chars),
            'y1': max(char['y1'] for char in word_chars),
            'stroking_color': word_chars[0]['stroking_color'],
            'non_stroking_color': word_chars[0]['non_stroking_color'],
            'isBold': 'bold' in word_chars[0]['fontname'].lower(),
            'isItalic': 'italic' in word_chars[0]['fontname'].lower()
        }
        word_style_list.append(word_info)
    return word_style_list

# Step 5: Create the style_location_mapping and unique_text_styles
def create_style_mapping(word_style_list):
    unique_text_styles = []
    style_location_mapping = {}
    for word in word_style_list:
        style = {
            'fontname': word['fontname'],
            'size': round(word['size']),
            'stroking_color': word['stroking_color'],
            'non_stroking_color': word['non_stroking_color'],
            'isBold': word['isBold'],
            'isItalic': word['isItalic']
        }
        if style not in unique_text_styles:
            unique_text_styles.append(style)
            style_key = f"style_{len(unique_text_styles) - 1:02d}"
            style_location_mapping[style_key] = []
        else:
            style_key = f"style_{unique_text_styles.index(style):02d}"
        
        page_entry = next((entry for entry in style_location_mapping[style_key] if entry['page_no'] == word['page_no']), None)
        if page_entry:
            page_entry['cord_list'].append((word['x0'], word['x1'], word['y0'], word['y1']))
        else:
            style_location_mapping[style_key].append({
                'page_no': word['page_no'],
                'cord_list': [(word['x0'], word['x1'], word['y0'], word['y1'])]
            })
    return unique_text_styles, style_location_mapping

# Step 6: Generate the word frequency for each style
def generate_word_frequency(word_style_list, unique_text_styles):
    style_frequency = {i: 0 for i in range(len(unique_text_styles))}
    for word in word_style_list:
        style = {
            'fontname': word['fontname'],
            'size': round(word['size']),
            'stroking_color': word['stroking_color'],
            'non_stroking_color': word['non_stroking_color'],
            'isBold': word['isBold'],
            'isItalic': word['isItalic']
        }
        index = unique_text_styles.index(style)
        style_frequency[index] += 1
    return style_frequency

# Step 7: Create unique image styles
def create_unique_image_styles(image_text_styles):
    unique_image_styles = []
    for char in image_text_styles:
        style = {
            'fontname': char['fontname'],
            'size': round(char['size']),
            'stroking_color': char['stroking_color'],
            'non_stroking_color': char['non_stroking_color'],
            'isBold': 'bold' in char['fontname'].lower(),
            'isItalic': 'italic' in char['fontname'].lower()
        }
        if style not in unique_image_styles:
            unique_image_styles.append(style)
    return unique_image_styles

# Main function to generate the report
def generate_report(pdf_path):
    chars_list = extract_characters(pdf_path)
    img_dict = extract_images(pdf_path)
    character_text_styles, image_text_styles = separate_text_styles(chars_list, img_dict)
    word_style_list = combine_characters_to_words(character_text_styles)
    unique_text_styles, style_location_mapping = create_style_mapping(word_style_list)
    style_frequency = generate_word_frequency(word_style_list, unique_text_styles)
    unique_image_styles = create_unique_image_styles(image_text_styles)
    
    result = {
        "unique_styles_count": len(unique_text_styles),
        "unique_image_styles_count": len(unique_image_styles),
        "unique_text_styles": unique_text_styles,
        "unique_image_styles": unique_image_styles,
        "sorted_text_style_frequency": dict(sorted(style_frequency.items(), key=lambda item: item[1], reverse=True)),
        "style_location_mapping": style_location_mapping
    }
    
    result_filename = f"result_{os.path.basename(pdf_path).replace('.pdf', '')}.json"
    with open(result_filename, "w") as json_file:
        json.dump(result, json_file, indent=4)
    
    print(f"JSON object saved to {result_filename}")
    return result

# Function to display the report in the UI
def display_report(report):
    unique_text_styles_count_label.config(text=f"Unique Styles in Text: {report['unique_styles_count']}")
    unique_image_styles_count_label.config(text=f"Unique Styles in Images: {report['unique_image_styles_count']}")
    
    # Populate the dropdown with style indices
    style_keys = [str(i) for i in range(len(report['unique_text_styles']))]
    style_dropdown['values'] = style_keys
    style_dropdown.current(0)
    
    # Display the most popular text styles
    popular_text_styles_text.delete(1.0, tk.END)
    popular_text_styles_text.insert(tk.END, "Most Popular Text Styles:\n")
    for style_key, freq in report['sorted_text_style_frequency'].items():
        popular_text_styles_text.insert(tk.END, f"Style {style_key} (Frequency: {freq})\n")

# Function to handle style selection from the dropdown
# Function to handle style selection from the dropdown
# Function to handle style selection from the dropdown
def on_style_select(event):
    selected_style_index = int(style_dropdown.get())
    style_info = report['unique_text_styles'][selected_style_index]
    frequency = report['sorted_text_style_frequency'].get(str(selected_style_index), 0)

    style_info_text.delete(1.0, tk.END)
    style_info_text.insert(tk.END, f"Style {selected_style_index} (Frequency: {frequency}):\n")
    for key, value in style_info.items():
        style_info_text.insert(tk.END, f"  {key}: {value}\n")
    
    # Draw rectangles around characters with the selected style
    style_key = f"style_{selected_style_index:02d}"
    if style_key in report['style_location_mapping']:
        for page_entry in report['style_location_mapping'][style_key]:
            page_number = page_entry['page_no']
            coordinates = page_entry['cord_list']
            with pdfplumber.open(pdf_path) as pdf:
                page = pdf.pages[page_number - 1]
                im = page.to_image(resolution=150)
                # Ensure y0 is less than or equal to y1
                sorted_coordinates = []
                for (x0, x1, y0, y1) in coordinates:
                    print(f"Original coordinates: {(x0, x1, y0, y1)}")
                    if y0 > y1:
                        print(f"Swapping y0 and y1 for coordinates: {(x0, x1, y0, y1)}")
                        y0, y1 = y1, y0
                    sorted_coordinates.append((x0, x1, y0, y1))
                print(f"Drawing rectangles with coordinates: {sorted_coordinates}")
                try:
                    im.draw_rects(sorted_coordinates, fill=None, stroke="red", stroke_width=2)
                except ValueError as e:
                    print(f"Error drawing rectangles: {e}")
                    for coord in sorted_coordinates:
                        print(f"Attempting to draw rectangle with coordinates: {coord}")
                        try:
                            im.draw_rect(coord, fill=None, stroke="red", stroke_width=2)
                        except ValueError as e:
                            print(f"Failed to draw rectangle with coordinates: {coord}, Error: {e}")
                im.show()

# Function to open a file dialog and select a PDF
def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if file_path:
        global report, pdf_path
        pdf_path = file_path
        report = generate_report(pdf_path)
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

# Start the main loop
root.mainloop()