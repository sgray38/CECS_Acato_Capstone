from transformers import pipeline
# Load a summarization pipeline
summarizer = pipeline("summarization", 
                      model="facebook/bart-large-cnn")

def summarize_text(text: str) -> str:
    """Summarize the input text using the summarization pipeline."""
    # Adjust max_length and min_length as needed but dont exceed the attention limit of the model
    summary = summarizer(text, max_length=len(text)/2, min_length=30, do_sample=False) 
    return summary[0]['summary_text'] if summary else "No summary available."

if __name__ == "__main__":
        # input_text will be the chunk of text to summarize in the actual application
        input_text = '''The Contractor will be required to design, develop, or operate a system of records on individuals, to accomplish 
                        an agency function subject to the Privacy Act of 1974, Public Law 93-579, December 31, 1974 (5 U.S.C. 552a) and 
                        applicable agency regulations. Violation of the Act may involve the imposition of criminal penalties.'''
        summary = summarize_text(input_text)
        print("Summary:")
        print(summary)