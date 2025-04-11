from pypdf import PdfReader
import re
from collections import Counter

def load_pdf(file_path):
    """Load the PDF file and return the PdfReader object."""
    return PdfReader(file_path)

def remove_headers_and_footers(page_texts:list[str]):
    """Remove headers and footers that appear consistently on each page."""
    # Extract first 5 lines to look for repeated content on each page unless the page is too short
    first_lines = []
    for page_text in page_texts:
        lines = page_text.splitlines()
        # Get the first 5 non-empty lines
        non_empty_lines = [line for line in lines if line.strip()]
        if non_empty_lines:
            first_lines.append(non_empty_lines[:5])
    
    # Find common lines that appear
    common_lines = Counter(sum(first_lines, [])).most_common(4)
    
    # Filter out lines that appear less then len(page_texts) - 2 times
    # title pages and final pages frequently dont have headers/footers, so we allow for some leniency
    lines_to_remove = filter(lambda x: x[1] >= len(page_texts) - 2 and x[0] != '', common_lines)
    lines_to_remove = list(map(lambda x: x[0], lines_to_remove))  # Extract only the line text
    if not lines_to_remove:
        return page_texts  # No headers/footers found, return original text
    
    # compile a pattern to match these lines for any document
    header_footer_regex = re.compile(r'^\s*(' + '|'.join(re.escape(line) for line in lines_to_remove) + r')\s*$', re.MULTILINE)
    # Remove these lines from each page
    cleaned_pages = []
    for page_text in page_texts:
        cleaned_text = header_footer_regex.sub('', page_text)
        
        cleaned_pages.append(cleaned_text)
    return cleaned_pages

def remove_pg_numbers(page_text:list[str]):
    """Remove page numbers from the text."""
    patterns = [
        # Matches "Page X of Y"
        r'\bPage\s+\d+\s+of\s+\d+\b',  
        # Matches "X | Page"
        r'\b\d+\s*\|\s*Page\b',  
        # Matches "Page X"
        r'\bPage\s+\d+\b'    
    ]
    possible_matches = filter(lambda p: re.search(p, page_text[-1], re.IGNORECASE), patterns)
    possible_matches = list(possible_matches)
    if not possible_matches:
        stand_alone_pgn = r'(?<!\d)\s*\d+\s*(?=\n|$)'
        possible_matches = [stand_alone_pgn]  # Fallback to standalone page numbers if no other patterns match
    
    cleaned_pages = []
    for page in page_text:
    # we are looking at a single page text, figure which pattern to use with a match
        for pattern in possible_matches:
            page = re.sub(pattern, '', page, flags=re.IGNORECASE)
        cleaned_pages.append(page)
    return cleaned_pages
    
def extract_text_from_pdf(pdf_reader:PdfReader):
    """Extract text from all pages of the PDF."""
    proposal_content = []
    for page in pdf_reader.pages:
        proposal_content.append(page.extract_text())
    # remove headers and footers if necessary
    proposal_content = remove_pg_numbers(proposal_content)
    proposal_content = remove_headers_and_footers(proposal_content)
    if not proposal_content:
        raise ValueError("Failed to extract text from the PDF or the PDF is empty.")
    return "".join(proposal_content)

def split_into_paragraphs(content:str):
    """Split the content into paragraphs by empty newlines."""
    paragraphs = [p.strip() for p in content.split('\n ')]
    return paragraphs

def filter_short_paragraphs(paragraphs:list[str], word_threshold=1):
    """Filter out paragraphs that are too short."""
    return [p for p in paragraphs if len(p.split(" ")) > word_threshold]

def process_pdf(file_path:str):
    """Process the PDF and return valid paragraphs."""
    pdf_reader = load_pdf(file_path)
    content = extract_text_from_pdf(pdf_reader)
    paragraphs = split_into_paragraphs(content)
    # if len(paragraphs) <= 4:
    #     # we have a badly formatted PDF with no logical text breaks.
    #     # Fall back to the bullet point extraction method
    #     paragraphs = extract_paragraphs_and_bullets(file_path)
    filtered_paragraphs = filter_short_paragraphs(paragraphs)
    if not filtered_paragraphs:
        raise ValueError("No valid paragraphs found in the PDF content.")
    return filtered_paragraphs

if __name__ == "__main__":
    # Example usage
    file_path = 'ExampleRFPs/GoodFit/IETSS DRAFT PWS v2 for RFI FINAL to POST.pdf'
    # 'ExampleRFPs/BadFit/Draft_Retirement_Services_COBOL_Database_Modernization_PWS.pdf' 
    # 'ExampleRFPs\GoodFit\Attachment A - Statement of Work_July 2023.pdf'
    # 
    paragraphs = process_pdf(file_path)
    # join and write to file
    with open('output.txt', 'w', encoding='utf-8') as f:
        for paragraph in paragraphs:
            f.write(paragraph + '\n\n')