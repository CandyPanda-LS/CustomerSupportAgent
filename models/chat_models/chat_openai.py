import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME")
OPENAI_MODEL_TEMPERATURE = os.getenv("MISTRAL_MODEL_TEMPERATURE")
OPENAI_MODEL_ENDPOINT = os.getenv("MISTRAL_MODEL_ENDPOINT")
OPENAI_MODEL_MAX_TOKENS = os.getenv("OPENAI_MODEL_MAX_TOKENS")

def get_openai_chat():
    return ChatOpenAI(
    model_name=OPENAI_MODEL_NAME,
    temperature=float(OPENAI_MODEL_TEMPERATURE),
    max_tokens=OPENAI_MODEL_MAX_TOKENS,
    max_retries=2,
    openai_api_key=OPENAI_API_KEY,
    openai_api_base=OPENAI_MODEL_ENDPOINT
)

