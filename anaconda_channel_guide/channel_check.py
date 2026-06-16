from collections.abc import Iterable

from anaconda_auth.token import TokenInfo, TokenNotFoundError
from conda.core.subdir_data import SubdirData
from conda.models.match_spec import MatchSpec
from conda.models.records import PackageRecord

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


def is_available_on_main_x(packages: Iterable[MatchSpec | PackageRecord | str]) -> bool:
    """Checks whether all of the given packages are available on the main-x channel.

    :param packages: Package specs to check (names, match specs, or records)
    :returns: True if every package is available on main-x, False otherwise
    """
    try:
        for package in packages:
            if isinstance(package, PackageRecord):
                return False
            if not SubdirData.query_all(package, channels=[MAIN_X_CHANNEL_URL]):
                return False
    except Exception:
        return False
    return True
