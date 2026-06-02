from anaconda_channel_guide.channel_check import get_available_packages_on_main_x
from anaconda_channel_guide.show import (
    ChannelGuideBox,
    show_config_prompt,
    show_login_and_config_prompt,
    show_login_prompt,
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

    in_main_x = get_available_packages_on_main_x(missing_packages)

    if not in_main_x:
        return None

    if authenticated and main_x_configured:
        return None

    # TODO: confirm API response shape for multi-package requests
    packages = ", ".join(in_main_x.keys())

    if main_x_configured and not authenticated:
        return show_login_prompt(packages)
    elif not main_x_configured and authenticated:
        return show_config_prompt(packages)
    else:
        return show_login_and_config_prompt(packages)
