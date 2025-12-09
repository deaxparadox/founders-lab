import asyncio
import json
import logging
from typing import (
    Annotated, 
    Any, 
    Literal, 
    List, 
    Dict
)

from langgraph.graph import END, StateGraph, START
from langgraph.graph.state import CompiledStateGraph

from ai.state import State
from ai.llm.openai import openai_llm_chat, ideation_llm_chat
from ai.prompts.entrepreneur_ideation_prompt import (
    cofounder_ideation_agent_prompt, 
    # cofounder_ideation_agent_prompt_v2, 
    # cofounder_ideation_agent_prompt_v3
)
from ai.prompts.enterpreneur_overview_agent import overview_agent_prompt
from ai.prompts.entrepreneur_roadmap_prompt import cofounder_roadmap_prompt
from ai.prompts.entrepreneur_router_prompt import entrepreneur_router_prompt
from ai.prompts.enterpreneur_get_step_resources import get_resources_for_step_prompt
from ai.prompts.enterpreneur_image_agent_prompt import image_generation_prompt
from ai.publisher import log_route_event
from ai.tokens import total_tokens
from ai.tools.image_generation import image_gen
from services.langgraph.db import Saver
from utils.json import normalize_json_response
from services.pinecone import query_pinecone


logger = logging.getLogger("ai")


async def get_messages_history(messages: list[dict], limit: int = 10) -> list[dict]:
    """
    Get the history from input messages
    by default get 10 messages
    
    Args:
        messages: List of messages
        limit: default history length
        
    Returns: History (list of dict)
    """
    return messages[-limit:]


async def remove_language_annotation(response: str, language: Literal['json']) -> str:
    """
    Remove the language annotation from llm response.
    
    Args:
        response: Respones from llm
        language: default to json annotation
    
    Returns: Removed string without annotation.
    """
    return response.replace("```json", "").replace("```", "")


async def user_query_node(state: State):
    chat_id = state['chat_id']
    await log_route_event(chat_id, "User query", "Saving user query")
    return {"messages": [{"role": "user", "content": state['user_query']}]}
    

async def entrepreneur_router_agent(state: State):
    logger.debug("1111111111111111111111111111111")
    user_query = state['user_query']
    chat_id = state['chat_id']
    
    await log_route_event(chat_id, "router_agent", "Router: Analyzing user query")
    
    logger.info(f"User query: {user_query}")
    logger.debug(f"Message history: {state['messages']}")
    
    router_prompt = await entrepreneur_router_prompt()
    history = await get_messages_history(state['messages'])
    messages = [
        {"role": "system", "content": router_prompt},
        *history,
        {"role": "user", "content": user_query}
    ]
    
    response = await openai_llm_chat.ainvoke(messages, config={'configurable': {"thread_id": chat_id}}, stream=False)
    
    tokens = response.response_metadata.get('token_usage').get('total_tokens')
    await total_tokens.add(tokens)
    
    response_content = response.content
    response_content_string = await remove_language_annotation(response_content, language="json")
    response = json.loads(response_content_string)
    logger.info(f"Router agent response: {response}")
    state["router_response"] = response
    recommended_node = state['router_response']
    
    await log_route_event(chat_id, "router_agent", f"Router: Routing to {recommended_node}")
    return state


async def entrepneur_conditional_node(state: State):
    logger.debug("2222222222222222222222222222222222")
    router_response = state['router_response']
    next_node = router_response['recommended_node']
    logger.info(f"Conditional agent response:, {next_node}")
    return next_node
    
    
async def entrepreneur_chat_node(state: State):
    messages = await openai_llm_chat.ainvoke(state['messages'])
    return {"messages": messages}


async def entrepreneur_roadmap_agent(state: State):
    logger.debug("333333333333333333333333333333333333333")
    user_query = state['user_query']
    chat_id = state["chat_id"]
    
    await log_route_event(chat_id, "roadmap_agent", f"Roadmap: Understanding and getting details for building roadmap...")
    
    cofounder_prompt = await cofounder_roadmap_prompt()
    messages = [
        {"role": "system", "content": cofounder_prompt},
        {"role": "user", "content": user_query}
    ]
    
    response = await openai_llm_chat.ainvoke(messages, config={'configurable': {"thread_id": chat_id}})
    logger.debug("Roadmap raw repsones: {}".format(response))
    response_content = response.content
    response_content_string = await remove_language_annotation(response_content, language="json")
    logger.debug("Roadmap repsones error: {}".format(response_content_string))
    response_content_string = await normalize_json_response(response_content_string)
    response = json.loads(response_content_string)
    logger.info(f"Roadmap agent response: {response}")
    state["final_response"] = response
    
    await log_route_event(chat_id, "roadmap_agent", f"Roadmap: Generated roadmap...")
    return state

    
