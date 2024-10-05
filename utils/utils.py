""" Utils for the project """
from typing import Any
import requests
def is_empty_or_none(data: Any) -> bool:
    """This method returns a boolean when data is empty or None
    receives any type of data
    Args:
        data (Any): _description_
    Returns:
        boolean
    """
    if data is None:
        return True

    if isinstance(data, str) and not str(data).strip():
        return True

    if isinstance(data, (dict, tuple, list)) and not data:
        return True

    return False

def request_service(
    params: dict = None,
    data: dict = None,
    url: str = None,
    method: str = "GET",
    headers: dict = None,
):
    """
    This method is used to request a service
    """
    if is_empty_or_none(headers):
        headers = {}

    if is_empty_or_none(data):
        data = {}

    if is_empty_or_none(params):
        params = {}

    if is_empty_or_none(url):
        return "url is required"

    response = requests.request(
        method=method,
        url=url,
        headers=headers,
        json=data,
        params=params,
        timeout=20,
    )
    return response
