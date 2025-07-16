import os

from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from embeddings.open_ai_embedding import get_openai_embeddings

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
pc = Pinecone(api_key=PINECONE_API_KEY)

index_name = "pinecone-chatbot"
index = pc.Index(index_name)

def get_pinecone_vector_db():
    embeddings = get_openai_embeddings()
    return PineconeVectorStore(index=index, embedding=embeddings)