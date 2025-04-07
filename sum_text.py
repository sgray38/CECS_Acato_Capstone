from transformers import pipeline
# Load a summarization pipeline
summarizer = pipeline("summarization", 
                      model="facebook/bart-large-cnn")

# Summarize each paragraph
def summarize_text(paragraphs:list[str]):
    summaries = []
    for idx, chunk in enumerate(paragraphs):
        try:
            # BART can handle up to 1024 tokens, but we keep it smaller for safety
            if len(chunk.split()) >= 1024: 
    
                print(f"Chunk {idx} is too long, splitting into smaller parts.")
                sub_chunks = chunk.split('. ')  # Split by sentences or paragraphs
                for sub_idx, sub_chunk in enumerate(sub_chunks):
                    if len(sub_chunk.split()) > 30:  # Only summarize meaningful chunks
                        summary = summarizer(sub_chunk, 
                                            min_length=30, 
                                            do_sample=False, 
                                            truncation=True)
                        summaries.append((f"{idx}.{sub_idx}", summary[0]['summary_text']))
                        print(f"Summary {idx}.{sub_idx}: {summary[0]['summary_text']}\n")
                
            # if the chunk is to large, we need to split it into smaller part
            elif len(chunk.split()) < 30:
                # add it to the next chunk if it's too short to summarize meaningfully
                if idx+1 <= len(paragraphs):
                    paragraphs[idx + 1] = paragraphs[idx] + " " + paragraphs[idx + 1]
                    print(f"Chunk {idx} is too short, merged with Chunk {idx + 1}.")
            else:
                summary = summarizer(chunk, 
                                        min_length=30,  # Adjust min_length as needed
                                        do_sample=False,  # Set to True for more diverse summaries
                                        truncation=True,  # Ensure long texts are truncated properly
                                        )
                
                summaries.append((idx, summary[0]['summary_text']))
                
                print(f"Summary {idx}: {summary[0]['summary_text']}\n")
        except Exception as e:
            print(f"Error summarizing chunk {idx}: {e}")
            summaries.append((idx, "Summary not available."))
            
if __name__ == "__main__":
    # Example usage
    import json # json representation of the paragraphs list
    
    with open('paragraphs.json', 'r', encoding='utf-8') as f:
        paragraphs_data = json.load(f)
    # make the paragraphs a list of strings
    paragraphs = [str(p) for p in paragraphs_data]
    # summarize the paragraphs
    summaries = summarize_text(paragraphs)