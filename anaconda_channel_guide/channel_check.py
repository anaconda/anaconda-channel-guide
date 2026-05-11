import requests

BASE_URL = "http://YOUR_BASE_URL/channels/main-x/artifacts/exists"

def check_package_availability(packages: list[str]) -> dict[str, list[str]]:
    """
    Check if the given packages are available on the main channel.
    """
    response = requests.post(BASE_URL, json={"packages": packages})
    return response.json()