from anaconda_auth.token import TokenInfo, TokenNotFoundError
from conda.base.context import context
from conda.core.subdir_data import SubdirData
from conda.models.match_spec import MatchSpec

BASE_URL = "http://YOUR_BASE_URL/channels/main-x/artifacts/exists"

MAIN_X_CHANNEL_URL = "https://repo.anaconda.cloud/repo/main-x"


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


def is_main_x_configured() -> bool:
    """Checks if the main-x channel is configured in the user's conda setup.

    :param info: Conda context or exception info containing channel configuration
    :returns: True if main-x is in the configured channels, False otherwise
    """
    # TODO: how to see if main-x is configured?
    return False


def get_packages_on_main_x(specs: list[str]) -> dict[str, list[str]]:
    """Queries main-x repodata to check which of the given package specs exist.

    :param specs: List of package specs (names or match specs) to check
    :returns: Mapping of package name to its versions on main-x
    """
    available: dict[str, list[str]] = {}
    for spec in specs:
        name = MatchSpec(spec).name
        records = SubdirData.query_all(name, channels=[MAIN_X_CHANNEL_URL], subdirs=context.subdirs)
        if records:
            available[name] = sorted({r.version for r in records})
    return available
