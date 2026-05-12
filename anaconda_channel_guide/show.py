def show_login_prompt() -> str:
    """Builds a prompt telling the user to log in to access main-x.

    :returns: Message string instructing the user to log in
    """
    return "Please login to your account to continue."


def show_config_prompt() -> str:
    """Builds a prompt telling the user to add the main-x channel to their config.

    :returns: Message string with the command to add main-x to their channel configuration
    """
    return "Please configure your main-x channel to continue."


def show_login_and_config_prompt() -> str:
    """Builds a prompt telling the user to both add the main-x channel and log in.

    :returns: Message string instructing the user to configure main-x and log in
    """
    return "Please login to your account and configure your main-x channel to continue."

