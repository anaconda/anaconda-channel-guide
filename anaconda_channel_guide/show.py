from rich.panel import Panel
from rich.console import Console
from rich.padding import Padding
from io import StringIO


class ChannelGuideBox:
    """Reusable Rich panel for channel guide prompts."""

    TITLE = "Anaconda Channel Guide"

    def __init__(self, header: str, steps: list[str]):
        """
        :param header: Top message explaining the situation
        :param steps: Numbered action items for the user
        """
        self.header = header
        self.steps = steps

    def to_panel(self) -> Panel:
        body = self.header + "\n"
        for i, step in enumerate(self.steps, 1):
            body += f"\n  {i}. {step}"
        return Padding(Panel(body, title=self.TITLE, padding=(1, 2)), (1, 0))

    def __str__(self) -> str:
        console = Console(file=StringIO(), width=80, highlight=False, markup=False)
        console.print(self.to_panel())
        return console.file.getvalue()


def show_login_prompt() -> ChannelGuideBox:
    return ChannelGuideBox(
        header="This package is available in main-x, Anaconda's extended channel.",
        steps=["Log in: anaconda login"],
    )

def show_config_prompt() -> ChannelGuideBox:
    return ChannelGuideBox(
        header="This package is available in main-x, Anaconda's extended channel.",
        steps=["Add the channel: conda config --add channels main-x"],
    )

def show_login_and_config_prompt() -> ChannelGuideBox:
    return ChannelGuideBox(
        header="This package is available in main-x, Anaconda's extended channel.",
        steps=[
            "Log in: anaconda login",
            "Add the channel: conda config --add channels main-x",
        ],
    )
