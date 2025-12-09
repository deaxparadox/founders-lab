import asyncio
import os
import json
import urllib.parse

import aiohttp
from dotenv import load_dotenv

load_dotenv(override=True)


async def fetch_filtered_user():
    base_url = os.getenv("BUBBLE_BASE_URL")
    bubble_api_key = os.getenv("BUBBLE_API_KEY")

    constraints = [
        {
            "key": "email",
            "constraint_type": "equals",
            "value": "aakash+freelancer@frondus.com"
        }
    ]
    constraints_param = urllib.parse.quote(json.dumps(constraints))
    url = f"{base_url}/freelancer?constraints={constraints_param}"
    # url = base_url + "/freelancer"

    headers = {
        "Authorization": F"Bearer {bubble_api_key}",
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            print("Status:", response.status)
            data = await response.json()
            print(json.dumps(data, indent=2))

if __name__ == '__main__':
    asyncio.run(fetch_filtered_user())
