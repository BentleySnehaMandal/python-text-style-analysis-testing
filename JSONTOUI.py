import json
import os
import tkinter as tk
from tkinter import ttk, Canvas, Frame
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from PIL import Image
import tempfile
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from wordcloud import WordCloud
from collections import Counter
import numpy as np
import re

def filter_word(word):
    # Exclude numbers and single characters (keep only words with at least 2 letters and not all digits)
    return len(word) > 1 and not word.isdigit() and re.match(r'^[A-Za-z]+$', word)

# C:\Users\Sneha.Mandal\python-test-folder\newBredan_pdf_data.json
# Load JSON data
def load_json_data():
    try:
        with open("newBredan_pdf_data.json", "r") as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        tk.messagebox.showerror("Error", "JSON file not found. Please ensure 'newBredan_pdf_data.json' exists.")
        return []

# Global variable to store loaded data
pdf_data = load_json_data()

# Function to display cumulative analysis
def display_cumulative_analysis():
    if not pdf_data:
        tk.messagebox.showerror("Error", "No data available. Please ensure the JSON file is loaded.")
        return

    # Create a new window for cumulative analysis
    cumulative_window = tk.Toplevel(root)
    cumulative_window.title("Cumulative Analysis")

    # Create a scrollable frame
    canvas_widget = Canvas(cumulative_window)
    scrollable_frame = Frame(canvas_widget)
    scrollbar = ttk.Scrollbar(cumulative_window, orient="vertical", command=canvas_widget.yview)
    canvas_widget.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    canvas_widget.pack(side="left", fill="both", expand=True)
    canvas_widget.create_window((0, 0), window=scrollable_frame, anchor="nw")

    # Configure the scrollable frame to resize properly
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas_widget.configure(scrollregion=canvas_widget.bbox("all"))
    )

    # Table for PDF summary
    columns = ["PDF Name", "No. of Images", "No. of Words", "Height", "Width", "No. of Pages"]
    tree = ttk.Treeview(scrollable_frame, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=150)

    for pdf in pdf_data:
        tree.insert("", "end", values=(
            pdf["pdf_name"], pdf["image_no"], pdf["word_count"],
            pdf["height"], pdf["width"], pdf["pages_total"]
        ))

    tree.pack(fill="both", expand=True, pady=10)

    # Tabs for graphs and tables
    notebook = ttk.Notebook(scrollable_frame)

    # Tab 1: Frequency of Dimensions
    dimension_tab = tk.Frame(notebook)
    notebook.add(dimension_tab, text="Dimension Frequency")
    plot_dimension_frequency(dimension_tab)

    # Tab 2: Frequency of Word Counts
    word_count_tab = tk.Frame(notebook)
    notebook.add(word_count_tab, text="Word Count Frequency")
    plot_word_count_frequency(word_count_tab)

    # Tab 3: Frequency of Image Counts
    image_count_tab = tk.Frame(notebook)
    notebook.add(image_count_tab, text="Image Count Frequency")
    plot_image_count_frequency(image_count_tab)

    # Tab 4: Frequency of Page Counts
    page_count_tab = tk.Frame(notebook)
    notebook.add(page_count_tab, text="Page Count Frequency")
    plot_page_count_frequency(page_count_tab)

    # Tab 5: Word Frequency (Word Cloud and Table)
    word_frequency_tab = tk.Frame(notebook)
    notebook.add(word_frequency_tab, text="Word Frequency")
    plot_word_frequency(word_frequency_tab)

    notebook.pack(fill="both", expand=True, pady=10)

    # Add a button to download the report as a PDF
    download_button = tk.Button(scrollable_frame, text="Download Report", command=download_report)
    download_button.pack(pady=10)

     # Tab 6: Words per Page Frequency
    words_per_page_tab = tk.Frame(notebook)
    notebook.add(words_per_page_tab, text="Words per Page Frequency")
    plot_words_per_page_frequency(words_per_page_tab)

    # Tab 7: Images per Page Frequency
    images_per_page_tab = tk.Frame(notebook)
    notebook.add(images_per_page_tab, text="Images per Page Frequency")
    plot_images_per_page_frequency(images_per_page_tab)


