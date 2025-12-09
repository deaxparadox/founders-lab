import ast
import json
from json_repair import repair_json
import re


async def normalize_json_response(response_str):
    """
    Checks if the given string is valid JSON.
    If not, attempts to correct common issues such as:
    - Single quotes instead of double quotes
    - Python dict-style strings
    Returns a valid JSON string or raises an error if irrecoverable.
    """
    # If already a dict (not a string), just convert to JSON
    # if isinstance(response_str, dict):
    #     return json.dumps(response_str)

    # # Try loading as valid JSON directly
    # try:
    #     json.loads(response_str)
    #     return response_str  # Already valid JSON
    # except json.JSONDecodeError:
    #     pass

    # # Try parsing Python-style dict using ast.literal_eval safely
    # try:
    #     python_obj = ast.literal_eval(response_str)
    #     if isinstance(python_obj, dict):
    #         return json.dumps(python_obj)
    # except Exception:
    #     pass

    # # Try simple replacements if still invalid
    # try:
    #     fixed = (
    #         response_str
    #         .replace("'", '"')
    #         .replace('None', 'null')
    #         .replace('True', 'true')
    #         .replace('False', 'false')
    #     )
    #     json.loads(fixed)  # Test validity
    #     return fixed
    # except json.JSONDecodeError as e:
    #     raise ValueError(f"Could not normalize response to valid JSON: {e}")
    return repair_json(response_str)