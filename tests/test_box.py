import pytest

from anaconda_channel_guide.box import (
    DISABLE_STEP,
    ChannelGuideBox,
)


def test_disable_message_shown() -> None:
    """Ensure that the message to disable the plug-in is shown."""
    box = ChannelGuideBox("package", [])
    padding = box.to_panel()
    assert DISABLE_STEP in padding.renderable.renderable
    lines = [line for line in DISABLE_STEP.split("\n") if line]
    assert all(line in str(box) for line in lines)


@pytest.mark.parametrize(
    ("packages", "expected_intro"),
    [
        (
            ["numpy"],
            "'numpy' is available in Anaconda's 'main-x' channel.",
        ),
        (
            ["numpy", "pandas"],
            "'numpy' and 'pandas' are available in Anaconda's 'main-x' channel.",
        ),
        (
            ["numpy", "pandas", "scipy"],
            "'numpy', 'pandas', and 'scipy' are available in Anaconda's 'main-x' channel.",
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
