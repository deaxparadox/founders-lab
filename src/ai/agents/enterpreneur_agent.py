import json
from traceback import format_exc
from typing import Annotated

from ai import graphs
from ai.prompts.entrepreneur_roadmap_prompt import (
    cofounder_agent_prompt,
    cofounder_agent_client_prompt
)


async def entrepreneur_agent(
    user_input: str, 
    chat_id: str, 
    /, 
    system_prompt: str = cofounder_agent_client_prompt
):

    message_state = {
        "messages": [
            # {"role": "system", "content": system_prompt}, 
            # {"role": "user", "content": user_input}
        ],
        "user_query": user_input,
        "chat_id": chat_id
    }
    
    
    response: str = ""
    async for mode, chunk in graphs.entrepreneur_graph.astream(
        message_state,
        {"configurable": {"thread_id": chat_id}},
        stream_mode=["updates"]
    ):
        # response += chunk[0].content
        # for value in event.values():
        #     print(value)
            # print("Assistant:", value["messages"].content)
            
        # print(f"\n{chunk}")
        if mode == "updates":
            if "entrepreneur_overview_agent" in chunk:
                response = chunk["entrepreneur_overview_agent"]['messages'][0]['content']
            
            if "enrich_roadmap_with_resources" in chunk:
                response = chunk["enrich_roadmap_with_resources"]['messages'][0]['content']
            
            if "entrepreneur_ideation_agent" in chunk:
                response = chunk["entrepreneur_ideation_agent"]['messages'][0]['content']
                
            if "image_generation_agent" in chunk:
                response = chunk["image_generation_agent"]['messages'][0]['content']
    try:
        # print(response)
        response = response.replace('```json', "").replace("```", "")
        # print("Stream Response:", {"response"})
        response = json.loads(response)
    except Exception as e:
        print(format_exc())
        # print("error response", response)
        pass
            
    return response