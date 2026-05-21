import responses
from anaconda_auth.token import TokenNotFoundError
from pytest_mock import MockerFixture

from anaconda_channel_guide.channel_check import BASE_URL, is_logged_in
from anaconda_channel_guide.plugin import handle_pnfe
from anaconda_channel_guide.show import ChannelGuideBox

FOUND_RESPONSE: dict[str, list[str]] = {"numpy": ["1.24", "1.25"]}
NOT_FOUND_RESPONSE: dict[str, list[str]] = {"numpy": []}


@responses.activate
def test_handle_pnfe_configured_not_authenticated() -> None:
    """Verifies that a user with main-x configured but not logged in is prompted to log in."""
    responses.post(BASE_URL, json=FOUND_RESPONSE, status=200)

    result = handle_pnfe(["numpy"], main_x_configured=True, authenticated=False)
    assert isinstance(result, ChannelGuideBox)
    output = str(result)
    assert "anaconda login" in output


@responses.activate
def test_handle_pnfe_configured_not_found() -> None:
    """Verifies that when the package is not on main-x, the plugin
    falls through to default PNFE behavior.
    """
    responses.post(BASE_URL, json=NOT_FOUND_RESPONSE, status=200)

    result = handle_pnfe(["numpy"], main_x_configured=True, authenticated=False)
    assert result is None


@responses.activate
def test_handle_pnfe_not_configured_authenticated() -> None:
    """Verifies that a logged-in user without main-x configured is prompted to add the channel."""
    responses.post(BASE_URL, json=FOUND_RESPONSE, status=200)

    result = handle_pnfe(["numpy"], main_x_configured=False, authenticated=True)
    assert isinstance(result, ChannelGuideBox)
    output = str(result)
    assert "conda config --add channels main-x" in output


@responses.activate
def test_handle_pnfe_not_configured_not_authenticated() -> None:
    """Verifies that a user without main-x configured and not logged in is prompted to do both."""
    responses.post(BASE_URL, json=FOUND_RESPONSE, status=200)

    result = handle_pnfe(["numpy"], main_x_configured=False, authenticated=False)
    assert isinstance(result, ChannelGuideBox)
    output = str(result)
    assert "anaconda login" in output
    assert "conda config --add channels main-x" in output


@responses.activate
def test_handle_pnfe_not_configured_not_found() -> None:
    """Verifies that when the package is not on main-x, the plugin
    falls through to default PNFE behavior.
    """
    responses.post(BASE_URL, json=NOT_FOUND_RESPONSE, status=200)

    result = handle_pnfe(["numpy"], main_x_configured=False, authenticated=False)
    assert result is None


@responses.activate
def test_handle_pnfe_fully_setup() -> None:
    """Verifies that a fully set up user (authenticated with main-x
    configured) gets no prompt, even if the package exists on main-x.
    """
    responses.post(BASE_URL, json=FOUND_RESPONSE, status=200)
    result = handle_pnfe(["numpy"], main_x_configured=True, authenticated=True)
    assert result is None


def test_is_logged_in_valid_token(mocker: MockerFixture) -> None:
    """Verify user is considered logged in if a valid token exists."""
    mock_cls = mocker.patch("anaconda_channel_guide.channel_check.TokenInfo")
    fake_token = mock_cls.load.return_value
    fake_token.expired = False
    assert is_logged_in() is True


def test_is_logged_in_expired_token(mocker: MockerFixture) -> None:
    """Verify user is not considered logged in if token is expired."""
    mock_cls = mocker.patch("anaconda_channel_guide.channel_check.TokenInfo")
    fake_token = mock_cls.load.return_value
    fake_token.expired = True
    assert is_logged_in() is False


def test_is_logged_in_no_token(mocker: MockerFixture) -> None:
    """Verify user is not considered logged in if no token is found."""
    mock_cls = mocker.patch("anaconda_channel_guide.channel_check.TokenInfo")
    mock_cls.load.side_effect = TokenNotFoundError("no token")
    assert is_logged_in() is False
