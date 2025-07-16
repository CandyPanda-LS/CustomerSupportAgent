# vector_db_setup.py
import os
import re
import uuid
from dotenv import load_dotenv
import requests
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, PodSpec
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

load_dotenv()

# Initialize clients
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index_name = "pinecone-chatbot"
index = pc.Index(index_name)
embeddings = OpenAIEmbeddings(
    model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    openai_api_base="https://models.inference.ai.azure.com"
)

def load_faq_data(local_file_path):
    print(f"Loading FAQ data from local file: {local_file_path}...")

    try:
        with open(local_file_path, 'r', encoding='utf-8') as file:
            faq_text = file.read()
        print("Successfully loaded FAQ data from local file")
        return [Document(page_content=txt) for txt in re.split(r"(?=\n##)", faq_text)]
    except FileNotFoundError:
        raise FileNotFoundError(f"The file {local_file_path} was not found")
    except Exception as e:
        raise Exception(f"An error occurred while reading the file: {str(e)}")


def ingest_documents(docs: list[Document], index_name: str = "travel-policies"):
    print("Starting ingestion of documents into Pinecone index...")
    vector_store = PineconeVectorStore(index=index, embedding=embeddings)

    # Add documents with unique IDs
    ids = [str(uuid.uuid4()) for _ in range(len(docs))]
    vector_store.add_documents(documents=docs, ids=ids)

    print(f"Successfully ingested {len(docs)} documents into Pinecone index {index_name}")


def clear_vector_store(index_name: str = "travel-policies"):
    print(f"Clearing all vectors from Pinecone index {index_name}...")
    index = pc.Index(index_name)
    index.delete(delete_all=True)
    print(f"Cleared all vectors from index {index_name}")


if __name__ == "__main__":
    # Example usage:
    # To ingest data:
    faq_docs = load_faq_data("swiss_faq.md")
    ingest_documents(faq_docs)

    # To clear the index:
    # clear_vector_store()