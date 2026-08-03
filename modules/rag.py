import os
import faiss
import numpy as np
import pandas as pd

from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

# -----------------------------
# Load API Key
# -----------------------------
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# -----------------------------
# Load Dataset
# -----------------------------
df = pd.read_excel("data/World_Cricketers.xlsx")

documents = []

for _, row in df.iterrows():

    doc = f"""
Name: {row['Name']}
Country: {row['Country']}
Role: {row['Role']}
Batting/Bowling Style: {row['Batting/Bowling Style']}
Era: {row['Era']}
Notable Achievements: {row['Notable Achievements']}
Background: {row['Background']}
"""

    documents.append(doc.strip())

# -----------------------------
# Load Model
# -----------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")

# -----------------------------
# Load FAISS
# -----------------------------
index = faiss.read_index("vector_db/cricket_index.faiss")

# -----------------------------
# BM25
# -----------------------------
tokenized_docs = [doc.lower().split() for doc in documents]
bm25 = BM25Okapi(tokenized_docs)


# -----------------------------
# Reciprocal Rank Fusion
# -----------------------------
def rrf(result_lists, k=60):

    scores = {}

    for results in result_lists:

        for rank, doc in enumerate(results):

            scores[doc] = scores.get(doc, 0) + 1 / (k + rank + 1)

    ranked = sorted(scores.items(),
                    key=lambda x: x[1],
                    reverse=True)

    return [doc for doc, _ in ranked]


# -----------------------------
# Generate Answer Function
# -----------------------------
def generate_answer(query):

    # Semantic Search
    query_embedding = model.encode([query])

    _, semantic_indices = index.search(query_embedding, 5)

    semantic_results = semantic_indices[0].tolist()

    # BM25 Search
    scores = bm25.get_scores(query.lower().split())

    bm25_results = np.argsort(scores)[::-1][:5].tolist()

    # Hybrid Search
    hybrid_results = rrf([semantic_results, bm25_results])

    # Build Context
    context = ""

    for idx in hybrid_results[:5]:
        context += documents[idx] + "\n\n"

    prompt = f"""
You are a cricket expert.

Answer ONLY using the information below.

Context:

{context}

Question:

{query}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content


# -----------------------------
# Run only if executed directly
# -----------------------------
if __name__ == "__main__":

    query = input("Ask anything about cricketers: ")

    answer = generate_answer(query)

    print("\n========================")
    print("RAG ANSWER")
    print("========================\n")

    print(answer)