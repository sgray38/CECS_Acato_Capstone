from pypdf import PdfReader
import spacy
import re

nlp = spacy.load("en_core_web_sm")

BULLET_REGEX = r"^\s*[\-\*\•]|\d+\.\s|\([a-zA-Z]\)\s"  # Matches bullets like *, -, •, 1., a)

def is_bullet_point(line):
    """ Check if a line is a bullet point """
    return re.match(BULLET_REGEX, line.strip()) is not None

def extract_paragraphs_and_bullets(pdf_path):
    reader = PdfReader(pdf_path)
    raw_text = ""

    for page in reader.pages:
        text = page.extract_text()
        if text:
            raw_text += "\n" + text.strip()  # Preserve line breaks

    # Split text into lines
    lines = raw_text.split("\n")
    paragraphs = []
    temp_para = ""

    for i, line in enumerate(lines):
        line = line.strip()

        if not line:  # Empty line signals paragraph break
            if temp_para:
                paragraphs.append(temp_para.strip())
                temp_para = ""
        elif is_bullet_point(line):  # Handle bullet points separately
            if temp_para:
                paragraphs.append(temp_para.strip())  # Store previous paragraph
            paragraphs.append(line)  # Store bullet point separately
            temp_para = ""  # Reset temp buffer
        else:
            temp_para += " " + line if temp_para else line  # Merge into a paragraph

    if temp_para:
        paragraphs.append(temp_para.strip())  # Append last paragraph if exists

    # Use spaCy to refine sentence chunking
    refined_paragraphs = []
    for para in paragraphs:
        doc = nlp(para)
        refined_paragraphs.append(" ".join([sent.text.strip() for sent in doc.sents]))

    return refined_paragraphs

def load_pdf(file_path):
    """Load the PDF file and return the PdfReader object."""
    return PdfReader(file_path)

def extract_text_from_pdf(pdf_reader):
    """Extract text from all pages of the PDF."""
    proposal_content = []
    for page in pdf_reader.pages:
        proposal_content.append(page.extract_text())
    return "".join(proposal_content)

def split_into_paragraphs(content):
    """Split the content into paragraphs by empty newlines."""
    paragraphs = [p.strip() for p in content.split('\n ') if p.startswith('\n') and p.endswith(' ')]
    return paragraphs

def filter_short_paragraphs(paragraphs, word_threshold=10):
    """Filter out paragraphs that are too short."""
    return [p for p in paragraphs if len(p.split()) > word_threshold]

def process_pdf(file_path):
    """Process the PDF and return valid paragraphs."""
    pdf_reader = load_pdf(file_path)
    content = extract_text_from_pdf(pdf_reader)
    paragraphs = split_into_paragraphs(content)
    if len(paragraphs) <= len(pdf_reader.pages)*2:
        # we have a badly formatted PDF with no logical text breaks.
        # Fall back to the bullet point extraction method
        paragraphs = extract_paragraphs_and_bullets(file_path)
    filtered_paragraphs = filter_short_paragraphs(paragraphs)
    if not filtered_paragraphs:
        raise ValueError("No valid paragraphs found in the PDF content.")
    return filtered_paragraphs

if __name__ == "__main__":
    # Example usage
    file_path = 'ExampleRFPs/GoodFit/IETSS DRAFT PWS v2 for RFI FINAL to POST.pdf' 
    # "ExampleRFPs\GoodFit\Attachment A - Statement of Work_July 2023.pdf"
    # 'ExampleRFPs/GoodFit/IETSS DRAFT PWS v2 for RFI FINAL to POST.pdf'
    paragraphs = process_pdf(file_path)
    # join and write to file
    with open('output.txt', 'w', encoding='utf-8') as f:
        for paragraph in paragraphs:
            f.write(paragraph + '\n\n')