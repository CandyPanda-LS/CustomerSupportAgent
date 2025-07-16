import os

from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI
load_dotenv()

MISTRAL_MODEL_NAME = os.getenv("MISTRAL_MODEL_NAME")
MISTRAL_MODEL_TEMPERATURE = os.getenv("MISTRAL_MODEL_TEMPERATURE")
MISTRAL_MODEL_ENDPOINT = os.getenv("MISTRAL_MODEL_ENDPOINT")
MISTRAL_MODEL_MAX_TOKENS = os.getenv("MISTRAL_MODEL_MAX_TOKENS")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")


def get_mistral_chat():
    return ChatMistralAI(
        model= MISTRAL_MODEL_NAME,
        mistral_api_key= MISTRAL_API_KEY,
        temperature=float(MISTRAL_MODEL_TEMPERATURE),
        endpoint=MISTRAL_MODEL_ENDPOINT,
        max_retries=2,
        max_tokens=int(MISTRAL_MODEL_MAX_TOKENS),
        verbose=True
    )