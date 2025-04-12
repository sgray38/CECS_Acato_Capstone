# query_doc.py
# this script is used to query the loaded documents that will sent to a summarization model
import logging
import sys
from sentence_transformers import SentenceTransformer
import torch
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("RAGapp.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)
model = SentenceTransformer('all-MiniLM-L6-v2')

def query_document(query: str, context: list) -> str:
    """Query the document with the given query string and return a response."""
    try:
        # Encode the query and the context
        query_embedding = model.encode(query, convert_to_tensor=True)
        context_embedding = model.encode(context, convert_to_tensor=True)
        
        # Compute cosine similarity
        cosine_scores = model.similarity(query_embedding, context_embedding)
        # get top results
        top_results = torch.topk(cosine_scores, k=len(context)//2 if len(context) > 5 else len(context))
        response = []
        # generate response based on scores and indices
        scored_context = zip(top_results.values[0], top_results.indices[0])
        # sort by index to maintain original order
        scored_context = sorted(scored_context, key=lambda x: x[1].item())
        for score, idx in scored_context:
            if score.item() > 0.29:  # threshold for relevance
                response.append(f"{context[idx]}")
                # (Score: {score.item():.4f} | line {idx})")
        return "\n".join(response) if response else "No relevant context found."
    except Exception as e:
        logger.error(f"Error during querying: {e}")
        return f"Error during querying: {e}"

def get_top_result(context, query, n_results=1):
    query_embedding = model.encode(query, convert_to_tensor=True)
    context_embedding = model.encode(context, convert_to_tensor=True)
    cosine_scores = model.similarity(query_embedding, context_embedding)
    top_results = torch.topk(cosine_scores, k=n_results)
    # get a list of top results as tuples of (score, index)
    scored_context = zip(top_results.values[0], top_results.indices[0])
    scored_context = sorted(scored_context, key=lambda x: x[0].item(), reverse=True)
    # join the top results into a response string with score
    response = []
    for score, idx in scored_context:
        if score.item() > 0.29:  # threshold for relevance
            response.append(f"{context[idx]} (Score: {score.item():.4f} | line {idx})")
    return "\n".join(response) if response else "No relevant context found."
    
if __name__ == "__main__":
    # Example query and context
    query = "What is the purpose of the Contractor?"
    context = [
        "The Contractor will be required to design, develop, or operate a system of records on individuals, to accomplish "
        "an agency function subject to the Privacy Act of 1974, Public Law 93-579, December 31, 1974 (5 U.S.C. 552a) and "
        "applicable agency regulations.",
        "Violation of the Act may involve the imposition of criminal penalties.",
        'Deliverables in this contract include the design, development, testing, implementation and documentation tasks.'
    ]
    
    response = query_document(query, context)
    print("Query Response:")
    print(response)
        