import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import Counter
import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
import tempfile
import os
from PIL import Image

def generate_pdf_report(font_style_frequency, font_character_frequency, font_size_data):
    pdf_file = "Font_Analysis_Report0001.pdf"
    c = pdf_canvas.Canvas(pdf_file, pagesize=letter)
    width, height = letter
    margin = 50
    y_position = height - margin

    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin, y_position, "Font Analysis Report")
    y_position -= 40

    # --- Style-Wise Frequency Table ---
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y_position, "Style-Wise Frequency Distribution")
    y_position -= 20
    style_data = []
    total_styles = sum(font_style_frequency.values())
    for font, freq in font_style_frequency.items():
        percentage = (freq / total_styles) * 100 if total_styles else 0
        style_data.append((font, freq, percentage))
    style_data_sorted = sorted(style_data, key=lambda x: x[2], reverse=True)
    table_data = [["Font Name", "Frequency", "Percentage"]]
    for font, freq, percentage in style_data_sorted:
        table_data.append([font, freq, f"{percentage:.2f}%"])
    y_position = draw_table_on_canvas(c, table_data, margin, y_position, width, height, margin)

    # --- Character-Wise Frequency Table ---
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y_position, "Character-Wise Frequency Distribution")
    y_position -= 20
    char_data = []
    total_characters = sum(font_character_frequency.values())
    for font, freq in font_character_frequency.items():
        percentage = (freq / total_characters) * 100 if total_characters else 0
        char_data.append((font, freq, percentage))
    char_data_sorted = sorted(char_data, key=lambda x: x[2], reverse=True)
    table_data = [["Font Name", "Frequency", "Percentage"]]
    for font, freq, percentage in char_data_sorted:
        table_data.append([font, freq, f"{percentage:.2f}%"])
    y_position = draw_table_on_canvas(c, table_data, margin, y_position, width, height, margin)

    # --- Font Size Distribution Table for each font ---
    for font, size_counter in font_size_data.items():
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin, y_position, f"Font Size Distribution for {font}")
        y_position -= 20
        data = [["Font Size", "Frequency", "Percentage"]]
        total_size = sum(size_counter.values())
        size_data = []
        for size, freq in size_counter.items():
            percentage = (freq / total_size) * 100 if total_size else 0
            size_data.append((size, freq, percentage))
        size_data_sorted = sorted(size_data, key=lambda x: x[2], reverse=True)
        for size, freq, percentage in size_data_sorted:
            data.append([size, freq, f"{percentage:.2f}%"])
        y_position = draw_table_on_canvas(c, data, margin, y_position, width, height, margin)
        y_position -= 10
        if y_position < 150:
            c.showPage()
            y_position = height - margin

    # Save charts as images and add to PDF
    temp_files = []
    for fig_num in plt.get_fignums():
        temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        plt.figure(fig_num).savefig(temp_file.name, format="png")
        temp_files.append(temp_file.name)

    for temp_file in temp_files:
        with Image.open(temp_file) as img:
            img_width, img_height = img.size
            aspect_ratio = img_width / img_height
            display_width = width - 2 * margin
            display_height = display_width / aspect_ratio
            if y_position - display_height < margin:
                c.showPage()
                y_position = height - margin
            c.drawImage(temp_file, margin, y_position - display_height, width=display_width, height=display_height)
            y_position -= display_height + 20

    c.save()
    for temp_file in temp_files:
        os.remove(temp_file)

def draw_table_on_canvas(c, data, x, y, page_width, page_height, margin):
    table = Table(data, colWidths=[120, 80, 80])
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ])
    table.setStyle(style)
    w, h = table.wrapOn(c, page_width - 2 * margin, page_height)
    # If not enough space, start a new page
    if y - h < margin:
        c.showPage()
        y = page_height - margin
    table.drawOn(c, x, y - h)
    return y - h - 20  # Return new y position
