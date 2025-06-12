import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import Counter
import json
import os
import re
import pdfplumber
from pdfminer.psparser import PSLiteral
import webcolors
from pdfplumber.ctm import CTM
from PIL import Image, ImageDraw, ImageFont
import math
import fitz


def calculate_skew_angle(matrix):
    skew_angle = round(math.degrees(math.atan2(matrix[1], matrix[0])), 2)
    return skew_angle


def adjust_font_size(chars):
    """
    Group characters into words, determine font styles, and calculate word coordinates.
    :param chars: List of character objects with non-zero skewness.
    :return: List of word information with consistent styles.
    """
    grouped_words = []
    current_word = []

    def normalize_fontname(fontname):
        """
        Normalize font names by removing font subsetting and special characters, and converting to lowercase.
        """
        # Remove font subsetting prefix (e.g., "ABCDE+Arial" -> "Arial")
        normalized_fontname = re.sub(r'^[A-Z]{6}\+', '', fontname)
        # Remove special characters and convert to lowercase
        return normalized_fontname.replace("-", "").replace("_", "").replace("+", "").replace(" ", "").lower()

    
    def is_same_word(char1, char2):
        """
        Check if two characters belong to the same word based on proximity, skew angle, and normalized font name.
        """
    # Normalize font names
        fontname1 = normalize_fontname(char1['fontname'])
        fontname2 = normalize_fontname(char2['fontname'])

    # Check if font names are consistent
        if fontname1 != fontname2:
            return False

    # Get skew angles
        skew1 = char1['skew_angle']
        skew2 = char2['skew_angle']

    # Check if skew angles are similar
        if abs(skew1 - skew2) > 1e-2:  # Allow a small tolerance for skew differences
            return False

    # Determine the dominant axis based on the skew angle
        if abs(skew1) < 10 or abs(skew1 - 180) < 10:  # Close to horizontal
        # Horizontal text: prioritize x-dimension for proximity
            horizontal_proximity = abs(char1['x1'] - char2['x0']) < 5  # Adjust threshold as needed
            # vertical_alignment = abs(char1['y0'] - char2['y0']) < 5 and abs(char1['y1'] - char2['y1']) < 5
            return horizontal_proximity 
        elif abs(skew1 - 90) < 10 or abs(skew1 + 90) < 10:  # Close to vertical
             # Vertical text: prioritize y-dimension for proximity
            vertical_proximity = abs(char1['y1'] - char2['y0']) < 5  # Adjust threshold as needed
            # horizontal_alignment = abs(char1['x0'] - char2['x0']) < 5
            return vertical_proximity 
        else:
         # Intermediate skew: use projections along the skew direction
            angle_rad = skew1
            dx1 = (char1['x1'] - char1['x0']) * math.cos(angle_rad)
            dy1 = (char1['y1'] - char1['y0']) * math.sin(angle_rad)
            dx2 = (char2['x1'] - char2['x0']) * math.cos(angle_rad)
            dy2 = (char2['y1'] - char2['y0']) * math.sin(angle_rad)

        # Check proximity along the skew direction
            proximity = abs((dx1 + dy1) - (dx2 + dy2)) < 5  # Adjust threshold as needed
            return proximity

    for char in chars:
        if current_word and is_same_word(current_word[-1], char):

            current_word.append(char)
        else:

            if current_word:
                grouped_words.append(current_word)
            current_word = [char]

   
    if current_word:
        grouped_words.append(current_word)

    # Normalize styles and calculate word coordinates
    word_info_list = []
    for word in grouped_words:
        # Use the font style of the first character as the reference
        reference_style = word[0]
        adjusted_sizes = []
        for char in word:
            skew_angle_rad = char['skew_angle']
            if abs(char['skew_angle'] - 90) < 1e-2 or abs(char['skew_angle'] + 90) < 1e-2:
                # For skew angles close to 90° or -90°, use the sine component
                adjusted_size = round(char['size'] * abs(math.sin(skew_angle_rad)))
            else:
                # For other angles, use the cosine component
                adjusted_size =round(char['size'] * abs(math.cos(skew_angle_rad)))
            adjusted_sizes.append(adjusted_size)

        
        size_counts = Counter(adjusted_sizes)
        mode_font_size = max(size_counts, key=size_counts.get)
        # average_font_size = round(sum(adjusted_sizes)/len(adjusted_sizes)) 
        average_font_size = round(mode_font_size)
       

        # print(word)
        # average_font_size = round(max(char['size'] for char in word)) 

        for char in word:
            char_info = {
                'fontname': char['fontname'],  # Use normalized font name
                'size': average_font_size,  # Update size to the average font size
                'stroking_color': char['stroking_color'],
                'non_stroking_color': char['non_stroking_color'],
                'x0': char['x0'],
                'x1': char['x1'],
                'y0': char['y0'],
                'y1': char['y1'],
                'top': char['top'],
                'bottom': char['bottom'],
                'skew_angle': char['skew_angle'],
                'page_number': char['page_number'],
                'text': char['text']  # Include the character text
            }
            word_info_list.append(char_info)


    return word_info_list



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
    

