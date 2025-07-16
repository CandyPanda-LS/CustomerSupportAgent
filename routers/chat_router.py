from fastapi import APIRouter

from schemas.chat import ChatRequest, ChatResponse
from services.chat_service import ChatService

router = APIRouter()
chat_service = ChatService()


@router.post(
    "/generate/llm/openAi",
    tags=["Customer support agent"],
    description="Flight agent that can answer questions about flights, hotels, and car rentals using OpenAI's chat model.",
)
def generate(request: ChatRequest) -> ChatResponse:
    response_content = chat_service.generate_response(request)
    return ChatResponse(response=response_content)
