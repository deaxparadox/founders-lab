import base64
from datetime import datetime, timedelta, timezone
import json

from django.conf import settings

from .exceptions import SIDTimeOutException


async def encode_string(data: dict, ttl: int = settings.TTL) -> str:
    """
    Encode the given data, with time-to-live for 5 minutes (default).
    Args:
        data: dict payload
        ttl: 5 mins time-to-live (default)
    Returns:
        A base64 encoded string
    """
    future = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()
    future_data = {
        'expire_at': future,
        **data
    }
    future_json = json.dumps(future_data)
    future_bytes = future_json.encode('utf-8')
    future_base64 = base64.b64encode(future_bytes)
    return future_base64.decode('utf-8')


async def decode_string(encoded_str: str) -> dict:
    """
    Decode the given base64 string, and return the payload
    Args:
        encoded_str: Encode data string
    Returns:
        Return the data payload dict.
    """
    future_bytes = base64.b64decode(encoded_str)
    future_json = future_bytes.decode('utf-8')
    future_data = json.loads(future_json)
    return future_data


async def check_encoded_str_validity(time_str: str, ttl: int = settings.TTL) -> None:
    """
    Take the datetime string in isoformat, check if the 
    """
    dt = datetime.fromisoformat(time_str)
    if datetime.now(timezone.utc) >= (dt + timedelta(minutes=ttl)):
        return SIDTimeOutException("Authentication token expired, please login again on bubble.io")