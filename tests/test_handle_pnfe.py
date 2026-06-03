import pytest
import responses
from anaconda_auth.token import TokenNotFoundError
from conda.models.channel import Channel
from pytest_mock import MockerFixture

from anaconda_channel_guide.channel_check import (
    BASE_URL,
    MAIN_X_CHANNEL,
    is_logged_in,
    is_main_x_configured,
)
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
    assert "conda config --append channels https://repo.anaconda.cloud/repo/main-x" in output


@responses.activate
def test_handle_pnfe_not_configured_not_authenticated() -> None:
    """Verifies that a user without main-x configured and not logged in is prompted to do both."""
    responses.post(BASE_URL, json=FOUND_RESPONSE, status=200)

    result = handle_pnfe(["numpy"], main_x_configured=False, authenticated=False)
    assert isinstance(result, ChannelGuideBox)
    output = str(result)
    assert "anaconda login" in output
    assert "conda config --append channels https://repo.anaconda.cloud/repo/main-x" in output


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


@pytest.mark.parametrize("expected", [True, False])
def test_is_logged_in(mocker: MockerFixture, expected: bool) -> None:
    """Verify is_logged_in reflects token state."""
    mock_cls = mocker.patch("anaconda_channel_guide.channel_check.TokenInfo")
    mock_cls.load.return_value.expired = not expected
    assert is_logged_in() == expected


def test_is_logged_in_no_token(mocker: MockerFixture) -> None:
    """Verify user is not considered logged in if no token is found."""
    mock_cls = mocker.patch("anaconda_channel_guide.channel_check.TokenInfo")
    mock_cls.load.side_effect = TokenNotFoundError("no token")
    assert not is_logged_in()


@pytest.mark.parametrize(
    ("channel_urls", "default_channels", "expected"),
    [
        ((MAIN_X_CHANNEL,), (), True),
        ((), (MAIN_X_CHANNEL,), True),
        ((), (), False),
    ],
)
def test_main_x_configured(
    mocker: MockerFixture,
    channel_urls: tuple[Channel, ...],
    default_channels: tuple[Channel, ...],
    expected: bool,
) -> None:
    """Verify is_main_x_configured returns True when main-x is present in channel_urls
    or default_channels, and False otherwise."""
    event = mocker.MagicMock()
    event.exc_value.channel_urls = channel_urls
    mocker.patch("anaconda_channel_guide.channel_check.context").default_channels = default_channels
    assert is_main_x_configured(event) is expected