# Function to process font data
def populate_table(tab, columns, data):
    # Clear existing widgets in the tab
    for widget in tab.winfo_children():
        widget.destroy()

    # Create a Treeview widget
    tree = ttk.Treeview(tab, columns=columns, show="headings", height=20)
    tree.pack(fill=tk.BOTH, expand=True)

    # Define column headings
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=150)

    # Insert data into the table
    for row in data:
        tree.insert("", tk.END, values=row)

    # Add a scrollbar
    scrollbar = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)



def process_fonts(report):
    unique_text_styles = report["unique_text_styles"]
    sorted_text_style_frequency = report["sorted_text_style_frequency"]

    font_style_frequency = Counter()
    font_character_frequency = Counter()
    font_size_data = {}

    for style_key, style in unique_text_styles.items():
        fontname = style["fontname"]
        size = style["size"]
        style_frequency = sorted_text_style_frequency.get(style_key, 0)

        # Update style frequency
        font_style_frequency[fontname] += 1

        # Update character frequency
        font_character_frequency[fontname] += style_frequency

        # Update font size data
        if fontname not in font_size_data:
            font_size_data[fontname] = Counter()
        font_size_data[fontname][size] += style_frequency

    return font_style_frequency, font_character_frequency, font_size_data

# Function to generate bar graph
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

    # Add frequency numbers on top of the bars
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,  # X-coordinate (center of the bar)
            height,  # Y-coordinate (top of the bar)
            f"{int(height)}",  # Text to display (convert to integer)
            ha="center",  # Horizontal alignment
            va="bottom",  # Vertical alignment
            fontsize=10,  # Font size
            color="black"  # Text color
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

def populate_table(tab, columns, data):
    # Clear existing widgets in the tab
    for widget in tab.winfo_children():
        widget.destroy()

    # Create a Treeview widget
    tree = ttk.Treeview(tab, columns=columns, show="headings", height=20)
    tree.pack(fill=tk.BOTH, expand=True)

    # Define column headings
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=150)

    # Insert data into the table
    for row in data:
        tree.insert("", tk.END, values=row)

    # Add a scrollbar
    scrollbar = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Function to generate horizontal bar graph for font sizes
def generate_horizontal_bar_graph(data, title, x_label, y_label):
    fig, ax = plt.subplots(figsize=(8, 6))
    keys = list(data.keys())
    values = [int(value) for value in data.values()]  # Ensure values are integers

    ax.set_yticks(keys)  # Set Y-axis ticks to show only the sizes
    ax.set_yticklabels(keys)  # Ensure the Y-axis labels match the sizes

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

# Function to display graphs in the UI
def display_graph(tab, fig):
    for widget in tab.winfo_children():
        widget.destroy()

    canvas = FigureCanvasTkAgg(fig, master=tab)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# Function to handle font selection from the dropdown
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
        display_graph(horizontal_graph_tab, font_size_graph)

        # Display the pie chart in the pie_chart_tab
        display_graph(pie_chart_tab, font_size_pie_chart)
        size_data = []
        total_size_characters = sum(font_size_data[selected_font].values())
        font_size_data_sorted = sorted(
            font_size_data[selected_font].items(),
            key=lambda x: (x[1] / total_size_characters) * 100,
            reverse=True
        )
        for size, freq in font_size_data_sorted:
            percentage = (freq / total_size_characters) * 100
            size_data.append((size, freq, f"{percentage:.2f}%"))
        populate_table(font_size_distribution_tab, ["Font Size", "Frequency", "Percentage"], size_data)
    else:
        # Clear the tabs if no data is available for the selected font
        for widget in horizontal_graph_tab.winfo_children():
            widget.destroy()
        tk.Label(horizontal_graph_tab, text="No data available for the selected font.").pack()

        for widget in pie_chart_tab.winfo_children():
            widget.destroy()
        tk.Label(pie_chart_tab, text="No data available for the selected font.").pack()
        populate_table(font_size_distribution_tab, ["Font Size", "Frequency", "Percentage"], [])


