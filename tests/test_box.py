from __future__ import annotations

import pytest

from anaconda_channel_guide.box import (
    CONFIG_STEP,
    DISABLE_STEP,
    LOGIN_STEP,
    TOS_MESSAGE,
    ChannelGuideBox,
)


def box_output(packages: list[str], steps: list[str]) -> str:
    """Get the output of a ChannelGuideBox for the given packages and steps"""
    return ChannelGuideBox(packages, steps).plain_text_message()


def test_always_present_content() -> None:
    """Ensure that content always appended by to_panel() is present in the output."""
    output = box_output(["package"], [])

    assert ChannelGuideBox.TITLE in output
    assert "Re-run the original command." in output
    assert all(line in output for line in DISABLE_STEP.splitlines() if line)
    assert all(line in output for line in TOS_MESSAGE.splitlines() if line)


@pytest.mark.parametrize(
    ("packages", "expected"),
    [
        pytest.param(
            ["pychoir"],
            "'pychoir' is available in Anaconda's 'main-x' channel.",
            id="single-package",
        ),
        pytest.param(
            ["pychoir", "aabbtree"],
            "'pychoir' and 'aabbtree' are available in Anaconda's 'main-x' channel.",
            id="two-packages",
        ),
        pytest.param(
            ["pychoir", "aabbtree", "numpy"],
            "'pychoir', 'aabbtree', and 'numpy' are available in Anaconda's 'main-x' channel.",
            id="three-packages",
        ),
    ],
)
def test_package_name_display(packages: list[str], expected: str) -> None:
    """Ensure that the package name(s) are displayed in the box with correct grammar."""
    assert expected in box_output(packages, [])


@pytest.mark.parametrize(
    ("steps", "expected_fragments"),
    [
        pytest.param(LOGIN_STEP, ["1. Log in:", "$ anaconda login"], id="login_only"),
        pytest.param(
            CONFIG_STEP,
            ["1. Add the 'main-x' channel:", "conda config --append channels"],
            id="config_only",
        ),
        pytest.param(
            [LOGIN_STEP, CONFIG_STEP],
            ["1. Log in:", "$ anaconda login", "2. Add the 'main-x' channel:"],
            id="login_and_config",
        ),
    ],
)
def test_expected_steps_in_box(steps: list[str] | str, expected_fragments: list[str]) -> None:
    """Ensure that the expected steps are displayed in the box."""
    step_list = [steps] if isinstance(steps, str) else steps
    output = box_output(["pychoir"], step_list)
    for fragment in expected_fragments:
        assert fragment in output


@pytest.mark.parametrize(
    ("packages", "expected_intro"),
    [
        pytest.param(
            ["numpy"],
            "'numpy' is available in Anaconda's 'main-x' channel.",
            id="single-package",
        ),
        pytest.param(
            ["numpy", "pandas"],
            "'numpy' and 'pandas' are available in Anaconda's 'main-x' channel.",
            id="two-packages",
        ),
        pytest.param(
            ["numpy", "pandas", "scipy"],
            "'numpy', 'pandas', and 'scipy' are available in Anaconda's 'main-x' channel.",
            id="three-packages",
        ),
    ],
)
def test_package_intro_formatting(packages: list[str], expected_intro: str) -> None:
    """Intro line uses correct grammar for one, two, or three packages."""
    box = ChannelGuideBox(packages, [])
    assert expected_intro in box.plain_text_message()


def test_steps_not_repeated_per_package() -> None:
    box = ChannelGuideBox(["a", "b"], [LOGIN_STEP, CONFIG_STEP])
    output = box.plain_text_message()
    assert output.count("$ anaconda login") == 1
    assert output.count("$ conda config --append channels") == 1
