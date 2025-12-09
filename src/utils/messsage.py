import json
from typing import Literal

from langchain.schema.messages import AIMessage, HumanMessage, SystemMessage


async def extract_last_qa(messages):
    """
    messages: list of SystemMessage, HumanMessage, AIMessage
    Returns: list of [SystemMessage, last HumanMessage, last AIMessage]
    """
    # system_msgs = [m for m in messages if isinstance(m, SystemMessage)]
    human_msgs = [m for m in messages if isinstance(m, HumanMessage)]
    ai_msgs = [m for m in messages if isinstance(m, AIMessage)]

    last_human = human_msgs[-1] if human_msgs else None
    last_ai = ai_msgs[-1] if ai_msgs else None

    result = []
    # result.extend(system_msgs)
    if last_human:
        result.append(last_human)
    if last_ai:
        result.append(last_ai)
    return result


async def get_all_messages(messages: dict, ai_msg_json_format: bool = False):
    messages = messages['channel_values']['messages']
    
    history: list[dict[Literal['user', 'agent'], str]] = []
    for citem in messages:
        if isinstance(citem, HumanMessage):
            history.append({"user": citem.content})
        
        if isinstance(citem, AIMessage):
            if ai_msg_json_format:
                citem = citem.content.replace("```json", "").replace("```", "")
                # citem = json.loads(citem)
                history.append({"agent": citem})
            else:
                history.append({"agent": citem.content})
    
    return history