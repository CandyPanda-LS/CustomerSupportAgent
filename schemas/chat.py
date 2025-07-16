from pydantic import BaseModel


class ChatRequest(BaseModel):
    query: str
    passenger_id: str = "3442 587242"
    session_id: str = "64aa1b15-d131-4c24-a340-6b80bd8075d5"


class ChatResponse(BaseModel):
    response: str
