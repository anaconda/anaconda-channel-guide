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