def normalize_color_to_rgb(color, color_space):
    """
    Normalize the color to an RGB tuple based on the color space.
    :param color: The color value (tuple or list).
    :param color_space: The color space (e.g., DeviceRGB, DeviceGray, etc.).
    :return: A normalized RGB tuple or None if the color space is unsupported.
    """
    if color is None:
        # Treat null colors as black
        return (0, 0, 0)  # RGB for black

    # DeviceGray color space
    if color_space == "DeviceGray":
        if len(color) == 1:  # Ensure the color tuple has one component
            gray_value = int(color[0] * 255)
            return (gray_value, gray_value, gray_value)
        else:
            return (0, 0, 0)  # Default to black for invalid color

    # DeviceRGB color space
    if color_space == "DeviceRGB":
        if len(color) == 3:  # Ensure the color tuple has three components
            r, g, b = [int(c * 255) for c in color]
            return (r, g, b)
        else:
            # Handle cases where the color tuple has fewer than 3 components
            scaled_color = [int(c * 255) for c in color]  # Scale available values
            while len(scaled_color) < 3:
                scaled_color.append(0)  # Fill missing components with 0
            return tuple(scaled_color[:3])  # Ensure exactly 3 components

    # DeviceCMYK color space
    if color_space == "DeviceCMYK":
        if len(color) == 4:  # Ensure the color tuple has four components
            c, m, y, k = color
            r = int(255 * (1 - c) * (1 - k))
            g = int(255 * (1 - m) * (1 - k))
            b = int(255 * (1 - y) * (1 - k))
            return (r, g, b)
        else:
            return None  # Default to black for invalid color

    # Handle Lab color space (exclude unsupported Lab colors)
    if color_space == "Lab":
        return None  # Exclude Lab colors

    # Unsupported or special color spaces
    return None



def classify_styles(char_info):
    # Remove font subset prefix
    fontname = re.sub(r'^[A-Z]{6}\+', '', char_info['fontname'])
    size = char_info['size']

    bucket_size = 3

    lower_bound = math.floor(size / bucket_size) * bucket_size
    middle_value = lower_bound + (bucket_size / 2)
    rounded_size = round(middle_value)
    # rounded_size = round(math.floor(size / bucket_size) * bucket_size)
    # rounded_size = round(math.ceil(size / bucket_size) * bucket_size)

    color_space = char_info.get('ncs', None)

    # rounded_size = ((size // bucket_size) * bucket_size) + (bucket_size // 2)
    stroking_color_rgb = normalize_color_to_rgb(char_info['stroking_color'],color_space)
    non_stroking_color_rgb = normalize_color_to_rgb(char_info['non_stroking_color'],color_space)
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
    )


def is_char_in_image(char, image):
    return (
        char['x0'] >= image['x0'] and char['x1'] <= image['x1'] and
        char['y0'] >= image['y0'] and char['y1'] <= image['y1']
    )


def convert_psliteral(obj):
    if isinstance(obj, PSLiteral):
        return str(obj)
    return obj


def extract_char_info(pdf_path):
    """
    Extract character details from the PDF and handle vertical/skewed text issues.
    :param pdf_path: Path to the PDF file.
    :return: List of character details and undetected styles.
    """
    char_list = []
    undetected_styles = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            temp_chars = []  # Temporary list to store characters with the same skewness
            for char in page.chars:
                text = char.get('text')
                page_rotation = page.rotation or 0

                if text and text.isalpha() and char.get('size') > 0:  
                   
                    matrix = char.get("matrix", [1, 0, 0, 1, 0, 0])
                    skew_angle = calculate_skew_angle(matrix)

                    if skew_angle == 0.0:
                        # For horizontal text, directly add to char_list
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
                            'skew_angle': skew_angle,
                            'page_number': page_number,
                            'ncs': char.get('ncs'),
                        }
                        char_list.append(char_info)
                    else:
                        # For non-horizontal text, add to temporary list
                        temp_chars.append({
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
                            'skew_angle': skew_angle,
                            'page_number': page_number,
                            'text': text,
                            'ncs': char.get('ncs'),

                        })

            # Process non-horizontal text
            if temp_chars:
                word_info_list = adjust_font_size(temp_chars)
                char_list.extend(word_info_list)

    return char_list, undetected_styles


