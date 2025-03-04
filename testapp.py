import json
import os

# Directory paths
obtained_results_dir = "obtainedResults"
original_results_dir = "originalResults"

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Load JSON data from a file
def load_json(filepath):
    with open(filepath, "r") as file:
        return json.load(file)

# Normalize font names
def normalize_fontname(fontname):
    return fontname.replace("-", "").replace("_", "").replace("+", "").replace(" ", "").replace(",", "").lower()

# Check if a style is present in unique_styles
def is_style_present(style, unique_styles):
    normalized_style = normalize_fontname(style)
    for unique_style in unique_styles:
        if normalized_style in normalize_fontname(unique_style['fontname']):
            return True
    return False

# Test 1: Check for missing and extra styles
print(f"{Colors.HEADER}Test 1: Check for missing and extra styles{Colors.ENDC}")
print(f"{Colors.HEADER}==========================================={Colors.ENDC}")
for obtained_filename in os.listdir(obtained_results_dir):
    if obtained_filename.endswith(".json"):
        obtained_filepath = os.path.join(obtained_results_dir, obtained_filename)
        original_filename = obtained_filename.replace("result_new", "Original_result_")
        original_filepath = os.path.join(original_results_dir, original_filename)

        if os.path.exists(original_filepath):
            obtained_data = load_json(obtained_filepath)
            original_data = load_json(original_filepath)

            used_styles = original_data.get("usedStyles", [])
            unique_styles = obtained_data.get("unique_styles", {})

            # Check for missing styles
            missing_styles = [style for style in used_styles if not is_style_present(style, unique_styles.values())]

            # Check for extra styles
            extra_styles = [unique_style['fontname'] for unique_style in unique_styles.values() if not any(is_style_present(style, [unique_style]) for style in used_styles)]

            # Log the results
            print(f"{Colors.OKBLUE}Results for {obtained_filename}:{Colors.ENDC}")
            print(f"{Colors.OKBLUE}-----------------------------{Colors.ENDC}")
            print(f"{Colors.OKCYAN}Checking for missing styles...{Colors.ENDC}")
            if missing_styles:
                print(f"{Colors.FAIL}  Missing styles: {missing_styles}{Colors.ENDC}")
            else:
                print(f"{Colors.OKGREEN}  No missing styles.{Colors.ENDC}")
                print(f"{Colors.OKGREEN}Result: PASSED{Colors.ENDC}")
            print(f"{Colors.OKCYAN}.............................{Colors.ENDC}")
            print(f"{Colors.OKCYAN}Checking for extra styles...{Colors.ENDC}")
            if extra_styles:
                print(f"{Colors.WARNING}  Extra styles: {extra_styles}{Colors.ENDC}")
            else:
                print(f"{Colors.OKGREEN}  No extra styles.{Colors.ENDC}")
                print(f"{Colors.OKGREEN}Result: PASSED{Colors.ENDC}")
            print()
        else:
            print(f"{Colors.FAIL}Original file not found for {obtained_filename}{Colors.ENDC}")