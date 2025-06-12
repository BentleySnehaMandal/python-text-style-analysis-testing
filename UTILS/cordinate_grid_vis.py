import fitz  # PyMuPDF

def overlay_coordinate_grid(pdf_path, output_path, grid_spacing=100):
    """
    Overlay a coordinate grid on the first page of a PDF to visualize the local coordinate system.
    :param pdf_path: Path to the input PDF file.
    :param output_path: Path to save the output PDF with the grid.
    :param grid_spacing: Spacing between grid lines in points (default is 100 points).
    """
    # Open the PDF
    doc = fitz.open(pdf_path)
    first_page = doc[0]  # Get the first page

    # Get page dimensions
    page_width = first_page.rect.width
    page_height = first_page.rect.height

    # Draw horizontal grid lines
    for y in range(0, int(page_height), grid_spacing):
        first_page.draw_line((0, y), (page_width, y), color=(0, 0, 1), width=0.5)  # Blue horizontal lines

    # Draw vertical grid lines
    for x in range(0, int(page_width), grid_spacing):
        first_page.draw_line((x, 0), (x, page_height), color=(1, 0, 0), width=0.5)  # Red vertical lines

    # Save the modified PDF
    doc.save(output_path)
    print(f"Grid overlay saved to: {output_path}")

# Example usage
if __name__ == "__main__":
    input_pdf = "C:\\Users\\Sneha.Mandal\\Downloads\\Hi hello worldsmallverysmall.pdf"  # Replace with your PDF path
    output_pdf = "C:\\Users\\Sneha.Mandal\\Downloads\\coords\\Hi hello worldsmallverysmall_with_grid.pdf"
    overlay_coordinate_grid(input_pdf, output_pdf)

# "C:\Users\Sneha.Mandal\Downloads\HihelloworldLarge.pdf"
# "C:\Users\Sneha.Mandal\Downloads\Hihelloworldsmall.pdf"
# "C:\Users\Sneha.Mandal\Downloads\Hi hello worldsmallverysmall.pdf"