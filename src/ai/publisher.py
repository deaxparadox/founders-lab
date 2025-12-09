
import json
import redis
import logging
from datetime import datetime, timezone
from typing import Literal

from ai.redis import redis_client, aredis_client

logger = logging.getLogger("ai")


async def log_route_event(session_id, agent: Literal['router_agent', "roadmap_agent", "ideation_agent"], action: str, details: str | None = None):
    """Publish a new event to Redis"""
    message = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent": agent,
        "action": action,
        "details": details,
    }
    logger.info("Publish... demo msg")
    redis_client.publish(f"route_updates:{session_id}", json.dumps(message))



async def alog_route_event(session_id, agent: Literal['router_agent', "roadmap_agent", "ideation_agent"], action: str, details: str | None = None):
    """Publish a new event to Redis"""
    message = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent": agent,
        "action": action,
        "details": details,
    }
    logger.info("Publish... demo msg")
    aredis_client.publish(f"route_updates:{session_id}", json.dumps(message))
