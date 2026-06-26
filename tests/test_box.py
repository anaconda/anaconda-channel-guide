from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from anaconda_channel_guide.box import (
    CONFIG_STEP,
    DISABLE_STEP,
    LOGIN_STEP,
    ChannelGuideBox,
)
from anaconda_channel_guide.hooks import on_package_not_found

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from pytest_mock import MockerFixture


def box_output(package: str, steps: list[str]) -> str:
    """Get the output of a ChannelGuideBox for a given package and steps"""
    return str(ChannelGuideBox(package, steps))


def make_pnfe_event(mocker: MockerFixture, *, quiet: bool = False, json: bool = False) -> MagicMock:
    """Make a mock CondaExceptionEvent for tests"""
    event = mocker.MagicMock()
    event.exc_value.message = "Packages not found.\n"
    event.exc_value.packages = ["pychoir"]
    event.channels = ("defaults",)
    event.quiet = quiet
    event.json = json
    return event


def test_disable_message_shown() -> None:
    """Ensure that the message to disable the plug-in is shown."""
    output = box_output("package", [])
    padding = ChannelGuideBox("package", []).to_panel()
    assert DISABLE_STEP in padding.renderable.renderable
    lines = [line for line in DISABLE_STEP.split("\n") if line]
    assert all(line in output for line in lines)


@pytest.mark.parametrize(
    ("package", "expected"),
    [
        ("pychoir", "'pychoir' is available in Anaconda's 'main-x' channel."),
    ],
)
def test_package_name_display(package: str, expected: str) -> None:
    """Ensure that the package name is displayed in the box."""
    assert expected in box_output(package, [])


def test_always_present_content() -> None:
    """Ensure that the always present content is displayed in the box."""
    output = box_output("pychoir", [LOGIN_STEP])
    assert ChannelGuideBox.TITLE in output
    assert "Then re-run the original command." in output
    assert "conda config --set plugins.anaconda_channel_guide false" in output


@pytest.mark.parametrize(
    ("steps", "expected_fragments"),
    [
        (LOGIN_STEP, ["1. Log in:", "$ anaconda login"]),
        (CONFIG_STEP, ["1. Add the 'main-x' channel:", "conda config --append channels"]),
        (
            [LOGIN_STEP, CONFIG_STEP],
            ["1. Log in:", "$ anaconda login", "2. Add the 'main-x' channel:"],
        ),
    ],
    ids=["login_only", "config_only", "login_and_config"],
)
def test_expected_steps_in_box(steps: list[str] | str, expected_fragments: list[str]) -> None:
    """Ensure that the expected steps are displayed in the box."""
    step_list = [steps] if isinstance(steps, str) else steps
    output = box_output("pychoir", step_list)
    for fragment in expected_fragments:
        print(f"Checking for fragment: {fragment!r}")
        assert fragment in output


@pytest.mark.parametrize(
    ("authenticated", "main_x_configured", "expected_fragments"),
    [
        (False, False, ["$ anaconda login", "conda config --append channels"]),
        (False, True, ["$ anaconda login"]),
        (True, False, ["conda config --append channels"]),
    ],
    ids=["needs_login_and_config", "needs_login_only", "needs_config_only"],
)
def test_box_appended(
    mocker: MockerFixture,
    authenticated: bool,
    main_x_configured: bool,
    expected_fragments: list[str],
) -> None:
    """Plugin enabled, normal output, package on main-x, action still needed."""
    event = make_pnfe_event(mocker)
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
        "anaconda_channel_guide.plugin.get_available_packages_on_main_x",
        return_value={"pychoir": ["0.0.29"]},
    )

    on_package_not_found(event)

    assert event.exc_value.message.startswith(original_message)
    assert event.exc_value.message != original_message
    assert ChannelGuideBox.TITLE in event.exc_value.message
    for fragment in expected_fragments:
        assert fragment in event.exc_value.message


@pytest.mark.parametrize(
    ("quiet", "json", "authenticated", "main_x_configured", "availability"),
    [
        (True, False, False, False, {"pychoir": ["0.0.29"]}),
        (False, True, False, False, {"pychoir": ["0.0.29"]}),
        (False, False, True, True, {"pychoir": ["0.0.29"]}),
        (False, False, False, False, {}),
    ],
)
def test_box_not_appended(
    mocker: MockerFixture,
    quiet: bool,
    json: bool,
    authenticated: bool,
    main_x_configured: bool,
    availability: dict[str, list[str]],
) -> None:
    """"""
    event = make_pnfe_event(mocker, quiet=quiet, json=json)
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
        "anaconda_channel_guide.plugin.get_available_packages_on_main_x",
        return_value=availability,
    )
    on_package_not_found(event)
    assert event.exc_value.message == original_message
    assert ChannelGuideBox.TITLE not in event.exc_value.message
