from collections.abc import Iterable
from io import StringIO

from conda.models.match_spec import MatchSpec
from rich.console import Console
from rich.padding import Padding
from rich.panel import Panel

LOGIN_STEP = "Log in:\n\n    $ anaconda login"
CONFIG_STEP = (
    "Add the 'main-x' channel:\n\n"
    "    $ conda config --append channels https://repo.anaconda.cloud/repo/main-x"
)
DISABLE_STEP = (
    "To disable these notifications, please run:\n\n"
    "    $ conda config --set plugins.anaconda_channel_guide false"
)


class ChannelGuideBox:
    """Reusable Rich panel for channel guide prompts."""

    TITLE = "Anaconda Channel Guide"

    def __init__(self, packages: Iterable[str], steps: list[str]) -> None:
        """
        :param packages: Packages that triggered the PNFE
        :param steps: Numbered action items for the user
        """
        self.packages = packages
        self.steps = steps

    def to_panel(self) -> Panel:
        for package in self.packages:
            package_name = package.name if isinstance(package, MatchSpec) else package
            body = f"'{package_name}' is available in Anaconda's 'main-x' channel."
            for i, step in enumerate(self.steps, 1):
                body += f"\n\n  {i}. {step}"
            body += "\n\nThen re-run the original command."
        body += f"\n\n{DISABLE_STEP}"
        return Padding(Panel(body, title=self.TITLE, padding=(1, 2)), (1, 0))

    def __str__(self) -> str:
        console = Console(file=StringIO(), width=84, height=25, highlight=False, markup=False)
        console.print(self.to_panel())
        return console.file.getvalue()
