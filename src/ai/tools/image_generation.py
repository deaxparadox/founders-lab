import os
import base64
import logging
from typing import Dict, Any, List

from openai.types.images_response import ImagesResponse, Image

from ai.llm.openai import image_client


logger = logging.getLogger("ai")

async def image_gen(prompt: str, n: int = 1, size: str = "1024x1024", response_format: str = "url") -> Dict[str, Any]:
    """
    Wrapper around OpenAI image generation.
    Returns a dict with 'type': 'image_response', 'count', 'logos': [{url, description}]
    - If the API returns URLs, use them.
    - If the API returns base64, convert to data URL (png).
    """
    resp: ImagesResponse = await image_client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        n=n,
        size=size,
        response_format=response_format
    )
    logger.info("Image generation raw respone: {}".format(response_format))

    logo = resp.data[-1].url

    return {
        "type": "image_response",
        "logo": logo
    }