def download_report():
    pdf_file = "JSONnew_Cumulativeeee_Analysis_Report.pdf"
    c = canvas.Canvas(pdf_file, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Cumulative Analysis Report")
    y_position = height - 100

    # PDF summary table
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y_position, "Table: PDF Summary")
    y_position -= 20
    c.setFont("Helvetica", 10)
    c.drawString(50, y_position, "PDF Name | No. of Images | No. of Words | Height | Width | No. of Pages")
    y_position -= 20
    for pdf in pdf_data:
        c.drawString(
            50,
            y_position,
            f"{pdf['pdf_name']} | {pdf['image_no']} | {pdf['word_count']} | {pdf['height']} | {pdf['width']} | {pdf['pages_total']}",
        )
        y_position -= 20
        if y_position < 50:
            c.showPage()
            y_position = height - 50

   # Frequency of Page Count (with dynamic bin size)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y_position, "Table: Frequency of Page Count")
    y_position -= 20
    page_counts = [pdf["pages_total"] for pdf in pdf_data]
    bin_size = get_dynamic_bin_size(page_counts)
    bins = np.arange(min(page_counts), max(page_counts) + bin_size, bin_size)
    if page_counts and max(page_counts) >= bins[-1]:
        bins = np.append(bins, bins[-1] + bin_size)
    total_pdfs = len(pdf_data)
    percentages = [(np.sum((np.array(page_counts) >= bins[i]) & (np.array(page_counts) < bins[i + 1])) / total_pdfs) * 100 for i in range(len(bins) - 1)]
    ranges = [f"{int(bins[i])}-{int(bins[i + 1])}" for i in range(len(bins) - 1)]
    for r, p in zip(ranges, percentages):
        c.drawString(50, y_position, f"{r}: {p:.2f}%")
        y_position -= 20
        if y_position < 50:
            c.showPage()
            y_position = height - 50
    # Frequency of Word Count
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y_position, "Table: Frequency of Word Count")
    y_position -= 20
    word_counts = [pdf["word_count"] for pdf in pdf_data]
    bins = np.arange(min(word_counts), max(word_counts) + 1000, 1000)
    if word_counts and max(word_counts) >= bins[-1]:
        bins = np.append(bins, bins[-1] + (bins[1] - bins[0]))
    percentages = [(np.sum((word_counts >= bins[i]) & (word_counts < bins[i + 1])) / total_pdfs) * 100 for i in range(len(bins) - 1)]
    ranges = [f"{int(bins[i])}-{int(bins[i + 1])}" for i in range(len(bins) - 1)]
    for r, p in zip(ranges, percentages):
        c.drawString(50, y_position, f"{r}: {p:.2f}%")
        y_position -= 20
        if y_position < 50:
            c.showPage()
            y_position = height - 50

    # Frequency of Image Count
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y_position, "Table: Frequency of Image Count")
    y_position -= 20
    image_counts = [pdf["image_no"] for pdf in pdf_data]
    bins = np.arange(min(image_counts), max(image_counts) + 50, 50)
    if image_counts and max(image_counts) >= bins[-1]:
        bins = np.append(bins, bins[-1] + (bins[1] - bins[0]))
    percentages = [(np.sum((image_counts >= bins[i]) & (image_counts < bins[i + 1])) / total_pdfs) * 100 for i in range(len(bins) - 1)]
    ranges = [f"{int(bins[i])}-{int(bins[i + 1])}" for i in range(len(bins) - 1)]
    for r, p in zip(ranges, percentages):
        c.drawString(50, y_position, f"{r}: {p:.2f}%")
        y_position -= 20
        if y_position < 50:
            c.showPage()
            y_position = height - 50

        # Words per Page Frequency
        # Words per Page Frequency
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y_position, "Table: Words per Page Frequency")
    y_position -= 20
    all_word_counts = []
    for pdf in pdf_data:
        all_word_counts.extend([page["word_count"] for page in pdf["page_data"]])
    if all_word_counts:
        bin_size = 50  # Set bucket size to 50
        bins = np.arange(min(all_word_counts), max(all_word_counts) + bin_size, bin_size)
        if max(all_word_counts) >= bins[-1]:
            bins = np.append(bins, bins[-1] + bin_size)
        total_pages = len(all_word_counts)
        percentages = [(np.sum((np.array(all_word_counts) >= bins[i]) & (np.array(all_word_counts) < bins[i + 1])) / total_pages) * 100 for i in range(len(bins) - 1)]
        ranges = [f"{int(bins[i])}-{int(bins[i + 1])}" for i in range(len(bins) - 1)]
        for r, p in zip(ranges, percentages):
            c.drawString(50, y_position, f"{r}: {p:.2f}%")
            y_position -= 20
            if y_position < 50:
                c.showPage()
                y_position = height - 50



    # Images per Page Frequency
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y_position, "Table: Images per Page Frequency")
    y_position -= 20
    all_image_counts = []
    for pdf in pdf_data:
        all_image_counts.extend([page["image_count"] for page in pdf["page_data"]])
    if all_image_counts:
        bin_size = get_dynamic_bin_size(all_image_counts)
        bins = np.arange(min(all_image_counts), max(all_image_counts) + bin_size, bin_size)
        if max(all_image_counts) >= bins[-1]:
            bins = np.append(bins, bins[-1] + bin_size)
        total_pages = len(all_image_counts)
        percentages = [(np.sum((np.array(all_image_counts) >= bins[i]) & (np.array(all_image_counts) < bins[i + 1])) / total_pages) * 100 for i in range(len(bins) - 1)]
        ranges = [f"{int(bins[i])}-{int(bins[i + 1])}" for i in range(len(bins) - 1)]
        for r, p in zip(ranges, percentages):
            c.drawString(50, y_position, f"{r}: {p:.2f}%")
            y_position -= 20
            if y_position < 50:
                c.showPage()
                y_position = height - 50

   
