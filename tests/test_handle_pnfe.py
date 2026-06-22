import pytest
from anaconda_auth.token import TokenNotFoundError
from pytest_mock import MockerFixture

from anaconda_channel_guide.channel_check import (
    MAIN_X_CHANNEL_NAME,
    is_logged_in,
    is_main_x_configured,
)
from anaconda_channel_guide.hooks import on_package_not_found
from anaconda_channel_guide.plugin import handle_pnfe
from anaconda_channel_guide.show import ChannelGuideBox

LOGIN_CMD = "anaconda login"
CONFIG_CMD = "conda config --append channels https://repo.anaconda.cloud/repo/main-x"
SUBDIRS = ("linux-64", "noarch")


@pytest.mark.parametrize(
    ("on_main_x", "main_x_configured", "authenticated"),
    [
        (False, True, False),
        (False, False, False),
        (True, True, True),
    ],
)
def test_handle_pnfe_returns_none(
    mocker: MockerFixture,
    on_main_x: bool,
    main_x_configured: bool,
    authenticated: bool,
) -> None:
    """No prompt when packages aren't on main-x, or the user is already set up."""
    mocker.patch("anaconda_channel_guide.plugin.is_available_on_main_x", return_value=on_main_x)

    result = handle_pnfe(
        ["pychoir"],
        main_x_configured=main_x_configured,
        authenticated=authenticated,
        subdirs=SUBDIRS,
    )
    assert result is None


@pytest.mark.parametrize(
    ("main_x_configured", "authenticated", "expected_steps"),
    [
        (True, False, [LOGIN_CMD]),
        (False, True, [CONFIG_CMD]),
        (False, False, [LOGIN_CMD, CONFIG_CMD]),
    ],
)
def test_handle_pnfe_prompts_required_steps(
    mocker: MockerFixture,
    main_x_configured: bool,
    authenticated: bool,
    expected_steps: list[str],
) -> None:
    """When packages are on main-x and setup is incomplete, prompt the missing steps."""
    mocker.patch("anaconda_channel_guide.plugin.is_available_on_main_x", return_value=True)

    result = handle_pnfe(
        ["pychoir"],
        main_x_configured=main_x_configured,
        authenticated=authenticated,
        subdirs=SUBDIRS,
    )
    assert isinstance(result, ChannelGuideBox)
    output = str(result)
    for step in expected_steps:
        assert step in output


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


def test_on_package_not_found_skips_offline(mocker: MockerFixture) -> None:
    """Availability checks are skipped entirely when conda is in offline mode."""
    event = mocker.MagicMock()
    event.offline = True
    mock_handle = mocker.patch("anaconda_channel_guide.hooks.handle_pnfe")
    on_package_not_found(event)
    mock_handle.assert_not_called()
