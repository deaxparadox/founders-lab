import logging
from typing import (
    Optional, 
    overload, 
    Union
)

import aiohttp
from django.conf import settings


logger = logging.getLogger('ai')


async def search_place(place: Optional[str] = None) -> Union[dict, str]:
    if not place:
        return {}
        
    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": f"{settings.GOOGLE_API_KEY}",
        "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress"
    }
    payload = {
        "textQuery": place
    }

    data: dict = {}

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            data = await response.json()
        
    logger.debug("Searched places: {}".format(data))
        
    if places := data.get("places"):
        return places[0]['id']
            
    return data


async def get_place_details(place_id: str) -> dict:
    url = f"https://places.googleapis.com/v1/places/{place_id}"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": f"{settings.GOOGLE_API_KEY}",
        "X-Goog-FieldMask": "id,displayName,formattedAddress,rating,userRatingCount,reviews,websiteUri"
    }

    data: dict = None
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            data = await response.json()
            
    logger.debug("Place detail: {}".format(data))
    
    return data