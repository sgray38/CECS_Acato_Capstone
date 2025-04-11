import logging
from pypdf import PdfReader
import spacy
import re
from collections import Counter
# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.info("Starting PDF text extraction and processing.")

# Load spaCy language model
nlp = spacy.load("en_core_web_sm")

# Regex to match bullet points
BULLET_REGEX = r"^\s*[\-\*\•]|\d+\.\s|\([a-zA-Z]\)\s"  # Matches bullets like *, -, •, 1., a)

def is_bullet_point(line):
    """Check if a line is a bullet point."""
    return re.match(BULLET_REGEX, line.strip()) is not None

def remove_headers_and_footers(page_texts):
    """Remove headers and footers that appear consistently on each page."""
    # Extract first 3 lines to look for repeated content on each page
    first_lines = []
    for i in range(3):
        first_lines.append([text.split("\n")[i] for text in page_texts if text != ""])

    # Identify most common first and last lines (likely header and footer)
    header = Counter(
        # flatten the list of first lines and count occurrences
        line for sublist in first_lines for line in sublist if line
        ).most_common(3)  # Get the most common header line
    # filter the counts of headers by page count, header count == number of pages - 1
    for text, count in header.copy():
        if count < len(page_texts) - 2 or text == " ":
            header.remove((text, count))
            
    if not header:
        logger.info("No consistent header found.")
    else:
        logger.info(f"Identified headers: {header}")
        
    h_names = [h[0].strip() for h in header if h[0].strip() != ""]
    # Remove headers
    cleaned_pages = []
    for text in page_texts:
        logger.info(f"Cleaning page {len(cleaned_pages) + 1}")
        lines = text.split("\n ")
        # Remove header lines
        cleaned_text = "\n ".join(line.strip() for line in lines if line.strip() not in h_names)
        # Remove page numbers from the string if present for "Page X of Y" and "Page X" and 'x | Page'
        mod_text_1 = re.sub(r'\bPage\s+\d+\s+of\s+\d+\b', '', cleaned_text, flags=re.IGNORECASE)
        mod_text_2 = re.sub(r'\bPage\s+\d+\b', '', cleaned_text, flags=re.IGNORECASE)
        mod_text_3 = re.sub(r'\b\d+\s*\|\s*Page\b', '', cleaned_text, flags=re.IGNORECASE)
        if mod_text_1 != cleaned_text:
            logger.info(f"Removed page numbers with 'Page X of Y' from headers.")
            mod_text = mod_text_1
        elif mod_text_2 != cleaned_text and mod_text_3 == cleaned_text:
            logger.info(f"Removed page numbers with 'Page X' from headers.")
            # Only mod_text_2 is different, so we keep it
            mod_text = mod_text_2
        elif mod_text_3 != cleaned_text:
            logger.info(f"Removed page numbers with 'x | Page' from headers.")
            mod_text = mod_text_3
        else:
            mod_text = cleaned_text
        cleaned_pages.append(mod_text)
    cleaned_pages = nlp("\n".join(cleaned_pages))  # Process the cleaned text with spaCy
    cleaned_pages = [sent.text.strip() for sent in cleaned_pages.sents if sent.text.strip()]
    return cleaned_pages

def extract_paragraphs_and_bullets(pdf_path):
    logger.info(f"whitespace extraction failed for {pdf_path}, attempting to extract paragraphs and bullets.")
    reader = PdfReader(pdf_path)
    raw_text = ""

    for page in reader.pages:
        text = page.extract_text()
        if text:
            raw_text += "\n" + text  # Preserve line breaks

    # Split text into lines
    lines = raw_text.split("\n")
    paragraphs = []
    temp_para = ""

    for i, line in enumerate(lines):
        line = line.strip()

        if not line:  # Empty line signals paragraph break
            if temp_para:
                paragraphs.append(temp_para)
                temp_para = ""
        elif is_bullet_point(line):  # Handle bullet points separately
            if temp_para:
                paragraphs.append(temp_para)  # Store previous paragraph
            paragraphs.append(line)  # Store bullet point separately
            temp_para = ""  # Reset temp buffer
        else:
            temp_para += " " + line if temp_para else line  # Merge into a paragraph

    if temp_para:
        paragraphs.append(temp_para)  # Append last paragraph if exists

    # Use spaCy to refine sentence chunking
    refined_paragraphs = []
    for para in paragraphs:
        doc = nlp(para)
        refined_paragraphs.append("\n".join([sent.text.strip() for sent in doc.sents if sent.text.strip()]))

    return refined_paragraphs

def load_pdf(file_path):
    """Load the PDF file and return the PdfReader object."""
    return PdfReader(file_path)

def extract_text_from_pdf(pdf_reader):
    """Extract text from all pages of the PDF."""
    proposal_content = []
    for page in pdf_reader.pages:
        proposal_content.append(page.extract_text())
    # remove headers and footers if necessary
    if proposal_content:
        proposal_content = remove_headers_and_footers(proposal_content)
    else:
        raise ValueError("The PDF is empty or could not be read properly.")
    
    return "".join(proposal_content)

def split_into_paragraphs(content):
    """Split the content into paragraphs by empty newlines."""
    paragraphs = [p.strip() for p in content.split('\n ')]
    logger.info(f"Split content into {len(paragraphs)} segments.")
    return paragraphs

def filter_short_paragraphs(paragraphs, word_threshold=5):
    """Filter out paragraphs that are too short."""
    return [p for p in paragraphs if len(p.split(" ")) > word_threshold]

def process_pdf(file_path):
    """Process the PDF and return valid paragraphs."""
    pdf_reader = load_pdf(file_path)
    content = extract_text_from_pdf(pdf_reader)
    if not content.strip():
        raise ValueError("The PDF is empty or could not be read properly.")
    
    paragraphs = split_into_paragraphs(content)
    if len(paragraphs) <= 10:
        # Handle poorly formatted PDFs with no logical text breaks
        paragraphs = extract_paragraphs_and_bullets(file_path)
    
    filtered_paragraphs = filter_short_paragraphs(paragraphs)
    if not filtered_paragraphs:
        raise ValueError("No valid paragraphs found in the PDF content.")
    return filtered_paragraphs

if __name__ == "__main__":
    # Example usage
    pdir = "ExampleRFPs/"
    pdf_names = [
    'GoodFit/IETSS DRAFT PWS v2 for RFI FINAL to POST.pdf',
    'GoodFit/Attachment A - Statement of Work_July 2023.pdf', 
    'GoodFitWithPartners/2024_11_15_R_G1ab8GqBwjXy42h_1.pdf',
    'GoodFitWithPartners/2.2.1 Attachment 1 GMMAD BPA PWS 112724.1732744126731.pdf',
    'BadFit/Draft_Retirement_Services_COBOL_Database_Modernization_PWS.pdf', # <-- This doc is driving me nuts, there is no logical text breaks between  numbered sections
    'GoodFit/RFP+CR-346570+Attachment+A+SOW+SQA+Consulting.pdf',
    'GoodFitWithPartners/FPAC Conservation Agile Release Train PWS.1729019986846.pdf',
    'GoodFitWithPartners/CB24-RFQ0009 IT Project Manager.pdf'
    ]

    file_path = pdir + pdf_names[-1]  # Change index to test different PDFs
    
    paragraphs = process_pdf(file_path)
    # Write processed paragraphs to a file
    with open('output.txt', 'w', encoding='utf-8') as f:
        for paragraph in paragraphs:
            f.write(paragraph + '\n\n')