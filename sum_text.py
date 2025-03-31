from transformers import pipeline

text = "summarize: OBJECTIVE/PURPOSE - Battelle Memorial Institute, Pacific Northwest Division, operator of the Pacific Northwest National Laboratory (PNNL) for the U.S. Department of Energy is working through a digital transformation through critical strategic objectives against our operating model. BACKGROUND - PNNL has a portfolio of strategic initiatives to modernize various business systems, and operating model improvements initiatives for Assets & Facilities and Operations. In support of these needs, PNNL needs an agile project manager to successfully lead these efforts through planning and execution against strategic roadmaps."
summarizer = pipeline("summarization", model="ckds/gov_sum_model")
print(summarizer(text, batch_size=8))