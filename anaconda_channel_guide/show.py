from io import StringIO

from rich.console import Console
from rich.padding import Padding
from rich.panel import Panel

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

    def to_panel(self) -> Panel:
        body = f"'{self.package}' is available in Anaconda's 'main-x' channel."
        for i, step in enumerate(self.steps, 1):
            body += f"\n\n  {i}. {step}"
        body += "\n\nThen re-run the original command."
        return Padding(Panel(body, title=self.TITLE, padding=(1, 2)), (1, 0))

    def __str__(self) -> str:
        console = Console(file=StringIO(), width=84, height=25, highlight=False, markup=False)
        console.print(self.to_panel())
        return console.file.getvalue()
