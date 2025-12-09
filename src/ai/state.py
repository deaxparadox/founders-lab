from typing import Annotated

from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class State(TypedDict):
    messages: Annotated[list, add_messages]
    user_query: str
    router_response: dict
    final_response: str
    chat_id: str
    
    
class StateStructured(TypedDict):
    messages: Annotated[list, add_messages]
    user_query: str
    step: str
    final_response: str
    chat_id: str