# Frequency of Words (filtered)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y_position, "Table: Frequency of Words (Excluding Numbers & Single Characters)")
    y_position -= 20
    word_counter = Counter()
    for pdf in pdf_data:
        filtered_words = [w for w in pdf["word_list"] if filter_word(w)]
        word_counter.update(filtered_words)
    most_common_words = word_counter.most_common(20)
    for word, freq in most_common_words:
        c.drawString(50, y_position, f"{word}: {freq}")
        y_position -= 20
        if y_position < 50:
            c.showPage()
            y_position = height - 50

    # Save graphs as temporary image files and add them to the PDF
    temp_files = []
    for i, fig in enumerate(plt.get_fignums()):
        temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        plt.figure(fig).savefig(temp_file.name, format="png")
        temp_files.append(temp_file.name)

    # Add graphs to the PDF
    for temp_file in temp_files:
        with Image.open(temp_file) as img:
            img_width, img_height = img.size
            aspect_ratio = img_width / img_height
            img_width = width - 100
            img_height = img_width / aspect_ratio
            if y_position - img_height < 50:
                c.showPage()
                y_position = height - 50
            c.drawImage(temp_file, 50, y_position - img_height, width=img_width, height=img_height)
            y_position -= img_height + 20

    c.save()
    for temp_file in temp_files:
        os.remove(temp_file)

    tk.messagebox.showinfo("Success", f"Report saved as {pdf_file}")

# Function to display individual PDF analysis
def display_individual_analysis(pdf_name):
    selected_pdf = next((pdf for pdf in pdf_data if pdf["pdf_name"] == pdf_name), None)
    if not selected_pdf:
        tk.messagebox.showerror("Error", "No data available for the selected PDF.")
        return

    # Create a new window for individual analysis
    individual_window = tk.Toplevel(root)
    individual_window.title(f"Analysis for {pdf_name}")

    # Table for page-level data
    columns = ["Page No", "Word Count", "Image Count"]
    tree = ttk.Treeview(individual_window, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=150)

    for page in selected_pdf["page_data"]:
        tree.insert("", "end", values=(page["page_number"], page["word_count"], page["image_count"]))

    tree.pack(fill="both", expand=True)

    # Tabs for graphs and tables
    notebook = ttk.Notebook(individual_window)

    # Tab 1: Word Count Frequency
    word_count_tab = tk.Frame(notebook)
    notebook.add(word_count_tab, text="Word Count Frequency")
    plot_page_word_count_frequency(selected_pdf, word_count_tab)

    # Tab 2: Image Count Frequency
    image_count_tab = tk.Frame(notebook)
    notebook.add(image_count_tab, text="Image Count Frequency")
    plot_page_image_count_frequency(selected_pdf, image_count_tab)

    # Tab 3: Word Cloud
    word_cloud_tab = tk.Frame(notebook)
    notebook.add(word_cloud_tab, text="Word Cloud")
    plot_word_cloud(selected_pdf, word_cloud_tab)

    notebook.pack(fill="both", expand=True)