def load_json():
    global font_style_frequency, font_character_frequency, font_size_data

    json_file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if json_file_path:
        with open(json_file_path, "r") as json_file:
            report = json.load(json_file)

        # Process the JSON data
        font_style_frequency, font_character_frequency, font_size_data = process_fonts(report)

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
        on_font_select(None)  # Display the graph for the first font by default

        # Populate Style-Wise Frequency Table
        style_data = []
        total_styles = sum(font_style_frequency.values())
        for font, freq in font_style_frequency.items():
            percentage = (freq / total_styles) * 100
            style_data.append((font, freq, f"{percentage:.2f}%"))
        style_data_sorted = sorted(style_data, key=lambda x: float(x[2][:-1]), reverse=True)
        populate_table(style_frequency_tab, ["Font Name", "Frequency", "Percentage"], style_data_sorted)

        # Populate Character-Wise Frequency Table
        char_data = []
        total_characters = sum(font_character_frequency.values())
        for font, freq in font_character_frequency.items():
            percentage = (freq / total_characters) * 100
            char_data.append((font, freq, f"{percentage:.2f}%"))
        char_data_sorted = sorted(char_data, key=lambda x: float(x[2][:-1]), reverse=True)
        populate_table(character_frequency_tab, ["Font Name", "Frequency", "Percentage"], char_data_sorted)
        generate_pdf_report(font_style_frequency, font_character_frequency, font_size_data)
        # Populate Font Size Distribution Table
        # if font_dropdown["values"]:
        #     first_font = font_dropdown["values"][0]
        #     font_size_data_sorted = sorted(
        #         font_size_data[first_font].items(),
        #         key=lambda x: (x[1] / sum(font_size_data[first_font].values())) * 100,
        #         reverse=True
        #     )
        #     size_data = []
        #     total_size_characters = sum(font_size_data[first_font].values())
        #     for size, freq in font_size_data_sorted:
        #         percentage = (freq / total_size_characters) * 100
        #         size_data.append((size, freq, f"{percentage:.2f}%"))
        #     populate_table(font_size_distribution_tab, ["Font Size", "Frequency", "Percentage"], size_data)


root = tk.Tk()
root.title("JSON Font Analysis Tool")
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
notebook.pack(fill=tk.X, expand=False, pady=5)

# Create tabs
tab1 = ttk.Frame(notebook)
tab2 = ttk.Frame(notebook)
tab3 = ttk.Frame(notebook)
tab4 = ttk.Frame(notebook)

notebook.add(tab1, text="Style-Wise Bar Graph")
notebook.add(tab2, text="Style-Wise Pie Chart")
notebook.add(tab3, text="Character-Wise Bar Graph")
notebook.add(tab4, text="Character-Wise Pie Chart")

style_frequency_tab = ttk.Frame(notebook)
character_frequency_tab = ttk.Frame(notebook)
font_size_distribution_tab = ttk.Frame(notebook)

notebook.add(style_frequency_tab, text="Style-Wise Frequency Table")
notebook.add(character_frequency_tab, text="Character-Wise Frequency Table")
notebook.add(font_size_distribution_tab, text="Font Size Distribution Table")

# Add Load JSON button
load_button = tk.Button(scrollable_frame, text="Load JSON", command=load_json)
load_button.pack(pady=10)

# Add font dropdown
font_dropdown_label = tk.Label(scrollable_frame, text="Select Font:")
font_dropdown_label.pack(pady=5)

font_dropdown = ttk.Combobox(scrollable_frame)
font_dropdown.pack(pady=5)
font_dropdown.bind("<<ComboboxSelected>>", on_font_select)

# Create a Notebook widget for the pie chart and horizontal graph
font_analysis_notebook = ttk.Notebook(scrollable_frame)
font_analysis_notebook.pack(fill=tk.BOTH, expand=True, pady=10)

# Create tabs for the pie chart and horizontal graph
pie_chart_tab = ttk.Frame(font_analysis_notebook)
horizontal_graph_tab = ttk.Frame(font_analysis_notebook)

font_analysis_notebook.add(pie_chart_tab, text="Font Size Pie Chart")
font_analysis_notebook.add(horizontal_graph_tab, text="Font Size Horizontal Graph")

# Start the main loop
root.mainloop()