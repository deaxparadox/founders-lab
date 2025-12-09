import logging

from langchain.tools import tool

from services.pinecone import query_pinecone


logger = logging.getLogger("ai")


@tool
async def query_pinecone_tool(question: str | None = None):
    """
    Use this tool to retrieve external resources, examples, supporting data,
    market validation, and reference material from Pinecone. Always call this
    tool before producing a roadmap to enrich the output with relevant resources.
    
    Args:
        question: Question to query the pinecone.
        
    Returns: Data from the pinecone
    """
    
    if not question:
        return "Invalid question"
    
    logger.info("Query pinecone: {}".format(question))
    data = await query_pinecone(question)
    
    logger.debug("Pinecone data: {}".format(data))
    return data