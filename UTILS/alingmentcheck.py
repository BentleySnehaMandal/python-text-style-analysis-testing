import pdfplumber
from pdfplumber.ctm import CTM

# Function to draw bounding boxes for text with a specific skewness range
def draw_bounding_boxes(pdf_path, output_image_path, target_skewness, skew_tolerance=1.0):
    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            # Get the page rotation
            page_rotation = page.rotation or 0  # Default to 0 if no rotation is specified
            print(page_rotation)
            # Get the page image
            page_image = page.to_image()

            # List to store bounding boxes
            bounding_boxes = []

            for char in page.chars:
                # Extract the transformation matrix and calculate skewness
                char_matrix = char.get("matrix")
                if not char_matrix:
                    continue
                char_ctm = CTM(*char_matrix)
                char_skewness = round(char_ctm.skew_x + page_rotation, 2)  # Add page rotation to character skewness

                # Debugging: Print skewness and bounding box coordinates
                print(f"Character: {char.get('text')}, Skewness: {char_skewness}, Bounding Box: ({char['x0']}, {char['top']}, {char['x1']}, {char['bottom']})")

                # Check if the skewness is within the target range
                if target_skewness - skew_tolerance <= char_skewness <= target_skewness + skew_tolerance:
                    # Add the bounding box to the list
                    bounding_boxes.append({
                        "x0": char["x0"],
                        "top": char["top"],
                        "x1": char["x1"],
                        "bottom": char["bottom"]
                    })

            # Draw the bounding boxes on the page image
            page_image.draw_rects(bounding_boxes, stroke="red", stroke_width=2)

            # Save the image with bounding boxes
            output_path = f"{output_image_path}_page_{page_number}.png"
            page_image.save(output_path)
            print(f"Bounding boxes saved to {output_path}")

# Example usage
pdf_path = "C:/Users/Sneha.Mandal/python-test-folder/TestPdfs/singletestpdf00.pdf"  # Path to the PDF
output_image_path = "image_acurate"  # Output image file prefix
target_skewness = 13.2 # Skewness to filter
draw_bounding_boxes(pdf_path, output_image_path, target_skewness)