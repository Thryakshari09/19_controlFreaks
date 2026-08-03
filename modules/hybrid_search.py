import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

from modules.data_loader import (
    load_dataframe,
    build_documents,
    build_search_documents
)

from modules.text_preprocessing import clean_and_stem
# ----------------------------
# Load Dataset and build documents (centralized in data_loader.py)
#   documents        -> unchanged display/LLM-context documents
#   search_documents -> field-weighted, used only for BM25 indexing
# See bm25_search.py / data_loader.build_search_documents() for the
# full rationale on why structured fields are weighted.
# ----------------------------
df = load_dataframe()
documents = build_documents(df)
search_documents = build_search_documents(df)

# ----------------------------
# Load Model & FAISS
# (unchanged -- FAISS/embedding retrieval was already performing well)
# ----------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")

index = faiss.read_index("vector_db/cricket_index.faiss")

# ----------------------------
# BM25
# Tokenize with the shared clean_and_stem() pipeline (lowercasing,
# punctuation stripping, stemming) instead of a naive .lower().split().
# This is applied to search_documents (field-weighted), not `documents`,
# so the text shown to the user / passed to the LLM is untouched.
# ----------------------------
tokenized_docs = [clean_and_stem(doc) for doc in search_documents]
bm25 = BM25Okapi(tokenized_docs)


# ----------------------------
# Reciprocal Rank Fusion
# (unchanged -- this implementation is mathematically correct; the
# ranking problems were coming entirely from BM25 input quality, not RRF)
# ----------------------------
def reciprocal_rank_fusion(result_lists, k=60):

    scores = {}

    for results in result_lists:

        for rank, doc_id in enumerate(results):

            scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank + 1)

    ranked = sorted(scores.items(),
                    key=lambda x: x[1],
                    reverse=True)

    return [doc for doc, _ in ranked]


# ----------------------------
# Hybrid Search Function
# ----------------------------
def hybrid_search(query):

    # Semantic Search (unchanged)
    query_embedding = model.encode([query])

    _, semantic_indices = index.search(query_embedding, 5)

    semantic_results = semantic_indices[0].tolist()

    # BM25 Search -- query MUST use the same clean_and_stem() pipeline
    # as the documents, or stemmed document tokens (e.g. "bowler") will
    # never match an unstemmed query token (e.g. "bowlers").
    query_tokens = clean_and_stem(query)

    scores = bm25.get_scores(query_tokens)

    bm25_results = np.argsort(scores)[::-1][:5].tolist()

    # Hybrid Search (unchanged -- RRF logic was already correct)
    hybrid_results = reciprocal_rank_fusion(
        [semantic_results, bm25_results]
    )

    return semantic_results, bm25_results, hybrid_results, documents


# ----------------------------
# Run only if executed directly
# ----------------------------
if __name__ == "__main__":

    query = input("Enter your search query: ")

    semantic, bm25_ranked, hybrid, documents = hybrid_search(query)

    print("\n=========== HYBRID SEARCH RESULTS ===========\n")

    for rank, idx in enumerate(hybrid[:5], start=1):
        print(f"Result {rank}")
        print(documents[idx])
        print("-" * 60)