# Function to plot dimension frequency as a histogram
def plot_dimension_frequency(parent):
    dimensions = [(pdf["height"], pdf["width"]) for pdf in pdf_data]
    dimension_labels = [f"{dim[0]}x{dim[1]}" for dim in dimensions]
    unique_dimensions, counts = np.unique(dimension_labels, return_counts=True)

    # Plot histogram
    fig, ax = plt.subplots()
    ax.bar(unique_dimensions, counts)
    ax.set_title("Frequency of Dimensions")
    ax.set_xlabel("Dimensions (Height x Width)")
    ax.set_ylabel("Frequency")
    plt.xticks(rotation=45)

    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.get_tk_widget().pack()
    canvas.draw()

    # Add table for dimension frequency
    add_dimension_table(parent, unique_dimensions, counts)

# Function to add a table for dimension frequency
def add_dimension_table(parent, dimensions, counts):
    # Create a table
    table_frame = tk.Frame(parent)
    table_frame.pack(fill="both", expand=True)

    table = ttk.Treeview(table_frame, columns=["Dimension", "Frequency"], show="headings")
    table.heading("Dimension", text="Dimension (Height x Width)")
    table.heading("Frequency", text="Frequency")

    for dim, count in zip(dimensions, counts):
        table.insert("", "end", values=(dim, count))

    table.pack(fill="both", expand=True)


def get_dynamic_bin_size(data, min_bins=5, max_bins=15):
    """Choose a bin size so that the number of bins is between min_bins and max_bins."""
    data_min, data_max = min(data), max(data)
    data_range = data_max - data_min
    if data_range == 0:
        return 1
    # Try to get bins between min_bins and max_bins
    for step in [1, 2, 5, 10, 20, 50, 100]:
        bins = int(data_range / step) + 1
        if min_bins <= bins <= max_bins:
            return step
    # Fallback: just use 10 bins
    return max(1, int(data_range / 10))

def plot_words_per_page_frequency(parent):
    all_word_counts = []
    for pdf in pdf_data:
        all_word_counts.extend([page["word_count"] for page in pdf["page_data"]])
    if not all_word_counts:
        return
    # bin_size = get_dynamic_bin_size(all_word_counts)
    bin_size = 50 # Fixed bin size for simplicity, can be adjusted
    bins = np.arange(min(all_word_counts), max(all_word_counts) + bin_size, bin_size)
    if max(all_word_counts) >= bins[-1]:
        bins = np.append(bins, bins[-1] + bin_size)

    fig, ax = plt.subplots()
    ax.hist(all_word_counts, bins=bins, edgecolor="black")
    ax.set_title("Words per Page Frequency")
    ax.set_xlabel("Words per Page")
    ax.set_ylabel("Frequency")
    plt.xticks(rotation=45)

    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.get_tk_widget().pack()
    canvas.draw()

    total_pages = len(all_word_counts)
    percentages = [(np.sum((np.array(all_word_counts) >= bins[i]) & (np.array(all_word_counts) < bins[i + 1])) / total_pages) * 100 for i in range(len(bins) - 1)]
    ranges = [f"{int(bins[i])}-{int(bins[i + 1])}" for i in range(len(bins) - 1)]

    table_frame = tk.Frame(parent)
    table_frame.pack(fill="both", expand=True)
    table = ttk.Treeview(table_frame, columns=["Range", "Percentage"], show="headings")
    table.heading("Range", text="Words/Page Range")
    table.heading("Percentage", text="Percentage (%)")
    for r, p in zip(ranges, percentages):
        table.insert("", "end", values=(r, f"{p:.2f}%"))
    table.pack(fill="both", expand=True)

