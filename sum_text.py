import logging
import sys
from transformers import pipeline
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("sum_text.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)
# Load a summarization pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def split_text_into_chunks(text: str, words_per_chunk: int = 1024) -> list:
    """Split the input text into chunks that fit within the threshold of words_per_chunk."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), words_per_chunk):
        chunks.append(" ".join(words[i:i + words_per_chunk]))
        logger.info(f"Chunk created with {len(chunks[-1].split())} words.")
        # print(f"Chunk text: {chunks[-1]}")
    return chunks

def summarize_text(text: str) -> str:
    """Summarize the input text using the summarization pipeline."""
    try:
        # Split text into chunks if it exceeds the word limit
        chunks = split_text_into_chunks(text.strip(), words_per_chunk=142)  # Use 142 as a safe limit for BART attention
        summaries = []
        
        for chunk in chunks:
            if len(chunk.split()) > 10:  
                summary = summarizer(chunk)
                summaries.append(summary[0]['summary_text'] if summary else "No summary available.")
                logger.info(f"Processed chunk: {chunk[:50]}...")
            else:
                summaries.append(chunk)
        
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