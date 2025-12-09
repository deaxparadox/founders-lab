import asyncio
import logging
from pathlib import Path

import aiofiles
from asgiref.sync import sync_to_async
from django.conf import settings
import yaml


logger = logging.getLogger("ai")


TEMPLATE_YAML_PATH = Path(__file__).resolve().parent.joinpath("template.yaml").absolute()


async def load_template_workbook():
    async with aiofiles.open(TEMPLATE_YAML_PATH, 'r') as file:
        data_str = await file.read()
        data = await sync_to_async(yaml.safe_load)(data_str)
        return data