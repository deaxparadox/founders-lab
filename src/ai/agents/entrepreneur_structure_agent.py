import json
from traceback import format_exc
from typing import Annotated

from ai import graphs

async def entrepreneur_structured_agent(
    user_input: str, 
    chat_id: str, 
    step: str,
    /, 
):

    message_state = {
        "messages": [
        ],
        "user_query": user_input,
        "chat_id": chat_id,
        "step": step
    }
    
    
    response: str = ""
    async for mode, chunk in graphs.entrepreneur_structured_graph.astream(
        message_state,
        {"configurable": {"thread_id": chat_id}},
        stream_mode=["updates"]
    ):
        
        if mode == "updates":
            if "entrepreneur_step_1" in chunk:
                print(chunk, type(chunk))
                # response = chunk["entrepreneur_step_1"]['messages'].content
                response = chunk["entrepreneur_step_1"]['messages'][0].content
    
            if "entrepreneur_step_2" in chunk:
                response = chunk["entrepreneur_step_2"]['messages'][0].content
            
            if "entrepreneur_step_3" in chunk:
                response = chunk["entrepreneur_step_3"]['messages'][0].content
            
            if "entrepreneur_step_4" in chunk:
                response = chunk["entrepreneur_step_4"]['messages'][0].content
            
            if "entrepreneur_step_5" in chunk:
                response = chunk["entrepreneur_step_5"]['messages'][0].content
                
            if "entrepreneur_step_6" in chunk:
                response = chunk["entrepreneur_step_6"]['messages'][0].content
                
            if "entrepreneur_step_7" in chunk:
                response = chunk["entrepreneur_step_7"]['messages'][0].content
    
    return {
        "step": step,
        "response": response
    }
    # return response