def plot_images_per_page_frequency(parent):
    all_image_counts = []
    for pdf in pdf_data:
        all_image_counts.extend([page["image_count"] for page in pdf["page_data"]])
    if not all_image_counts:
        return
    bin_size = get_dynamic_bin_size(all_image_counts)
    bins = np.arange(min(all_image_counts), max(all_image_counts) + bin_size, bin_size)
    if max(all_image_counts) >= bins[-1]:
        bins = np.append(bins, bins[-1] + bin_size)

    fig, ax = plt.subplots()
    ax.hist(all_image_counts, bins=bins, edgecolor="black")
    ax.set_title("Images per Page Frequency")
    ax.set_xlabel("Images per Page")
    ax.set_ylabel("Frequency")
    plt.xticks(rotation=45)

    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.get_tk_widget().pack()
    canvas.draw()

    total_pages = len(all_image_counts)
    percentages = [(np.sum((np.array(all_image_counts) >= bins[i]) & (np.array(all_image_counts) < bins[i + 1])) / total_pages) * 100 for i in range(len(bins) - 1)]
    ranges = [f"{int(bins[i])}-{int(bins[i + 1])}" for i in range(len(bins) - 1)]

    table_frame = tk.Frame(parent)
    table_frame.pack(fill="both", expand=True)
    table = ttk.Treeview(table_frame, columns=["Range", "Percentage"], show="headings")
    table.heading("Range", text="Images/Page Range")
    table.heading("Percentage", text="Percentage (%)")
    for r, p in zip(ranges, percentages):
        table.insert("", "end", values=(r, f"{p:.2f}%"))
    table.pack(fill="both", expand=True)




# Function to plot word count frequency as a histogram
def plot_word_count_frequency(parent):
    word_counts = [pdf["word_count"] for pdf in pdf_data]
    bins = np.arange(min(word_counts), max(word_counts) + 1000, 1000)  # Adjust bucket size dynamically

    # Plot histogram
    fig, ax = plt.subplots()
    ax.hist(word_counts, bins=bins, edgecolor="black")
    ax.set_title("Frequency of Word Counts")
    ax.set_xlabel("Word Count")
    ax.set_ylabel("Frequency")

    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.get_tk_widget().pack()
    canvas.draw()

    # Add table for percentages
    add_percentage_table(parent, word_counts, bins, "Word Count")

# Function to add percentage table
def add_percentage_table(parent, data, bins, label):
    total_pdfs = len(pdf_data)  # Correctly calculate percentages based on the number of PDFs

    # Ensure the maximum value is included in the last bucket
    if data and max(data) >= bins[-1]:
        bins = np.append(bins, bins[-1] + (bins[1] - bins[0]))

    percentages = [(np.sum((data >= bins[i]) & (data < bins[i + 1])) / total_pdfs) * 100 for i in range(len(bins) - 1)]
    ranges = [f"{int(bins[i])}-{int(bins[i + 1])}" for i in range(len(bins) - 1)]

    # Create a table
    table_frame = tk.Frame(parent)
    table_frame.pack(fill="both", expand=True)

    table = ttk.Treeview(table_frame, columns=["Range", "Percentage"], show="headings")
    table.heading("Range", text=f"{label} Range")
    table.heading("Percentage", text="Percentage (%)")

    for r, p in zip(ranges, percentages):
        table.insert("", "end", values=(r, f"{p:.2f}%"))

    table.pack(fill="both", expand=True)

# Function to plot image count frequency as a histogram
def plot_image_count_frequency(parent):
    image_counts = [pdf["image_no"] for pdf in pdf_data]
    bins = np.arange(min(image_counts), max(image_counts) + 50, 50)  # Adjust bucket size dynamically

    # Plot histogram
    fig, ax = plt.subplots()
    ax.hist(image_counts, bins=bins, edgecolor="black")
    ax.set_title("Frequency of Image Counts")
    ax.set_xlabel("Image Count")
    ax.set_ylabel("Frequency")

    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.get_tk_widget().pack()
    canvas.draw()

    # Add table for percentages
    add_percentage_table(parent, image_counts, bins, "Image Count")

# Function to plot page count frequency as a histogram
def plot_page_count_frequency(parent):
    page_counts = [pdf["pages_total"] for pdf in pdf_data]
    bin_size = get_dynamic_bin_size(page_counts)
    bins = np.arange(min(page_counts), max(page_counts) + bin_size, bin_size)

    # Plot histogram
    fig, ax = plt.subplots()
    ax.hist(page_counts, bins=bins, edgecolor="black")
    ax.set_title("Frequency of Page Counts")
    ax.set_xlabel("Page Count")
    ax.set_ylabel("Frequency")

    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.get_tk_widget().pack()
    canvas.draw()

    # Add table for percentages
    add_percentage_table(parent, page_counts, bins, "Page Count")

