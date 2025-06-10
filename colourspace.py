import webcolors

# Helper function to get the closest color name
def get_color_name(rgb):
    try:
        # Try to get the exact color name
        return webcolors.rgb_to_name(rgb)
    except ValueError:
        # If exact match is not found, get the closest color name
        closest_name = webcolors.rgb_to_name(webcolors.rgb_to_hex(rgb))
        return f"Closest Match: {closest_name}"

# Helper function to normalize color values
def normalize_color(color):
    if color is None:
        return "None"  # No color specified
    if len(color) == 1:  # DeviceGray
        gray_value = int(color[0] * 255)  # Scale to 0-255
        rgb = (gray_value, gray_value, gray_value)
        return get_color_name(rgb)
    if len(color) == 3:  # DeviceRGB
        r, g, b = [int(c * 255) for c in color]  # Scale to 0-255
        rgb = (r, g, b)
        return get_color_name(rgb)
    if len(color) == 4:  # DeviceCMYK
        c, m, y, k = color
        r = int(255 * (1 - c) * (1 - k))
        g = int(255 * (1 - m) * (1 - k))
        b = int(255 * (1 - y) * (1 - k))
        rgb = (r, g, b)
        return get_color_name(rgb)
    return "Unknown Color Space"