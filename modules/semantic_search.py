import faiss
from sentence_transformers import SentenceTransformer

from data_loader import load_dataframe, build_documents

# Load dataset and build documents (now centralized in data_loader.py)
df = load_dataframe()
documents = build_documents(df)

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Load FAISS index
index = faiss.read_index("vector_db/cricket_index.faiss")

# Ask user for query
query = input("Enter your search query: ")

# Convert query to embedding
query_embedding = model.encode([query])

# Search Top 5
distances, indices = index.search(query_embedding, 5)

print("\nTop 5 Semantic Search Results:\n")

for i, idx in enumerate(indices[0], start=1):
    print(f"Result {i}  (distance: {distances[0][i - 1]:.4f})")
    print(documents[idx])
    print("-" * 60)