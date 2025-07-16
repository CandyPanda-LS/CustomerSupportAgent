from datetime import datetime
import uuid

from fastapi import FastAPI
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import START
from langgraph.graph import StateGraph
from langgraph.prebuilt import tools_condition

from constants.prompts import CUSTOMER_SUPPORT_AGENT_SYSTEM_PROMPT
from models.chat_models.chat_openai import get_openai_chat
from tools.car_rental_tools import search_car_rentals, book_car_rental, update_car_rental, cancel_car_rental
from tools.ddg_search_tool import ddg_search
from tools.flight_tools import search_flights, fetch_user_flight_information, cancel_ticket, update_ticket_to_new_flight
from tools.hotel_tools import search_hotels, book_hotel, update_hotel, cancel_hotel
from tools.policy_tool import lookup_policy
from utils.Assistant import Assistant
from utils.State import State
from utils.utils import create_tool_node_with_fallback

app = FastAPI(
    title="Customer Support Agent API",
    description="An API for a customer support agent that can answer questions about flights, hotels, and car rentals.",
    version="1.0.0",
)

@app.post(
    path="/generate/llm/openAi",
    tags=["Customer support agent"],
    description="Flight agent that can answer questions about flights, hotels, and car rentals using OpenAI's chat model.",
)
def generate(query: str, passenger_id:str = "4765 014996") -> str:
    tools = [
        ddg_search,
        fetch_user_flight_information,
        search_flights, update_ticket_to_new_flight, cancel_ticket,
        lookup_policy,
        search_car_rentals, book_car_rental, update_car_rental, cancel_car_rental,
        search_hotels, book_hotel, update_hotel, cancel_hotel
    ]
    llm = get_openai_chat()

    primary_assistant_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                CUSTOMER_SUPPORT_AGENT_SYSTEM_PROMPT,
            ),
            ("placeholder", "{messages}"),
        ]
    ).partial(time=datetime.now)
    assistant_runnable = primary_assistant_prompt | llm.bind_tools(tools)

    builder = StateGraph(State)

    builder.add_node("assistant", Assistant(assistant_runnable))
    builder.add_node("tools", create_tool_node_with_fallback(tools))
    builder.add_edge(START, "assistant")
    builder.add_conditional_edges(
        "assistant",
        tools_condition,
    )
    builder.add_edge("tools", "assistant")

    memory = MemorySaver()
    agent_graph = builder.compile(checkpointer=memory)
    thread_id = str(uuid.uuid4())

    config = {
        "configurable": {

            "passenger_id": "4765 014996",
            "thread_id": thread_id,
        }
    }

    final_state = agent_graph.invoke(
        {"messages": ("user", query)},
        config=config,
    )

    print("\n\n-- VERBOSE EXECUTION LOG --\n")
    if final_state and "messages" in final_state:
        for message in final_state["messages"]:
            print(message.pretty_repr())
    print("\n-- END OF LOG --\n\n")

    final_response = final_state['messages'][-1] if final_state['messages'] else None

    if isinstance(final_response, AIMessage):
        return final_response.content
    else:
        return "An error occurred, and no final response was generated."


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
