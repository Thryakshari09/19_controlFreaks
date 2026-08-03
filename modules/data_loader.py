"""
data_loader.py

Single source of truth for loading the dataset and building the
display-format document strings. Used by semantic_search.py,
bm25_search.py, and hybrid_pipeline.py so that if the Excel schema
ever changes (e.g. a new column is added), it only needs to be
updated in one place instead of three.

This does NOT change the document format/content in any way --
it's the exact same f-string that was in all three scripts before.
"""

import pandas as pd


def load_dataframe(path: str = "data/World_Cricketers.xlsx") -> pd.DataFrame:
    """Loads the raw cricketer dataset."""
    return pd.read_excel(path)


def build_documents(df: pd.DataFrame) -> list[str]:
    """
    Builds the display/LLM-context document for each row.
    This is the exact same format used across all three scripts --
    unchanged, just centralized.
    """
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
""".strip()

        documents.append(doc)

    return documents


def load_documents(path: str = "data/World_Cricketers.xlsx") -> list[str]:
    """Convenience wrapper: load the dataframe and build documents in one call."""
    df = load_dataframe(path)
    return build_documents(df)


def build_search_documents(df: pd.DataFrame, field_weight: int = 3) -> list[str]:
    """
    Builds the field-weighted document used ONLY for BM25 indexing
    (see bm25_search.py / hybrid_pipeline.py for the full rationale).

    Structured fields (Name, Country, Role, Batting/Bowling Style) are
    repeated `field_weight` times so they outweigh incidental mentions
    of the same words inside long narrative fields (Notable Achievements,
    Background). This is kept separate from build_documents() because it
    must NEVER be shown to the user or passed to the LLM -- it's index-only.
    """
    search_documents = []

    for _, row in df.iterrows():
        weighted_doc = (
            (f"{row['Name']} " * field_weight) +
            (f"{row['Country']} " * field_weight) +
            (f"{row['Role']} " * field_weight) +
            (f"{row['Batting/Bowling Style']} " * field_weight) +
            f"{row['Era']} " +
            f"{row['Notable Achievements']} " +
            f"{row['Background']} "
        )
        search_documents.append(weighted_doc)

    return search_documents