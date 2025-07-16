from fastapi import FastAPI

from routers import chat_router

app = FastAPI(
    title="Customer Support Agent API",
    description="An API for a customer support agent that can answer questions about flights, hotels, and car rentals.",
    version="1.0.0",
)

app.include_router(chat_router.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

# [
#     "Hi there, what time is my flight?",
#     "Am i allowed to update my flight to something sooner? I want to leave later today.",
#     "Update my flight to sometime next week then",
#     "The next available option is great",
#     "what about lodging and transportation?",
#     "Yeah i think i'd like an affordable hotel for my week-long stay (7 days). And I'll want to rent a car.",
#     "OK could you place a reservation for your recommended hotel? It sounds nice.",
#     "yes go ahead and book anything that's moderate expense and has availability.",
#     "Now for a car, what are my options?",
#     "Awesome let's just get the cheapest option. Go ahead and book for 7 days"
# ]