def extract_image_info(pdf_path):
    image_info = {}
    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            images = page.images
            image_info[page_number] = [(img['x0'], img['x1'], img['y0'], img['y1']) for img in images]
    return image_info

#  classify styles into text styles and image styles
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
                # text_styles.append(char_info)
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
            temp.append([{
                'page_no': char_info['page_number'],
                'cord_list': [{'skew': char_info['skew_angle'], 'loc': [char_info['x0'], char_info['top'], char_info['x1'], char_info['bottom']]}]
            }])
        else:
            index = unique_text_styles.index(style_dict)
            page_entry = next((entry for entry in temp[index] if entry['page_no'] == char_info['page_number']), None)
            if page_entry:
                page_entry['cord_list'].append({'skew': char_info['skew_angle'], 'loc': [char_info['x0'], char_info['top'], char_info['x1'], char_info['bottom']]})
            else:
                temp[index].append({
                    'page_no': char_info['page_number'],
                    'cord_list': [{'skew': char_info['skew_angle'], 'loc': [char_info['x0'], char_info['top'], char_info['x1'], char_info['bottom']]}]
                })
    return unique_text_styles, temp

# Function to create the JSON report
def generate_report(pdf_path):
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



def normalize_fontname(fontname):
    """
    Normalize font names by removing font subsetting and special characters, and converting to lowercase.
    """
    normalized_fontname = re.sub(r'^[A-Z]{6}\+', '', fontname)
    normalized_fontname = normalized_fontname.replace("-", "").replace("_", "").replace("+", "").replace(" ", "").lower()
    normalized_fontname = normalized_fontname.replace("bold", "").replace("italic", "").strip()
    return normalized_fontname

#  process font data
def process_fonts(report):
    unique_text_styles = report["unique_text_styles"]
    sorted_text_style_frequency = report["sorted_text_style_frequency"]

    font_style_frequency = Counter()
    font_character_frequency = Counter()
    font_size_data = {}

    for style_key, style in unique_text_styles.items():
        fontname = normalize_fontname(style["fontname"])
        size = style["size"]
        style_frequency = sorted_text_style_frequency.get(style_key, 0)

        
        font_style_frequency[fontname] += 1

        
        font_character_frequency[fontname] += style_frequency

       
        if fontname not in font_size_data:
            font_size_data[fontname] = Counter()
        font_size_data[fontname][size] +=style_frequency

    return font_style_frequency, font_character_frequency, font_size_data


def generate_bar_graph(data, title, x_label, y_label):
    fig, ax = plt.subplots(figsize=(8, 6))
    keys = list(data.keys())
    values = list(data.values())

    bars = ax.bar(keys, values, color="blue")
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_xticks(range(len(keys)))
    ax.set_xticklabels(keys, rotation=45, ha="right")

   
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,  # X-coordinate (center of the bar)
            height,  # Y-coordinate (top of the bar)
            f"{int(height)}",  # Text to display (convert to integer)
            ha="center",  
            va="bottom",  
            fontsize=10,  
            color="black"  
        )

    return fig

# Function to generate pie chart
def generate_pie_chart(data, title):
    fig, ax = plt.subplots(figsize=(8, 6))
    labels = list(data.keys())
    sizes = list(data.values())

    ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=140)
    ax.set_title(title)

    return fig

# Function to generate horizontal bar graph for font sizes
def generate_horizontal_bar_graph(data, title, x_label, y_label):
    fig, ax = plt.subplots(figsize=(8, 6))
    keys = list(data.keys())
    values = [int(value) for value in data.values()]  # Ensure values are integers

    # Check if there is only one size with a frequency of 1
    if len(keys) == 1 and values[0] == 1:
        ax.set_xlim(0, 2)  
        ax.set_yticks(keys) 
        ax.set_yticklabels(keys)  
    else:
        ax.set_yticks(keys) 
        ax.set_yticklabels(keys) 

    bars = ax.barh(keys, values, color="green")
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    # Add frequency numbers next to the bars
    for bar in bars:
        width = bar.get_width()
        ax.text(
            width,  # X-coordinate (end of the bar)
            bar.get_y() + bar.get_height() / 2,  # Y-coordinate (center of the bar)
            f"{int(width)}",  # Text to display (convert to integer)
            ha="left",  # Horizontal alignment
            va="center",  # Vertical alignment
            fontsize=10,  # Font size
            color="black"  # Text color
        )

    return fig



def display_graph(tab, fig):
    for widget in tab.winfo_children():
        widget.destroy()

    canvas = FigureCanvasTkAgg(fig, master=tab)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)



