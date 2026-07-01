from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from conda.exceptions import PackagesNotFoundInChannelsError
from conda.plugins.types import CondaExceptionEvent

from anaconda_channel_guide.box import ChannelGuideBox
from anaconda_channel_guide.hooks import conda_settings, on_package_not_found

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


def make_pnfe_event(
    json: bool = False,
    channels: tuple[str, ...] | None = ("defaults",),
    packages: list[str] | None = None,
    offline: bool = False,
    conda_version: str | None = "26.5.3",
) -> CondaExceptionEvent:
    """Build a CondaExceptionEvent for PackagesNotFoundError hook tests."""
    channel_urls = () if channels is None else channels
    exc = PackagesNotFoundInChannelsError(packages or ["pychoir"], channel_urls=channel_urls)
    return CondaExceptionEvent(
        exc_type=PackagesNotFoundInChannelsError,
        exc_value=exc,
        exc_traceback=None,
        channels=channels,
        json=json,
        offline=offline,
        conda_version=conda_version,
    )


def test_conda_settings() -> None:
    """
    Ensure the correct conda settings are returned
    """
    settings = list(conda_settings())

    assert len(settings) == 1
    assert settings[0].name == "anaconda_channel_guide"
    assert settings[0].description == "Whether Anaconda Channel Guide is enabled"
    assert settings[0].parameter.default.value is True


@pytest.mark.parametrize(
    "enabled",
    [pytest.param(True, id="enabled"), pytest.param(False, id="disabled")],
)
def test_enable_disable_plugin(enabled: bool, mocker: MockerFixture) -> None:
    """
    Make sure that nothing is returned when the plugin is disabled via settings
    """
    mocker.patch("anaconda_channel_guide.hooks.context.plugins.anaconda_channel_guide", enabled)
    event = make_pnfe_event()
    mock_handle = mocker.patch("anaconda_channel_guide.hooks.handle_pnfe")
    on_package_not_found(event)
    assert mock_handle.called is enabled


@pytest.mark.parametrize(
    ("authenticated", "main_x_configured", "expected_fragments"),
    [
        pytest.param(
            False,
            False,
            ["$ anaconda login", "conda config --append channels"],
            id="needs_login_and_config",
        ),
        pytest.param(False, True, ["$ anaconda login"], id="needs_login_only"),
        pytest.param(True, False, ["conda config --append channels"], id="needs_config_only"),
    ],
)
def test_box_correct_steps_appended(
    mocker: MockerFixture,
    authenticated: bool,
    main_x_configured: bool,
    expected_fragments: list[str],
) -> None:
    """Plugin enabled, normal output, package on main-x, action still needed."""
    event = make_pnfe_event()
    original_message = event.exc_value.message

    mocker.patch(
        "anaconda_channel_guide.hooks.context.plugins.anaconda_channel_guide",
        True,
    )
    mocker.patch(
        "anaconda_channel_guide.hooks.is_logged_in",
        return_value=authenticated,
    )
    mocker.patch(
        "anaconda_channel_guide.hooks.is_main_x_configured",
        return_value=main_x_configured,
    )
    mocker.patch(
        "anaconda_channel_guide.plugin.is_available_on_main_x",
        return_value=True,
    )

    on_package_not_found(event)

    assert event.exc_value.message.startswith(original_message)
    assert event.exc_value.message != original_message
    assert ChannelGuideBox.TITLE in event.exc_value.message
    for fragment in expected_fragments:
        assert fragment in event.exc_value.message


@pytest.mark.parametrize(
    ("enabled", "json", "authenticated", "main_x_configured", "on_main_x"),
    [
        pytest.param(True, True, False, False, True, id="json"),
        pytest.param(True, False, True, True, True, id="no_action_needed"),
        pytest.param(True, False, False, False, False, id="not_on_main_x"),
        pytest.param(False, False, False, False, True, id="disabled"),
    ],
)
def test_box_not_appended(
    mocker: MockerFixture,
    enabled: bool,
    json: bool,
    authenticated: bool,
    main_x_configured: bool,
    on_main_x: bool,
) -> None:
    """Box is not appended when output mode or user state makes it unnecessary."""
    event = make_pnfe_event(json=json)
    original_message = event.exc_value.message
    mocker.patch(
        "anaconda_channel_guide.hooks.context.plugins.anaconda_channel_guide",
        enabled,
    )
    mocker.patch(
        "anaconda_channel_guide.hooks.is_logged_in",
        return_value=authenticated,
    )
    mocker.patch(
        "anaconda_channel_guide.hooks.is_main_x_configured",
        return_value=main_x_configured,
    )
    mocker.patch(
        "anaconda_channel_guide.plugin.is_available_on_main_x",
        return_value=on_main_x,
    )
    on_package_not_found(event)
    assert event.exc_value.message == original_message
    assert ChannelGuideBox.TITLE not in event.exc_value.message


@pytest.mark.parametrize(
    "conda_version",
    [
        pytest.param("26.7.0", id="at_max_unsupported"),
        pytest.param("26.9.0", id="above_max_unsupported"),
    ],
)
def test_box_not_appended_outside_supported_version_range(
    mocker: MockerFixture,
    conda_version: str,
) -> None:
    """
    Box is not appended when conda_version is at or above MAX_CONDA_VERSION.
    """
    event = make_pnfe_event(conda_version=conda_version)
    original_message = event.exc_value.message

    mocker.patch("anaconda_channel_guide.hooks.context.plugins.anaconda_channel_guide", True)
    mocker.patch("anaconda_channel_guide.hooks.is_logged_in", return_value=False)
    mocker.patch("anaconda_channel_guide.hooks.is_main_x_configured", return_value=False)
    mocker.patch("anaconda_channel_guide.plugin.is_available_on_main_x", return_value=True)

    on_package_not_found(event)

    assert event.exc_value.message == original_message
    assert ChannelGuideBox.TITLE not in event.exc_value.message