# Function to plot word frequency
def plot_word_frequency(parent):
    word_counter = Counter()
    for pdf in pdf_data:
        filtered_words = [w for w in pdf["word_list"] if filter_word(w)]
        word_counter.update(filtered_words)
    most_common_words = word_counter.most_common(20)

    # Bar chart
    words, freqs = zip(*most_common_words) if most_common_words else ([], [])
    fig, ax = plt.subplots()
    ax.bar(words, freqs)
    ax.set_title("Top 20 Most Common Words")
    ax.set_xlabel("Word")
    ax.set_ylabel("Frequency")
    plt.xticks(rotation=45)
    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.get_tk_widget().pack()
    canvas.draw()

    # Table
    table_frame = tk.Frame(parent)
    table_frame.pack(fill="both", expand=True)
    table = ttk.Treeview(table_frame, columns=["Word", "Frequency"], show="headings")
    table.heading("Word", text="Word")
    table.heading("Frequency", text="Frequency")
    for word, freq in most_common_words:
        table.insert("", "end", values=(word, freq))
    table.pack(fill="both", expand=True)

# Function to add a table for most common words
def add_word_frequency_table(parent, word_frequencies):
    # Create a table
    table_frame = tk.Frame(parent)
    table_frame.pack(fill="both", expand=True)

    table = ttk.Treeview(table_frame, columns=["Word", "Frequency"], show="headings")
    table.heading("Word", text="Word")
    table.heading("Frequency", text="Frequency")

    for word, freq in word_frequencies:
        table.insert("", "end", values=(word, freq))

    table.pack(fill="both", expand=True)

# Function to plot word count frequency for a single PDF
def plot_page_word_count_frequency(pdf, parent):
    word_counts = [page["word_count"] for page in pdf["page_data"]]
    bins = np.linspace(min(word_counts), max(word_counts), 10)  # Create 10 bins

    fig, ax = plt.subplots()
    ax.hist(word_counts, bins=bins, edgecolor="black")
    ax.set_title("Frequency of Word Counts (Pages)")
    ax.set_xlabel("Word Count")
    ax.set_ylabel("Frequency")

    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.get_tk_widget().pack()
    canvas.draw()

    # Add table for percentages
    add_percentage_table(parent, word_counts, bins, "Word Count")

# Function to plot image count frequency for a single PDF
def plot_page_image_count_frequency(pdf, parent):
    image_counts = [page["image_count"] for page in pdf["page_data"]]
    bins = np.linspace(min(image_counts), max(image_counts), 10)  # Create 10 bins

    fig, ax = plt.subplots()
    ax.hist(image_counts, bins=bins, edgecolor="black")
    ax.set_title("Frequency of Image Counts (Pages)")
    ax.set_xlabel("Image Count")
    ax.set_ylabel("Frequency")

    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.get_tk_widget().pack()
    canvas.draw()

    # Add table for percentages
    add_percentage_table(parent, image_counts, bins, "Image Count")

# Function to plot word cloud for a single PDF
def plot_word_cloud(pdf, parent):
    word_cloud = WordCloud(width=800, height=400, background_color="white").generate(" ".join(pdf["word_list"]))

    fig, ax = plt.subplots()
    ax.imshow(word_cloud, interpolation="bilinear")
    ax.axis("off")
    ax.set_title("Word Cloud")

    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.get_tk_widget().pack()
    canvas.draw()

# Create the main UI
root = tk.Tk()
root.title("PDF Data Analyzer (JSON Mode)")

# Cumulative Analysis Section
tk.Button(root, text="Cumulative Analysis", command=display_cumulative_analysis).pack(pady=10)

# Individual Analysis Section
tk.Label(root, text="Select a PDF for Individual Analysis:").pack(pady=10)
selected_pdf_name = tk.StringVar()
pdf_dropdown = ttk.Combobox(root, textvariable=selected_pdf_name, state="readonly")
pdf_dropdown["values"] = [pdf["pdf_name"] for pdf in pdf_data]
pdf_dropdown.pack(pady=10)
tk.Button(root, text="Analyze PDF", command=lambda: display_individual_analysis(selected_pdf_name.get())).pack(pady=10)

root.mainloop()