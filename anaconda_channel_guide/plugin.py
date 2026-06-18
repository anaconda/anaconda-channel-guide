from __future__ import annotations

from typing import TYPE_CHECKING

from anaconda_channel_guide.channel_check import is_available_on_main_x
from anaconda_channel_guide.show import (
    CONFIG_STEP,
    LOGIN_STEP,
    ChannelGuideBox,
)

if TYPE_CHECKING:
    from collections.abc import Iterable


def handle_pnfe(
    missing_packages: list[str],
    main_x_configured: bool,
    authenticated: bool,
    subdirs: Iterable[str],
) -> ChannelGuideBox | None:
    """Handles a PackageNotFoundError by checking if missing packages
    are available on main-x and guiding the user on what to do next.

    :param missing_packages: List of package names that triggered the PNFE
    :param main_x_configured: True if the main-x channel is already in the user's config
    :param authenticated: True if the user is currently logged in
    :param subdirs: List of subdirectories to check for availability
    :returns: A user-facing prompt string if action is needed,
        or None to fall through to default PNFE behavior
    """
    if authenticated and main_x_configured:
        return None

    if not is_available_on_main_x(missing_packages, subdirs):
        return None

    steps = []
    if not authenticated:
        steps.append(LOGIN_STEP)
    if not main_x_configured:
        steps.append(CONFIG_STEP)
    return ChannelGuideBox(missing_packages, steps)
