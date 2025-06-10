import os
import json
import tkinter as tk
from tkinter import filedialog, ttk
import pdfplumber
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from wordcloud import WordCloud
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import numpy as np
import nltk

# Download NLTK resources
nltk.download('stopwords')
nltk.download('punkt')

# Global variables
pdf_data = []  # List to store data for all PDFs
stop_words = set(stopwords.words("english"))

# Function to extract data from a single PDF
def extract_pdf_data(pdf_path):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            num_pages = len(pdf.pages)
            width, height = round((pdf.pages[0].width)/72),round( (pdf.pages[0].height)/72)
            total_words = 0
            word_frequency = Counter()
            image_count = 0
            page_data = []

            for page_number, page in enumerate(pdf.pages, start=1):
                # Count words
                text = page.extract_text()
                word_count = 0
                if text:
                    words = word_tokenize(text.lower())
                    filtered_words = [word for word in words if word.isalnum() and word not in stop_words]
                    word_count = len(filtered_words)
                    total_words += word_count
                    word_frequency.update(filtered_words)

                # Count images
                images_on_page = len(page.images)
                image_count += images_on_page

                # Store page-level data
                page_data.append({
                    "page_number": page_number,
                    "word_count": word_count,
                    "image_count": images_on_page
                })

            return {
                "pdf_name": os.path.basename(pdf_path),
                "height": round(height),
                "width": round(width),
                "pages_total": num_pages,
                "image_no": image_count,
                "word_count": total_words,
                "word_list": list(word_frequency.keys()),
                "page_data": page_data
            }
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return None

# Function to process all PDFs in a folder
def process_folder(folder_path):
    global pdf_data
    pdf_data = []  # Reset data
    for file_name in os.listdir(folder_path):
        if file_name.lower().endswith(".pdf"):
            pdf_path = os.path.join(folder_path, file_name)
            pdf_info = extract_pdf_data(pdf_path)
            if pdf_info:
                pdf_data.append(pdf_info)

    # Save data to JSON
    with open("pdf_data.json", "w") as json_file:
        json.dump(pdf_data, json_file, indent=4)
    print("PDF data saved to pdf_data.json")

# Function to display cumulative analysis
def display_cumulative_analysis():
    if not pdf_data:
        tk.messagebox.showerror("Error", "No data available. Please process a folder first.")
        return

    # Create a new window for cumulative analysis
    cumulative_window = tk.Toplevel(root)
    cumulative_window.title("Cumulative Analysis")

    # Table for PDF summary
    columns = ["PDF Name", "No. of Images", "No. of Words", "Height", "Width", "No. of Pages"]
    tree = ttk.Treeview(cumulative_window, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=150)

    for pdf in pdf_data:
        tree.insert("", "end", values=(
            pdf["pdf_name"], pdf["image_no"], pdf["word_count"],
            pdf["height"], pdf["width"], pdf["pages_total"]
        ))

    tree.pack(fill="both", expand=True)

    # Tabs for graphs
    notebook = ttk.Notebook(cumulative_window)

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

    # Tab 5: Word Frequency
    word_frequency_tab = tk.Frame(notebook)
    notebook.add(word_frequency_tab, text="Word Frequency")
    plot_word_frequency(word_frequency_tab)

    notebook.pack(fill="both", expand=True)

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

    # Tabs for graphs
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

    fig, ax = plt.subplots()
    ax.bar(unique_dimensions, counts)
    ax.set_title("Frequency of Dimensions")
    ax.set_xlabel("Dimensions (Height x Width)")
    ax.set_ylabel("Frequency")
    plt.xticks(rotation=45)

    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.get_tk_widget().pack()
    canvas.draw()

# Function to plot word count frequency as a histogram
def plot_word_count_frequency(parent):
    word_counts = [pdf["word_count"] for pdf in pdf_data]
    bins = np.linspace(min(word_counts), max(word_counts), 10)  # Create 10 bins

    fig, ax = plt.subplots()
    ax.hist(word_counts, bins=bins, edgecolor="black")
    ax.set_title("Frequency of Word Counts")
    ax.set_xlabel("Word Count")
    ax.set_ylabel("Frequency")

    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.get_tk_widget().pack()
    canvas.draw()

# Function to plot image count frequency as a histogram
def plot_image_count_frequency(parent):
    image_counts = [pdf["image_no"] for pdf in pdf_data]
    bins = np.linspace(min(image_counts), max(image_counts), 10)  # Create 10 bins

    fig, ax = plt.subplots()
    ax.hist(image_counts, bins=bins, edgecolor="black")
    ax.set_title("Frequency of Image Counts")
    ax.set_xlabel("Image Count")
    ax.set_ylabel("Frequency")

    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.get_tk_widget().pack()
    canvas.draw()

# Function to plot page count frequency as a histogram
def plot_page_count_frequency(parent):
    page_counts = [pdf["pages_total"] for pdf in pdf_data]
    bins = np.linspace(min(page_counts), max(page_counts), 10)  # Create 10 bins

    fig, ax = plt.subplots()
    ax.hist(page_counts, bins=bins, edgecolor="black")
    ax.set_title("Frequency of Page Counts")
    ax.set_xlabel("Page Count")
    ax.set_ylabel("Frequency")

    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.get_tk_widget().pack()
    canvas.draw()

# Function to plot word frequency
def plot_word_frequency(parent):
    word_counter = Counter()
    for pdf in pdf_data:
        word_counter.update(pdf["word_list"])

    most_common_words = word_counter.most_common(20)
    words, frequencies = zip(*most_common_words)

    fig, ax = plt.subplots()
    ax.bar(words, frequencies)
    ax.set_title("Top 20 Most Common Words")
    ax.set_xlabel("Words")
    ax.set_ylabel("Frequency")
    plt.xticks(rotation=45)

    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.get_tk_widget().pack()
    canvas.draw()

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

# Function to select a folder and process PDFs
def select_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        process_folder(folder_path)
        update_dropdown()
        tk.messagebox.showinfo("Success", "PDF data processed successfully!")

# Function to update dropdown with PDF names
def update_dropdown():
    pdf_dropdown["values"] = [pdf["pdf_name"] for pdf in pdf_data]

# Create the main UI
root = tk.Tk()
root.title("PDF Data Analyzer")

# Cumulative Analysis Section
tk.Button(root, text="Select Folder", command=select_folder).pack(pady=10)
tk.Button(root, text="Cumulative Analysis", command=display_cumulative_analysis).pack(pady=10)

# Individual Analysis Section
tk.Label(root, text="Select a PDF for Individual Analysis:").pack(pady=10)
selected_pdf_name = tk.StringVar()
pdf_dropdown = ttk.Combobox(root, textvariable=selected_pdf_name, state="readonly")
pdf_dropdown.pack(pady=10)
tk.Button(root, text="Analyze PDF", command=lambda: display_individual_analysis(selected_pdf_name.get())).pack(pady=10)

root.mainloop()