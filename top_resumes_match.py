from langchain_community.embeddings import HuggingFaceEmbeddings
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd

def get_top_matching_resumes(df: pd.DataFrame, jd_text: str, threshold: float = 0.5, top_n: int = 10) -> pd.DataFrame:
    """
    Embeds job description and resumes, computes cosine similarity, and returns top-matching resumes.

    Args:
        df (pd.DataFrame): DataFrame with column 'combined_text' (already prepared).
        jd_text (str): Job description string.
        threshold (float): Minimum similarity threshold to consider.
        top_n (int): Number of top resumes to return.

    Returns:
        pd.DataFrame: Sorted top matching resumes with similarity score.
    """
    # Convert lists/mixed to strings
    df["combined_text"] = df["combined_text"].apply(lambda x: " ".join(x) if isinstance(x, list) else str(x))

    # Load embedding model
    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # Embed JD
    embeddings_job = embedding_model.embed_documents([jd_text])[0]  # single vector
    jd_vector = np.array(embeddings_job).reshape(1, -1)

    # Embed resumes
    embeddings_resumes = embedding_model.embed_documents(df["combined_text"].tolist())
    resume_vectors = np.array(embeddings_resumes)

    # Compute cosine similarity
    similarities = cosine_similarity(jd_vector, resume_vectors)[0]
    df["similarity_score"] = similarities

    # Sort top matches
    top_matches = df[df["similarity_score"] > threshold].sort_values(by="similarity_score", ascending=False)

    return top_matches.head(top_n)
