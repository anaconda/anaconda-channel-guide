from __future__ import annotations

from typing import TYPE_CHECKING

import requests
from anaconda_auth.token import TokenInfo, TokenNotFoundError
from conda.models.channel import Channel

from anaconda_channel_guide.box import (
    CONFIG_STEP,
    LOGIN_STEP,
    ChannelGuideBox,
)

if TYPE_CHECKING:
    from conda.plugins.types import CondaExceptionEvent

BASE_URL = "http://YOUR_BASE_URL/channels/main-x/artifacts/exists"
MAIN_X_CHANNEL_URL = "https://repo.anaconda.cloud/repo/main-x"
MAIN_X_CHANNEL_NAME = Channel.from_url(MAIN_X_CHANNEL_URL).canonical_name


def is_logged_in() -> bool:
    """Checks if the user is authenticated via anaconda-auth.

    Attempts to load the token. Returns False if no token
    is found or if the token has expired.

    :returns: True if the user has a valid (non-expired) token, False otherwise
    """
    try:
        token_info = TokenInfo.load()
        return not token_info.expired
    except TokenNotFoundError:
        return False


def is_main_x_configured(event: CondaExceptionEvent) -> bool:
    """Checks if the main-x channel is configured in the user's conda setup.

    :param event: The conda exception event containing channel and error information
    :returns: True if main-x is in the configured channels, False otherwise
    """
    return MAIN_X_CHANNEL_NAME in (event.channels or ())


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


def handle_pnfe(
    missing_packages: list[str],
    main_x_configured: bool,
    authenticated: bool,
) -> ChannelGuideBox | None:
    """Handles a PackageNotFoundError by checking if missing packages
    are available on main-x and guiding the user on what to do next.

    :param missing_packages: List of package names that triggered the PNFE
    :param main_x_configured: True if the main-x channel is already in the user's config
    :param authenticated: True if the user is currently logged in
    :returns: A ChannelGuideBox object if action is needed,
        None to fall through to default PNFE behavior
    """

    in_main_x = get_available_packages_on_main_x(missing_packages)

    if not in_main_x:
        return None

    if authenticated and main_x_configured:
        return None

    packages = ", ".join(in_main_x.keys())

    steps = []
    if not authenticated:
        steps.append(LOGIN_STEP)
    if not main_x_configured:
        steps.append(CONFIG_STEP)
    return ChannelGuideBox(packages, steps)
