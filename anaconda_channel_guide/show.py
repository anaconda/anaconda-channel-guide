from io import StringIO

from rich.console import Console
from rich.padding import Padding
from rich.panel import Panel


class ChannelGuideBox:
    """Reusable Rich panel for channel guide prompts."""

    TITLE = "Anaconda Channel Guide"
    FOOTER = "Then re-run your original command."

    def __init__(self, header: str, steps: list[str]) -> None:
        """
        :param header: Top message explaining the situation
        :param steps: Numbered action items for the user
        """
        self.header = header
        self.steps = steps

    def to_panel(self) -> Panel:
        body = self.header
        for i, step in enumerate(self.steps, 1):
            body += f"\n\n  {i}. {step}"
        body += f"\n\n{self.FOOTER}"
        return Padding(Panel(body, title=self.TITLE, padding=(1, 2)), (1, 0))

    def __str__(self) -> str:
        console = Console(file=StringIO(), width=84, height=25, highlight=False, markup=False)
        console.print(self.to_panel())
        return console.file.getvalue()


def show_login_prompt(package: str) -> ChannelGuideBox:
    return ChannelGuideBox(
        header=f"'{package}' is available in Anaconda's 'main-x' channel.",
        steps=["Log in:\n\n    $ anaconda login"],
    )


def show_config_prompt(package: str) -> ChannelGuideBox:
    return ChannelGuideBox(
        header=f"'{package}' is available in Anaconda's 'main-x' channel.",
        steps=[
            "Add the 'main-x' channel:\n\n"
            "    $ conda config --append channels https://repo.anaconda.cloud/repo/main-x"
        ],
    )


def show_login_and_config_prompt(package: str) -> ChannelGuideBox:
    return ChannelGuideBox(
        header=f"'{package}' is available in Anaconda's 'main-x' channel.",
        steps=[
            "Log in:\n\n    $ anaconda login",
            "Add the 'main-x' channel:\n\n"
            "    $ conda config --append channels https://repo.anaconda.cloud/repo/main-x",
        ],
    )
