

## config, move to config file later
CONFIG = {
    "SOURCE_PDF" : "../../resources/grundwortschatz.pdf",
    "PAGES" : (14, 25)
}


## code

from pypdf import PdfReader
import re
import pprint


def extract_text_from_pdf(config):
    """
    Extract text from a PDF file that has a text layer.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        str: Extracted text from all pages
    """
    text = ""
    # pdf_path = config["SOURCE_PDF"]
    pdf_reader = PdfReader(config["SOURCE_PDF"])
    for page_num in range(config["PAGES"][0]-1, config["PAGES"][1]):
        text += pdf_reader.pages[page_num].extract_text() + "\n\n"
        
    # Remove standalone numbers (page numbers are usually on their own line)
    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
    # Also remove numbers at the end of lines followed by newline
    text = re.sub(r'\s+\d+\s*\n', '\n', text)
    
    return text.strip()
    
# TODO: code below works for all but "9. Affixe" and "10. Stammkonstanz". remove those for now and repair later...

def parse_word_categories(text, use_subcategories=True):
    """
    Parse text with numbered categories into a dictionary or nested dictionary.
    
    Args:
        text (str): Text with numbered categories (1., 2., etc.) and optional subcategories (a., b., etc.)
        use_subcategories (bool): If True, create nested dict with subcategories. If False, ignore subcategories.
        
    Returns:
        dict: Dictionary (flat or nested) with categories containing word lists
    """
    result = {}
    current_category = None
    current_subcategory = None
    
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check for main category (e.g., "1. ", "2. ")
        category_match = re.match(r'^\d+\.\s+(.+)$', line)
        if category_match:
            current_category = category_match.group(1).strip()
            result[current_category] = {} if use_subcategories else []
            current_subcategory = None
            continue
        
        # Check for subcategory (e.g., "a. ", "b. ")
        subcategory_match = re.match(r'^[a-z]\.\s+(.+)$', line)
        if subcategory_match:
            if use_subcategories and current_category is not None:
                current_subcategory = subcategory_match.group(1).strip()
                result[current_category][current_subcategory] = []
            continue
        
        # Extract words from the line
        if current_category is not None:
            words = [word.strip() for word in line.split() if word.strip()]
            
            if use_subcategories:
                if current_subcategory is not None:
                    result[current_category][current_subcategory].extend(words)
                else:
                    # No subcategory - convert to list if needed
                    if isinstance(result[current_category], dict) and not result[current_category]:
                        result[current_category] = []
                    if isinstance(result[current_category], list):
                        result[current_category].extend(words)
            else:
                result[current_category].extend(words)
    
    return result
    
    
if __name__ == "__main__":
    extracted_text = extract_text_from_pdf(CONFIG)
    print(f"lenght of text: {len(extracted_text)}")
    
    print_start = 3800
    print(extracted_text[print_start:print_start+1000])
    # if extracted_text:
    #     print(extracted_text[:1000])
    
    print("With subcategories:")   
    word_categories = parse_word_categories(extracted_text)
    pprint.pp(word_categories["Affixe"])
    
    print("\n\nWithout subcategories:")
    result = parse_word_categories(extracted_text, use_subcategories=False)
    for cat, words in result.items():
        print(f"\n{cat}: {len(words)} words - {words[:5]}...")