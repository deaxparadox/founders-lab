import json
import logging
from typing import (
    Any,
    Optional
)
import urllib

import aiohttp
from django.conf import settings
from langchain_core.tools import tool


logger = logging.getLogger("ai")


@tool
async def get_bubble_entreprenurs():
    """
    This function fetch the list of entreprenur from "The entrepreneur lab" site.
    """
    URL = f"{settings.BUBBLE_BASE_URL}/entrepreneur"
    HEADERS = {
        "Authorization": f"Bearer {settings.BUBBLE_API_KEY}",
        "Content-Type": "application/json",
    }
    logger.info("Making entrepreneur data request to entrepreneur lab...")
    
    data = None
    async with aiohttp.ClientSession() as session:
        async with session.get(URL, headers=HEADERS) as response:
            logger.info(f"Entrepreneur response status code: {response.status}")
            data = await response.json()
            # logger.debug(f"Response data: {data}")
            
    return data


@tool
async def get_bubble_freelancers(email: Optional[str] = None) -> Any:
    """
    This function fetch the list of freelancer from "The entrepreneur lab" site.
    
    You can use filter also, if required:
    email: use this filter to search freelancer by email
    
    Args:
        email: Email of freelancer to search
    """
    logger.info(f"Freelancer email: {email}")
    
    
    URL = f"{settings.BUBBLE_BASE_URL}/freelancer"
    HEADERS = {
        "Authorization": f"Bearer {settings.BUBBLE_API_KEY}",
        "Content-Type": "application/json",
    }
    logger.info("Making entrepreneur data request to entrepreneur lab...")
    
    if email:
        constraints = [
            {
                "key": "email",
                "constraint_type": "equals",
                "value": email
            }
        ]
        constraints_param = urllib.parse.quote(json.dumps(constraints))
        URL = f"{URL}?constraints={constraints_param}"
    
    
    
    data = None
    async with aiohttp.ClientSession() as session:
        async with session.get(URL, headers=HEADERS) as response:
            logger.info(f"Freelancer response status code: {response.status}")
            data = await response.json()
            logger.debug(f"Response data: {data}")
            
    return data

@tool
async def get_bubble_freelancers_v2(email: Optional[str] = None) -> Any:
    """
    Search The Entrepreneur Lab's internal database of freelancers and professionals.
    
    **WHEN TO USE THIS TOOL:**
    - When user asks to find professionals (lawyers, consultants, advisors, etc.)
    - This is your FIRST choice before searching externally
    - Use this to check if The Entrepreneur Lab has any professionals in their network
    
    **IMPORTANT:** The internal database is small and may not have many results. 
    If this returns empty or no relevant matches, immediately use the Google search 
    tool (search_place_and_rating) to find external professionals.
    
    **SEARCH CAPABILITIES:**
    - Can filter by email if you're looking for a specific person
    - Returns all freelancers/professionals in database if no filter provided
    - Database includes various professionals: lawyers, consultants, advisors, etc.
    
    **TYPICAL WORKFLOW:**
    1. User asks: "Find me a lawyer in Bangalore"
    2. First try: get_bubble_freelancers() to check internal network
    3. If empty/no matches → Immediately use search_place_and_rating for Google search
    4. Present whatever results you find (internal or external)
    
    Args:
        email: (Optional) Email of specific freelancer/professional to search for.
               Leave empty to get all professionals in database.
    
    Returns:
        List of professionals from internal database. May be empty if database 
        has no matches. This is NORMAL for a startup - just move to Google search.
    
    **AFTER CALLING THIS TOOL:**
    - If results found → Present them as "professionals from The Entrepreneur Lab network"
    - If empty → Say "Let me search for professionals in your area..." and call 
      search_place_and_rating immediately
    - DON'T say "no professionals available" - just search externally instead
    """
    logger.info(f"Freelancer email: {email}")
    
    URL = f"{settings.BUBBLE_BASE_URL}/freelancer"
    HEADERS = {
        "Authorization": f"Bearer {settings.BUBBLE_API_KEY}",
        "Content-Type": "application/json",
    }
    logger.info("Making entrepreneur data request to entrepreneur lab...")
    
    if email:
        constraints = [
            {
                "key": "email",
                "constraint_type": "equals",
                "value": email
            }
        ]
        constraints_param = urllib.parse.quote(json.dumps(constraints))
        URL = f"{URL}?constraints={constraints_param}"
    
    data = None
    async with aiohttp.ClientSession() as session:
        async with session.get(URL, headers=HEADERS) as response:
            logger.info(f"Freelancer response status code: {response.status}")
            data = await response.json()
            logger.debug(f"Response data: {data}")
            
    return data