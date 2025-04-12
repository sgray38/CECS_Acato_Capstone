import logging
import sys
from transformers import pipeline
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("sum_text.log",encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)
# Load a summarization pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def split_text_into_chunks(text: str, sentences_per_chunk: int = 3) -> list:
    """Split the input text into chunks that fit within the threshold of sentences_per_chunk."""
    sentences = text.split("\n")
    # Remove empty sentences
    sentences = [s for s in sentences if s.strip()]
    chunks = []
    current_chunk = []
    for sentence in sentences:
        if len(current_chunk) < sentences_per_chunk:
            current_chunk.append(sentence.strip())
        else:
            chunks.append(" ".join(current_chunk))
            current_chunk = [sentence.strip()]
            logger.info(f"Created chunk: {len(chunks)} of size {len(chunks[-1].split())} words.")
            
    if current_chunk:
        chunks.append(" ".join(current_chunk))
        logger.info(f"Created final chunk: {len(chunks)} of size {len(chunks[-1].split())} words.")
    return chunks

def summarize_text(text: str) -> str:
    """Summarize the input text using the summarization pipeline."""
    try:
        # Split text into chunks if it exceeds the word limit
        chunks = split_text_into_chunks(text.strip(), sentences_per_chunk=7)  # Use 142 as a safe limit for BART attention
        summaries = []
        
        for chunk in chunks:
            summary = summarizer(chunk)
            summaries.append(summary[0]['summary_text'] if summary else "No summary available.")
            logger.info(f"Processed chunk: {chunk[:50]}...")
            
        
        # Combine all summaries into a single summary
        return "\n".join(summaries)
    except Exception as e:
        logger.error(f"Error during summarization: {e}")
        return f"Error during summarization: {e}"

if __name__ == "__main__":
    # Example input text
    input_text = '''The Contractor will be required to design, develop, or operate a system of records on individuals, to accomplish 
                    an agency function subject to the Privacy Act of 1974, Public Law 93-579, December 31, 1974 (5 U.S.C. 552a) and 
                    applicable agency regulations. Violation of the Act may involve the imposition of criminal penalties.'''
    summary = summarize_text(input_text)
    print("Summary:")
    print(summary)