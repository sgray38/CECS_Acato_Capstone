from llmsherpa.readers import LayoutPDFReader
import openai
from llama_index.core import Document
from llama_index.core import VectorStoreIndex
from sentence_transformers import SentenceTransformer, util
import torch
import numpy as np
# graph the vectors and their cosine similarities
import matplotlib.pyplot as plt
import networkx as nx
import chunkPDF as chunk

llmsherpa_api_url = "http://localhost:5010/api/parseDocument?renderFormat=all" # local API endpoint

#TODO: connect url to file explorer
url = ""
pdf_url = url
# "ExampleRFPs/GoodFit/IETSS DRAFT PWS v2 for RFI FINAL to POST.pdf" # also allowed is a file path e.g. /home/downloads/xyz.pdf
pdf_reader = LayoutPDFReader(llmsherpa_api_url)
doc = pdf_reader.read_pdf(pdf_url)

model = SentenceTransformer('all-MiniLM-L6-v2')
# Encode the paragraphs into embeddings.
sections = []
for section in doc.sections():
    sections.append(section.to_context_text(include_section_info=True))
    # sections.append(section.title)
doc_embeddings = model.encode(sections, convert_to_tensor=True)


#TODO: Connect Queries to query box
#queries = input("Enter Queries: ")
for query in queries:
    query_embedding = model.encode(query, convert_to_tensor=True)
    similarities = model.similarity(query_embedding, doc_embeddings)[0]
    # top 5 results
    top_indices = torch.topk(similarities, 5)
    for i in range(len(top_indices[0])):
        print(f"Query: {query}\nResult {i}:\n{sections[top_indices[1][i]]}\nScore: {top_indices[0][i].item():.4f}\n")

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
        
        #TODO: Connect input_text to output of RAG
        input_text = rag_output
        summary = summarize_text(input_text)
        print("Summary:")
        print(summary)