import uuid
from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import START
from langgraph.graph import StateGraph
from langgraph.prebuilt import tools_condition

from models.chat_models.chat_openai import get_openai_chat
from tools.car_rental_tools import search_car_rentals, book_car_rental, update_car_rental, cancel_car_rental
from tools.ddg_search_tool import ddg_search
from tools.flight_tools import search_flights, fetch_user_flight_information, cancel_ticket, update_ticket_to_new_flight
from tools.hotel_tools import search_hotels, book_hotel, update_hotel, cancel_hotel
from tools.policy_tool import lookup_policy
from utils.Assistant import Assistant
from utils.State import State
from utils.utils import _print_event, create_tool_node_with_fallback

tools = [
ddg_search,
fetch_user_flight_information,
search_flights,update_ticket_to_new_flight,cancel_ticket,
lookup_policy,
search_car_rentals,book_car_rental,update_car_rental,cancel_car_rental,
search_hotels,book_hotel,update_hotel,cancel_hotel
]

llm = get_openai_chat()

primary_assistant_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful customer support assistant for Swiss Airlines. "
            " Use the provided tools to search for flights, company policies, and other information to assist the user's queries. "
            " When searching, be persistent. Expand your query bounds if the first search returns no results. "
            " If a search comes up empty, expand your search before giving up."
            "\n\nCurrent user:\n<User>\n{user_info}\n</User>"
            "\nCurrent time: {time}.",
        ),
        ("placeholder", "{messages}"),
    ]
).partial(time=datetime.now)

part_1_assistant_runnable = primary_assistant_prompt | llm.bind_tools(tools)

builder = StateGraph(State)


builder.add_node("assistant", Assistant(part_1_assistant_runnable))
builder.add_node("tools", create_tool_node_with_fallback(tools))
builder.add_edge(START, "assistant")
builder.add_conditional_edges(
    "assistant",
    tools_condition,
)
builder.add_edge("tools", "assistant")

# The checkpointer lets the graph persist its state
# this is a complete memory for the entire graph.
memory = MemorySaver()
part_1_graph = builder.compile(checkpointer=memory)

tutorial_questions = [
    "Hi there, what time is my flight?",
    "Am i allowed to update my flight to something sooner? I want to leave later today.",
    "Update my flight to sometime next week then",
    "The next available option is great",
    # "what about lodging and transportation?",
    # "Yeah i think i'd like an affordable hotel for my week-long stay (7 days). And I'll want to rent a car.",
    # "OK could you place a reservation for your recommended hotel? It sounds nice.",
    # "yes go ahead and book anything that's moderate expense and has availability.",
    # "Now for a car, what are my options?",
    # "Awesome let's just get the cheapest option. Go ahead and book for 7 days"
]

thread_id = str(uuid.uuid4())

config = {
    "configurable": {

        "passenger_id": "4765 014996",
        "thread_id": thread_id,
    }
}


_printed = set()
for question in tutorial_questions:
    events = part_1_graph.stream(
        {"messages": ("user", question)}, config, stream_mode="values"
    )
    for event in events:
        _print_event(event, _printed)