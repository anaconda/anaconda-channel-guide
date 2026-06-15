from anaconda_channel_guide.channel_check import get_packages_on_main_x
from anaconda_channel_guide.show import (
    CONFIG_STEP,
    LOGIN_STEP,
    ChannelGuideBox,
)


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
    :returns: A user-facing prompt string if action is needed,
        or None to fall through to default PNFE behavior
    """

    if not get_packages_on_main_x(missing_packages):
        return None

    if authenticated and main_x_configured:
        return None

    packages = ", ".join([str(package) for package in missing_packages])

    steps = []
    if not authenticated:
        steps.append(LOGIN_STEP)
    if not main_x_configured:
        steps.append(CONFIG_STEP)
    return ChannelGuideBox(packages, steps)