async def entrepreneur_ideation_agent(state: State):
    logger.debug("44444444444444444444444444444444444444444")
    user_query = state['user_query']
    chat_id = state["chat_id"]
    
    await log_route_event(chat_id, "ideation_agent", f"Ideation: Understanding user query...")
    
    history = await get_messages_history(state['messages'])
    system_prompt = cofounder_ideation_agent_prompt
    # system_prompt = await cofounder_ideation_agent_prompt_v3()
    messages = [
        {"role": "system", "content": system_prompt},
        *history,
        {"role": "user", "content": user_query}
    ]
    
    response = await ideation_llm_chat.ainvoke({'messages': messages}, config={'configurable': {"thread_id": chat_id}})
    logger.info("Raw ideation respones: {}".format(response))
    response_content = response['messages'][-1].content
    logger.info(f"Ideation agent content:, {response_content}, {type(response_content)}")
    response_content_string = await remove_language_annotation(response_content, language="json")
    # response_content_string = await normalize_json_response(response_content_string)
    # response = json.loads(response_content_string)
    logger.info(f"Ideation agent response: {response}")
    state["final_response"] = response_content_string
    
    await log_route_event(chat_id, "ideation_agent", f"Ideation: Forming final response...")
    return {
        "messages": [{
            "role": "assistant", "content": response_content_string
        }]
    }
    
    
async def image_gen_agent(state: State) -> Dict[str, Any]:
    # prompt = await image_generation_prompt()
    user_query = state['user_query']
    logo = await image_gen(user_query)
    logger.info("Image generation response: {}".format(logo))
    return {
        "messages": [{
            "role": "assistant", "content": json.dumps(logo)
        }]
    }
    

async def entrepreneur_overview_agent(state: State):
    logger.debug("55555555555555555555555555555555555555555")
    user_query = state['user_query']
    chat_id = state["chat_id"]
    final_response = state['final_response']
    
    await log_route_event(chat_id, "overview_agent", f"Overview: Understanding user query...")
    
    cofounder_overview_prompt = await overview_agent_prompt(final_response)
    history = await get_messages_history(state['messages'])
    messages = [
        {"role": "system", "content": cofounder_overview_prompt},
        # *history,
        {"role": "user", "content": user_query}
    ]
    
    response = await openai_llm_chat.ainvoke(messages, config={'configurable': {"thread_id": chat_id}})
    logger.debug("Overview raw repsones: {}".format(response))
    response_content = response.content
    response_content_string = await remove_language_annotation(response_content, language="json")
    response_content_string = await normalize_json_response(response_content_string)
    logger.debug("Overview repsones error: {}".format(response_content_string))
    response = json.loads(response_content_string)
    logger.info(f"Overview agent response: {response}")
    state["final_response"] = response
    
    await log_route_event(chat_id, "overview_agent", f"Overview: Forming final response...")
    
    return {
        "messages": [
            {"role": "assistant", "content": response_content_string}
        ]
    }


async def enrich_roadmap_with_resources(state: State) -> List[Dict]:
    """
    For each roadmap step, query the RAG source database and attach top matching resources.
    """
    final_response = state['final_response']
    if final_response['type'] == "entrepreneurial_response":
        roadmap_steps = final_response['data']['roadmap']
        enriched_steps = []
        for step in roadmap_steps:
            logger.info(f"Query resources for step: {step}")
            query_text = f"{step['title']} {step['description']} {' '.join(step.get('objectives', []))}"
            resources = await query_pinecone(query_text)
            resources_for_step_prompt = await get_resources_for_step_prompt(step, resources)
            
            raw_response = await openai_llm_chat.ainvoke([{"role": "user", "content": resources_for_step_prompt}])
            logger.debug("Enrich roadmap raw repsones: {}".format(raw_response))
            response_content = raw_response.content
            response_content_string = await remove_language_annotation(response_content, language="json")
            response_content_string = await normalize_json_response(response_content_string)
            logger.debug("Enrich roadmap repsones error: {}".format(response_content_string))
            response = json.loads(response_content_string)
            logger.info(f"Enrich roadmap agent response: {response}")
            
            logger.info(f"Response for step: {response}")
            step['resources'] = [
                {"title": r['title'], "url": r['url']}
                for r in response
            ]
            # enriched_steps.append(step)
            # break
    return {
        "messages": [
            {"role": "assistant", "content": json.dumps(final_response)}
        ]
    }


async def entrepreneur_graph_builder() -> CompiledStateGraph:
    graph = StateGraph(State)
    graph.add_node("user_query_node", user_query_node)
    graph.add_node("entrepreneur_chat_node", entrepreneur_chat_node)
    graph.add_node("entrepreneur_router_agent", entrepreneur_router_agent)
    graph.add_node("entrepreneur_roadmap_agent", entrepreneur_roadmap_agent)
    graph.add_node("entrepreneur_ideation_agent", entrepreneur_ideation_agent)
    graph.add_node("entrepreneur_overview_agent", entrepreneur_overview_agent)
    graph.add_node("enrich_roadmap_with_resources", enrich_roadmap_with_resources)
    graph.add_node("image_generation_agent", image_gen_agent)
    
    graph.add_edge(START, "user_query_node")
    graph.add_edge("user_query_node", "entrepreneur_router_agent")
    graph.add_conditional_edges("entrepreneur_router_agent", entrepneur_conditional_node)
    # ideation
    graph.add_edge("entrepreneur_ideation_agent", END)
    # roadmap
    graph.add_edge("entrepreneur_roadmap_agent", "enrich_roadmap_with_resources")
    graph.add_edge("enrich_roadmap_with_resources", END)
    # Image generation
    graph.add_edge("image_generation_agent", END)
    # END
    graph.add_edge("entrepreneur_overview_agent", END)
    
    return graph.compile(checkpointer=Saver.saver)