#  handle font selection from the dropdown
def on_font_select(event):
    selected_font = font_dropdown.get()
    if selected_font in font_size_data:
        # Generate the horizontal bar graph for the selected font
        font_size_graph = generate_horizontal_bar_graph(
            font_size_data[selected_font],
            f"Font Sizes for {selected_font}",
            "Frequency",
            "Font Sizes"
        )

        # Generate the pie chart for the selected font
        font_size_pie_chart = generate_pie_chart(
            font_size_data[selected_font],
            f"Font Size Distribution for {selected_font}"
        )

        # Display the horizontal bar graph in the horizontal_graph_tab
        for widget in horizontal_graph_tab.winfo_children():
            widget.destroy()
        canvas = FigureCanvasTkAgg(font_size_graph, master=horizontal_graph_tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Display the pie chart in the pie_chart_tab
        for widget in pie_chart_tab.winfo_children():
            widget.destroy()
        canvas = FigureCanvasTkAgg(font_size_pie_chart, master=pie_chart_tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    else:
        # Clear the tabs if no data is available for the selected font
        for widget in horizontal_graph_tab.winfo_children():
            widget.destroy()
        tk.Label(horizontal_graph_tab, text="No data available for the selected font.").pack()

        for widget in pie_chart_tab.winfo_children():
            widget.destroy()
        tk.Label(pie_chart_tab, text="No data available for the selected font.").pack()

# Function to open files and process PDFs
def open_files():
    file_paths = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
    if file_paths:
        combined_report = {
            "unique_text_styles": {},
            "sorted_text_style_frequency": {}
        }
        for file_path in file_paths:
            report = generate_report(file_path)  # Assuming generate_report is implemented
            combined_report["unique_text_styles"].update(report["unique_text_styles"])
            combined_report["sorted_text_style_frequency"].update(report["sorted_text_style_frequency"])

        # Process fonts
        global font_style_frequency, font_character_frequency, font_size_data
        font_style_frequency, font_character_frequency, font_size_data = process_fonts(combined_report)

        # Generate graphs
        style_bar_graph = generate_bar_graph(font_style_frequency, "Style-Wise Frequency", "Fonts", "Frequency")
        style_pie_chart = generate_pie_chart(font_style_frequency, "Style-Wise Frequency Percentage")
        char_bar_graph = generate_bar_graph(font_character_frequency, "Character-Wise Frequency", "Fonts", "Frequency")
        char_pie_chart = generate_pie_chart(font_character_frequency, "Character-Wise Frequency Percentage")

        # Display graphs in tabs
        display_graph(tab1, style_bar_graph)
        display_graph(tab2, style_pie_chart)
        display_graph(tab3, char_bar_graph)
        display_graph(tab4, char_pie_chart)

        # Populate font dropdown
        font_dropdown["values"] = list(font_size_data.keys())
        font_dropdown.current(0)
        on_font_select(None)  

# Create the main window
root = tk.Tk()
root.title("PDF Font Analysis Tool")
root.geometry("900x900")

# Create a scrollable canvas
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)

canvas = tk.Canvas(main_frame)
scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
scrollable_frame = tk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Create a Notebook widget (tabs)
notebook = ttk.Notebook(scrollable_frame)
notebook.pack(fill=tk.X, expand=False, pady=5)  # Reduce the height of the tabs section

# Create tabs
tab1 = ttk.Frame(notebook)
tab2 = ttk.Frame(notebook)
tab3 = ttk.Frame(notebook)
tab4 = ttk.Frame(notebook)
font_size_tab = ttk.Frame(notebook)

notebook.add(tab1, text="Style-Wise Bar Graph")
notebook.add(tab2, text="Style-Wise Pie Chart")
notebook.add(tab3, text="Character-Wise Bar Graph")
notebook.add(tab4, text="Character-Wise Pie Chart")
notebook.add(font_size_tab, text="Font Size Analysis")

# Add Open Files button
open_button = tk.Button(scrollable_frame, text="Open PDFs", command=open_files)
open_button.pack(pady=10)

# Add font dropdown
font_dropdown_label = tk.Label(scrollable_frame, text="Select Font:")
font_dropdown_label.pack(pady=5)

font_dropdown = ttk.Combobox(scrollable_frame)
font_dropdown.pack(pady=5)
font_dropdown.bind("<<ComboboxSelected>>", on_font_select)

# Create a frame for the horizontal bar graph
font_analysis_notebook = ttk.Notebook(scrollable_frame)
font_analysis_notebook.pack(fill=tk.BOTH, expand=True, pady=10)

# Create tabs for the pie chart and horizontal graph
pie_chart_tab = ttk.Frame(font_analysis_notebook)
horizontal_graph_tab = ttk.Frame(font_analysis_notebook)

font_analysis_notebook.add(pie_chart_tab, text="Font Size Pie Chart")
font_analysis_notebook.add(horizontal_graph_tab, text="Font Size Horizontal Graph")

# Start the main loop
root.mainloop()