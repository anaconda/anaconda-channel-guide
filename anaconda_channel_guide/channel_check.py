import requests

BASE_URL = "http://YOUR_BASE_URL/channels/main-x/artifacts/exists"


def is_logged_in() -> bool:
    """Checks if the user is authenticated.

    :returns: True if the user is logged in, False otherwise
    """
    # TODO: real auth check - through conda?
    return False


def is_main_x_configured() -> bool:
    """Checks if the main-x channel is configured in the user's conda setup.

    :param info: Conda context or exception info containing channel configuration
    :returns: True if main-x is in the configured channels, False otherwise
    """
    # TODO: how to see if main-x is configured?
    return False


def is_package_on_main_x(packages: list[str]) -> dict[str, list[str]]:
    """Posts a list of package names to the main-x API and returns available versions.

    :param packages: List of package names to check availability for
    :returns: Dictionary mapping package names to their available versions on main-x
    """
    response = requests.post(BASE_URL, json=packages, timeout=10)
    return response.json()


def get_available_packages_on_main_x(missing_packages: list[str]) -> dict[str, list[str]]:
    """Queries the main-x channel API and filters to only packages
       that have available versions.

    :param missing_packages: List of package names that were not found during install
    :returns: Dictionary of packages available on main-x with their
        versions, or empty dict on API failure
    """
    try:
        availability = is_package_on_main_x(missing_packages)
        in_main_x = {pkg: v for pkg, v in availability.items() if v}
        return in_main_x
    except requests.exceptions.RequestException:
        return {}
