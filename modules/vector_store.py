import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
import os

print("Loading dataset...")

# Load dataset
df = pd.read_excel("data/World_Cricketers.xlsx")

# Create documents
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

print(f"Documents Loaded: {len(documents)}")

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

print("Generating embeddings...")

embeddings = model.encode(
    documents,
    convert_to_numpy=True,
    show_progress_bar=True
)

print("Embedding Shape:", embeddings.shape)

# Create FAISS index
dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(dimension)

index.add(np.array(embeddings))

print("\nFAISS Index Created Successfully!")
print("Total Vectors Stored:", index.ntotal)

# Create vector_db folder if it doesn't exist
os.makedirs("vector_db", exist_ok=True)

# Save index
faiss.write_index(index, "vector_db/cricket_index.faiss")

print("\nIndex Saved Successfully!")