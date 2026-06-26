from __future__ import annotations

import pytest

from anaconda_channel_guide.box import (
    CONFIG_STEP,
    DISABLE_STEP,
    LOGIN_STEP,
    ChannelGuideBox,
)


def box_output(package: str, steps: list[str]) -> str:
    """Get the output of a ChannelGuideBox for a given package and steps"""
    return str(ChannelGuideBox(package, steps))


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
        ("pychoir, aabbtree", "'pychoir, aabbtree' is available in Anaconda's 'main-x' channel."),
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
        assert fragment in output
