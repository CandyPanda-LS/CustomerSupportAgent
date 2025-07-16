from pydantic import BaseModel


class ChatRequest(BaseModel):
    query: str
    passenger_id: str = "4765 014996"


class ChatResponse(BaseModel):
    response: str
