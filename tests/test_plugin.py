import pytest
import responses
from anaconda_auth.token import TokenNotFoundError
from pytest_mock import MockerFixture

from anaconda_channel_guide.box import CONFIG_STEP, LOGIN_STEP, ChannelGuideBox
from anaconda_channel_guide.plugin import (
    BASE_URL,
    MAIN_X_CHANNEL_NAME,
    handle_pnfe,
    is_logged_in,
    is_main_x_configured,
    is_package_on_main_x,
)

FOUND_RESPONSE: dict[str, list[str]] = {"numpy": ["1.24", "1.25"]}
NOT_FOUND_RESPONSE: dict[str, list[str]] = {"numpy": []}
MOCK_RESPONSE: dict[str, list[str]] = {"numpy": ["1.24", "1.25"], "six": []}


@responses.activate
def test_handle_pnfe_configured_not_authenticated() -> None:
    """Verifies that a user with main-x configured but not logged in is prompted to log in."""
    responses.post(BASE_URL, json=FOUND_RESPONSE, status=200)

    result = handle_pnfe(["numpy"], main_x_configured=True, authenticated=False)
    assert isinstance(result, ChannelGuideBox)
    assert LOGIN_STEP in result.steps


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
    assert CONFIG_STEP in result.steps


@responses.activate
def test_handle_pnfe_not_configured_not_authenticated() -> None:
    """Verifies that a user without main-x configured and not logged in is prompted to do both."""
    responses.post(BASE_URL, json=FOUND_RESPONSE, status=200)

    result = handle_pnfe(["numpy"], main_x_configured=False, authenticated=False)
    assert isinstance(result, ChannelGuideBox)
    assert LOGIN_STEP in result.steps
    assert CONFIG_STEP in result.steps


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
    mock_cls = mocker.patch("anaconda_channel_guide.plugin.TokenInfo")
    mock_cls.load.return_value.expired = not expected
    assert is_logged_in() == expected


def test_is_logged_in_no_token(mocker: MockerFixture) -> None:
    """Verify user is not considered logged in if no token is found."""
    mock_cls = mocker.patch("anaconda_channel_guide.plugin.TokenInfo")
    mock_cls.load.side_effect = TokenNotFoundError("no token")
    assert not is_logged_in()


@pytest.mark.parametrize(
    ("channels", "expected"),
    [
        ((MAIN_X_CHANNEL_NAME,), True),
        (("defaults", MAIN_X_CHANNEL_NAME), True),
        (("defaults", "conda-forge"), False),
        ((), False),
        (None, False),
    ],
)
def test_main_x_configured(
    mocker: MockerFixture,
    channels: tuple[str, ...] | None,
    expected: bool,
) -> None:
    event = mocker.MagicMock()
    event.channels = channels
    assert is_main_x_configured(event) is expected


@responses.activate
def test_is_package_on_main_x() -> None:
    """Verifies that is_package_on_main_x posts the package list
    and returns the parsed API response.
    """
    responses.post(
        BASE_URL,
        json=MOCK_RESPONSE,
        status=200,
    )

    result = is_package_on_main_x(["numpy", "six"])

    assert result == MOCK_RESPONSE


def test_render_channel_guide_prints(capsys: pytest.CaptureFixture) -> None:
    """Verifies render_channel_guide outputs the panel to stderr."""
    from anaconda_channel_guide.box import render_channel_guide

    box = ChannelGuideBox("numpy", [LOGIN_STEP])
    render_channel_guide(box)
    _, err = capsys.readouterr()
    assert "Anaconda Channel Guide" in err
