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
    return str(ChannelGuideBox([package], steps))


def test_always_present_content() -> None:
    """Ensure that content always appended by to_panel() is present in the output."""
    output = box_output("package", [])

    assert ChannelGuideBox.TITLE in output
    assert "Then re-run the original command." in output
    assert all(line in output for line in DISABLE_STEP.splitlines() if line)


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
    assert expected_intro in str(box)


def test_steps_not_repeated_per_package() -> None:
    from anaconda_channel_guide.box import CONFIG_STEP, LOGIN_STEP

    box = ChannelGuideBox(["a", "b"], [LOGIN_STEP, CONFIG_STEP])
    body = box.to_panel().renderable.renderable
    assert body.count(LOGIN_STEP) == 1
    assert body.count(CONFIG_STEP) == 1
