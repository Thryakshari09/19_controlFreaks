import numpy as np
from rank_bm25 import BM25Okapi

from modules.text_preprocessing import clean_and_stem
from data_loader import load_dataframe, build_documents, build_search_documents

# ----------------------------------------------------------------------
# Load dataset and build documents (centralized in data_loader.py)
#   documents        -> unchanged, used for display / downstream LLM answer
#   search_documents -> field-weighted, used ONLY to build the BM25 index
#
# WHY the weighting: raw BM25 term frequency treats every field equally.
# A word like "Pakistan" appearing once in a clean "Country:" field
# carries the same weight as "Pakistan" appearing incidentally inside a
# long narrative "Background"/"Notable Achievements" paragraph (e.g. a
# bowler famous for playing AGAINST Pakistan). Duplicating the short,
# authoritative fields amplifies their term frequency so they dominate
# scoring over incidental narrative mentions -- without touching what's
# displayed to the user. See data_loader.build_search_documents().
# ----------------------------------------------------------------------
df = load_dataframe()
documents = build_documents(df)
search_documents = build_search_documents(df)

# ----------------------------------------------------------------------
# Tokenize documents using the SAME cleaning/stemming pipeline that will
# be applied to the query below. This fixes the singular/plural mismatch
# (e.g. query "bowlers" now matches document token "bowler").
# ----------------------------------------------------------------------
tokenized_docs = [clean_and_stem(doc) for doc in search_documents]

# Build BM25 index
bm25 = BM25Okapi(tokenized_docs)

# ----------------------------------------------------------------------
# User query
# ----------------------------------------------------------------------
query = input("Enter your search query: ")

# Same preprocessing pipeline as documents -- critical for token overlap
query_tokens = clean_and_stem(query)

# Calculate scores
scores = bm25.get_scores(query_tokens)

# Top 5 results (descending score order -- this logic was already correct)
top_indices = np.argsort(scores)[::-1][:5]

print("\nTop 5 BM25 Results:\n")

for rank, idx in enumerate(top_indices, start=1):
    print(f"Result {rank}  (score: {scores[idx]:.4f})")
    print(documents[idx])
    print("-" * 60)