from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

def get_embeddings(text):
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Create embeddings for your documents
    embeddings = embedding_model.embed_documents(text)

    # Create the vector store (this auto-saves now in Chroma >=0.4)
    vector_store = Chroma.from_texts(
        texts=text,
        embedding=embedding_model,
        persist_directory="/content/Chroma_store_job"
    )

