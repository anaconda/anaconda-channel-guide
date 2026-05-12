from anaconda_channel_guide.channel_check import get_available_packages_on_main_x
from anaconda_channel_guide.show import show_login_prompt, show_config_prompt, show_login_and_config_prompt



def handle_pnfe(missing_packages: list[str], main_x_configured: bool, authenticated: bool) -> str | None:
    """Handles a PackageNotFoundError by checking if missing packages are available on main-x and guiding the user on what to do next.

    :param missing_packages: List of package names that triggered the PNFE
    :param main_x_configured: True if the main-x channel is already in the user's config
    :param authenticated: True if the user is currently logged in
    :returns: A user-facing prompt string if action is needed, or None to fall through to default PNFE behavior
    """

    if not get_available_packages_on_main_x(missing_packages):
        return None

    # best case scenario: PNFE really means it's not on main x
    if authenticated and main_x_configured:
        return None

    if main_x_configured and not authenticated:
        return show_login_prompt()
    elif not main_x_configured and authenticated:
        return show_config_prompt()
    else:
        return show_login_and_config_prompt()