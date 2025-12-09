import json
import logging
from typing import (
    Annotated,
    Any,
    Literal,
    List, 
    Dict
)

from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import END, StateGraph, START
from langgraph.graph.state import CompiledStateGraph

from ai.state import StateStructured
from ai.llm.openai import openai_llm_chat, ideation_llm_chat
from .enterpreneur_graph import (
    get_messages_history,
    remove_language_annotation,
    # user_query_node
)
from ai.prompts.steps.step_1_prompt import cofounder_roadmap_step_1_prompt_v6
from ai.prompts.steps.step_2_prompt import cofounder_roadmap_step_2_prompt_v4
from ai.prompts.steps.step_3_prompt import cofounder_roadmap_step_3_prompt_v2
from ai.prompts.steps.step_4_prompt import cofounder_roadmap_step_4_prompt_v2
from ai.prompts.steps.step_5_prompt import cofounder_roadmap_step_5_prompt_v3
from ai.prompts.steps.step_6_prompt import cofounder_roadmap_step_6_prompt_v3
from ai.prompts.steps.step_7_prompt import cofounder_roadmap_step_7_prompt_v2
from services.langgraph.db import Saver


logger = logging.getLogger("ai")


    
async def create_step_message(
    content: str, 
    step: Literal['entrepreneur_step_1', 'entrepreneur_step_2', 'entrepreneur_step_3', 'entrepreneur_step_4', 'entrepreneur_step_5'], 
    role: Literal['assistant', "user"] = "assistant"
):
    """Create a message with step metadata"""
    if role == "assistant":
        return AIMessage(content=content, metadata={"step": step})
    else:
        return HumanMessage(content=content, metadata={"step": step})
    
    
async def user_query_node(state: StateStructured):
    return {"messages": [await create_step_message(content=state['user_query'], step=state["step"], role="user")]}
    

async def entrepreneur_conditional_node(state: StateStructured):
    # logger.info("State: {}".format(state))
    step = state['step']
    logger.info("Going to step: {}".format(step))
    return step


async def get_query(state: StateStructured, prompt: str, /):
    user_query = state['user_query']
    messages = state['messages']
    if len(messages) > 1 and (messages[-2].metadata['step'] != state['step']):
        logger.info(f"First message in {state['step']}")
        query = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_query}
        ]
    elif len(messages) == 1:
        logger.info(f"First message in step {state['step']}")
        query = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_query}
        ]
    else:
        logger.info(f"Not the first message in {state['step']}")
        query = [
            {"role": "system", "content": prompt},
            *messages,
            {"role": "user", "content": user_query}
        ]
        
    return query
    

async def entrepreneur_step_1(state: StateStructured):
    user_query = state['user_query']
    messages = state['messages']
    chat_id = state['chat_id']
    
    step_1_prompt = await cofounder_roadmap_step_1_prompt_v6()
        
    query = await get_query(state, step_1_prompt)
    
    response = await ideation_llm_chat.ainvoke(
        {"messages": query},
        config={"configurable": {'thread_id': chat_id}}
    )
    response_content = response['messages'][-1].content
    response_content_string = await remove_language_annotation(response_content, language="json")
    logger.info("Step 1 output: {}".format(response_content))
    state['final_response'] = response_content_string
    
    return {
        "messages": [await create_step_message(content=response_content_string, step=state["step"], role="assistant")]
    }
    
    
async def entrepreneur_step_2(state: StateStructured):
    user_query = state['user_query']
    messages = state['messages']
    chat_id = state['chat_id']
    
    step_1_prompt = await cofounder_roadmap_step_2_prompt_v4()
      
    query = await get_query(state, step_1_prompt)
    
    response = await ideation_llm_chat.ainvoke(
        {"messages": query},
        config={"configurable": {'thread_id': chat_id}}
    )
    response_content = response['messages'][-1].content
    response_content_string = await remove_language_annotation(response_content, language="json")
    logger.info("Step 2 output: {}".format(response_content))
    state['final_response'] = response_content_string
    
    return {
        "messages": [await create_step_message(content=response_content_string, step=state["step"], role="assistant")]
    }
    
async def entrepreneur_step_3(state: StateStructured):
    user_query = state['user_query']
    messages = state['messages']
    chat_id = state['chat_id']
    
    step_1_prompt = await cofounder_roadmap_step_3_prompt_v2()    
    
    query = await get_query(state, step_1_prompt)
    
    
    response = await ideation_llm_chat.ainvoke(
        {"messages": query},
        config={"configurable": {'thread_id': chat_id}}
    )
    response_content = response['messages'][-1].content
    response_content_string = await remove_language_annotation(response_content, language="json")
    logger.info("Step 3 output: {}".format(response_content))
    state['final_response'] = response_content_string
    
    return {
        "messages": [await create_step_message(content=response_content_string, step=state["step"], role="assistant")]
    }
    

