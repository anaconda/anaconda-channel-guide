from rich.console import Console
from rich.padding import Padding
from rich.panel import Panel

MAX_WIDTH = 84
MAX_HEIGHT = 25

LOGIN_STEP = "Log in:\n\n    $ anaconda login"
CONFIG_STEP = "Add the 'main-x' channel:\n\n    $ conda config --append channels https://repo.anaconda.cloud/repo/main-x"


class ChannelGuideBox:
    """Reusable Rich panel for channel guide prompts."""

    TITLE = "Anaconda Channel Guide"

    def __init__(self, package: str, steps: list[str]) -> None:
        """
        :param package: Package name that triggered the PNFE
        :param steps: Numbered action items for the user
        """
        self.package = package
        self.steps = steps

    def to_panel(self) -> Padding:
        """Returns a Rich panel with the package name and steps."""
        body = f"'{self.package}' is available in Anaconda's 'main-x' channel."
        for i, step in enumerate(self.steps, 1):
            body += f"\n\n  {i}. {step}"
        body += "\n\nThen re-run the original command."
        return Padding(Panel(body, title=self.TITLE, padding=(1, 2)), (1, 0))


def render_channel_guide(box: ChannelGuideBox) -> None:
    """Renders a ChannelGuideBox to stderr as a Rich panel.

    Auto-detects terminal width and caps at MAX_WIDTH to prevent
    the box from stretching on wide terminals.

    :param box: The channel guide box to render
    """
    console = Console(stderr=True, height=MAX_HEIGHT)
    if console.width > MAX_WIDTH:
        console = Console(stderr=True, width=MAX_WIDTH, height=MAX_HEIGHT)
    console.print(box.to_panel())
