import os
import json
import pdfplumber
from collections import defaultdict

# Function to classify styles
def classify_styles(char_info):
    fontname = char_info['fontname']
    return {
        "fontname": fontname,
        "size": round(char_info['size']),
        "stroking_color": char_info['stroking_color'],
        "non_stroking_color": char_info['non_stroking_color'],
        "isBold": 'bold' in fontname.lower(),
        "isItalic": 'italic' in fontname.lower()
    }

# Function to extract character information from the PDF
def extract_char_info(pdf_path):
    char_list = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            for char in page.chars:
                text = char.get('text')
                if text and (text.isalpha() or text.isdigit()):  # Check if the character is a letter or a digit
                    char_info = {
                        'fontname': char.get('fontname'),
                        'size': char.get('size'),
                        'stroking_color': char.get('stroking_color'),
                        'non_stroking_color': char.get('non_stroking_color'),
                        'page_number': page_number
                    }
                    char_list.append(char_info)
    return char_list

# Function to generate JSON report for a PDF
def generate_report(pdf_path, output_folder):
    char_list = extract_char_info(pdf_path)
    unique_styles = set()
    for char_info in char_list:
        style = classify_styles(char_info)
        unique_styles.add(json.dumps(style))  # Use JSON string for set comparison

    # Convert styles back to dictionaries
    unique_styles = [json.loads(style) for style in unique_styles]

    # Save the JSON report
    report = {
        "pdf_name": os.path.basename(pdf_path),
        "unique_styles": unique_styles
    }
    output_path = os.path.join(output_folder, f"{os.path.basename(pdf_path).replace('.pdf', '')}_report.json")
    with open(output_path, "w") as json_file:
        json.dump(report, json_file, indent=4)
    print(f"Report generated for {pdf_path}: {output_path}")
    return report

# Function to find common styles across all reports
def find_common_styles(report_folder):
    style_to_pdfs = defaultdict(set)

    # Read all JSON reports
    for report_file in os.listdir(report_folder):
        if report_file.endswith("_report.json"):
            with open(os.path.join(report_folder, report_file), "r") as file:
                report = json.load(file)
                pdf_name = report["pdf_name"]
                for style in report["unique_styles"]:
                    style_key = json.dumps(style, sort_keys=True)  # Use JSON string for comparison
                    style_to_pdfs[style_key].add(pdf_name)

    # Find common styles
    common_styles = {style: pdfs for style, pdfs in style_to_pdfs.items() if len(pdfs) > 1}

    # Print the common styles
    print("\nCommon Styles Across PDFs:")
    for style, pdfs in common_styles.items():
        print(f"Style: {json.loads(style)}")
        print(f"Used in PDFs: {', '.join(pdfs)}\n")

    return common_styles

# Main function
def main():
    input_folder = "CADPLANFOLDER"  # Folder containing the PDFs
    output_folder = "REPORTS"  # Folder to save the JSON reports

    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Generate reports for all PDFs in the input folder
    for file_name in os.listdir(input_folder):
        if file_name.endswith(".pdf"):
            pdf_path = os.path.join(input_folder, file_name)
            generate_report(pdf_path, output_folder)

    # Find common styles across all reports
    find_common_styles(output_folder)

if __name__ == "__main__":
    main()