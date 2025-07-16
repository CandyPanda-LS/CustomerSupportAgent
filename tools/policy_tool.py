from typing import List

from langchain_core.documents import Document
from langchain_core.tools import tool
from persistance.pinecone_db_config import get_pinecone_vector_db

vector_store = get_pinecone_vector_db()

@tool
def lookup_policy(query: str) -> str:
    """
    Consult the company policies to check whether certain options are permitted.
    Use this before making any flight changes or performing other 'write' events.

    Args:
        query: The policy question or topic to search for
    Returns:
        A string containing the most relevant policy excerpts concatenated together
    """
    try:
        results: List[Document] = vector_store.similarity_search(query=query, k=2)
        policy_excerpts = [doc.page_content for doc in results]
        return "\n\n".join(policy_excerpts)

    except Exception as e:
        return f"Error retrieving policies: {str(e)}"