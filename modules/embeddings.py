from sentence_transformers import SentenceTransformer
import pandas as pd
import time


class Embedder:
    """Generate embeddings for cricket player documents"""

    def __init__(self, model_name="all-MiniLM-L6-v2"):

        print(f"Loading embedding model: {model_name}")

        self.model = SentenceTransformer(model_name)

        self.dimensions = self.model.get_sentence_embedding_dimension()

        print(f"Embedding Dimension: {self.dimensions}")

    def embed_documents(self, documents):

        start = time.time()

        embeddings = self.model.encode(
            documents,
            batch_size=32,
            show_progress_bar=True,
            convert_to_numpy=True
        )

        print(f"\nGenerated {len(documents)} embeddings")
        print(f"Time Taken: {time.time()-start:.2f} seconds")

        return embeddings

    def embed_query(self, query):

        return self.model.encode(
            query,
            convert_to_numpy=True
        )


if __name__ == "__main__":

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

    embedder = Embedder()

    embeddings = embedder.embed_documents(documents)

    print("\nEmbedding Shape:", embeddings.shape)
    print("\nFirst Embedding:")
    print(embeddings[0][:10])