async def entrepreneur_step_4(state: StateStructured):
    user_query = state['user_query']
    messages = state['messages']
    chat_id = state['chat_id']
    
    step_1_prompt = await cofounder_roadmap_step_4_prompt_v2()
    
    query = await get_query(state, step_1_prompt)
    
    
    
    response = await ideation_llm_chat.ainvoke(
        {"messages": query},
        config={"configurable": {'thread_id': chat_id}}
    )
    response_content = response['messages'][-1].content
    response_content_string = await remove_language_annotation(response_content, language="json")
    logger.info("Step 4 output: {}".format(response_content))
    state['final_response'] = response_content_string
    
    return {
        "messages": [await create_step_message(content=response_content_string, step=state["step"], role="assistant")]
    }
    


async def entrepreneur_step_5(state: StateStructured):
    user_query = state['user_query']
    messages = state['messages']
    chat_id = state['chat_id']
    
    step_1_prompt = await cofounder_roadmap_step_5_prompt_v3()
    
    query = await get_query(state, step_1_prompt)
    
    
    response = await ideation_llm_chat.ainvoke(
        {"messages": query},
        config={"configurable": {'thread_id': chat_id}}
    )
    response_content = response['messages'][-1].content
    response_content_string = await remove_language_annotation(response_content, language="json")
    logger.info("Step 5 output: {}".format(response_content))
    state['final_response'] = response_content_string
    
    return {
        "messages": [await create_step_message(content=response_content_string, step=state["step"], role="assistant")]
    }


async def entrepreneur_step_6(state: StateStructured):
    user_query = state['user_query']
    messages = state['messages']
    chat_id = state['chat_id']
    
    step_1_prompt = await cofounder_roadmap_step_6_prompt_v3()
    
    query = await get_query(state, step_1_prompt)
    
    
    response = await ideation_llm_chat.ainvoke(
        {"messages": query},
        config={"configurable": {'thread_id': chat_id}}
    )
    response_content = response['messages'][-1].content
    response_content_string = await remove_language_annotation(response_content, language="json")
    logger.info("Step 6 output: {}".format(response_content))
    state['final_response'] = response_content_string
    
    return {
        "messages": [await create_step_message(content=response_content_string, step=state["step"], role="assistant")]
    }
    
    
async def entrepreneur_step_7(state: StateStructured):
    user_query = state['user_query']
    messages = state['messages']
    chat_id = state['chat_id']
    
    step_1_prompt = await cofounder_roadmap_step_7_prompt_v2()
    
    query = await get_query(state, step_1_prompt)
    
    
    response = await ideation_llm_chat.ainvoke(
        {"messages": query},
        config={"configurable": {'thread_id': chat_id}}
    )
    response_content = response['messages'][-1].content
    response_content_string = await remove_language_annotation(response_content, language="json")
    logger.info("Step 7 output: {}".format(response_content))
    state['final_response'] = response_content_string
    
    return {
        "messages": [await create_step_message(content=response_content_string, step=state["step"], role="assistant")]
    }
    
    
async def entrepreneur_structured_graph_builder() -> CompiledStateGraph:
    graph = StateGraph(StateStructured)
    graph.add_node("user_query_node", user_query_node)
    # graph.add_node("entrepreneur_conditional_node", entrepreneur_conditional_node)
    graph.add_node("entrepreneur_step_1", entrepreneur_step_1)
    graph.add_node("entrepreneur_step_2", entrepreneur_step_2)
    graph.add_node("entrepreneur_step_3", entrepreneur_step_3)
    graph.add_node("entrepreneur_step_4", entrepreneur_step_4)
    graph.add_node("entrepreneur_step_5", entrepreneur_step_5)
    graph.add_node("entrepreneur_step_6", entrepreneur_step_6)
    graph.add_node("entrepreneur_step_7", entrepreneur_step_7)
    
    graph.add_edge(START, "user_query_node")
    # graph.add_edge("user_query_node", "entrepreneur_conditional_node")
    
    graph.add_conditional_edges("user_query_node", entrepreneur_conditional_node)
    
    graph.add_edge("entrepreneur_step_1", END)
    graph.add_edge("entrepreneur_step_2", END)
    graph.add_edge("entrepreneur_step_3", END)
    graph.add_edge("entrepreneur_step_4", END)
    graph.add_edge("entrepreneur_step_5", END)
    graph.add_edge("entrepreneur_step_6", END)
    graph.add_edge("entrepreneur_step_7", END)
    
    return graph.compile(checkpointer=Saver.saver)
