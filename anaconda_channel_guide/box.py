from __future__ import annotations

from io import StringIO
from typing import TYPE_CHECKING

from conda.models.match_spec import MatchSpec
from rich.console import Console
from rich.padding import Padding
from rich.panel import Panel

# Cap rendered box width so it stays readable on wide terminals.
MAX_WIDTH = 84

LOGIN_STEP = "Log in:\n\n    $ anaconda login"
CONFIG_STEP = (
    "Add the 'main-x' channel:\n\n"
    "    $ conda config --append channels https://repo.anaconda.cloud/repo/main-x"
)
DISABLE_STEP = (
    "To disable these notifications, please run:\n\n"
    "    $ conda config --set plugins.anaconda_channel_guide false"
)
TOS_MESSAGE = (
    "By accessing main-x, you agree to Anaconda's Terms of Service:\n\n"
    "    https://www.anaconda.com/legal/terms-of-service"
)


if TYPE_CHECKING:
    from collections.abc import Iterable


class ChannelGuideBox:
    """Reusable Rich panel for channel guide prompts."""

    TITLE = "Anaconda Channel Guide"

    def __init__(self, packages: Iterable[str | MatchSpec], steps: list[str]) -> None:
        """
        :param packages: Packages that triggered the PNFE
        :param steps: Numbered action items for the user
        """
        self.packages = packages
        self.steps = steps

    def to_panel(self) -> Padding:
        names = [pkg.name if isinstance(pkg, MatchSpec) else pkg for pkg in self.packages]
        if len(names) == 1:
            intro = f"'{names[0]}' is available in Anaconda's 'main-x' channel."
        elif len(names) == 2:
            intro = f"'{names[0]}' and '{names[1]}' are available in Anaconda's 'main-x' channel."
        else:
            *rest, last = names
            joined = ", ".join(f"'{n}'" for n in rest)
            intro = f"{joined}, and '{last}' are available in Anaconda's 'main-x' channel."

        body = intro
        for i, step in enumerate(self.steps, 1):
            body += f"\n\n  {i}. {step}"
        body += f"\n\nThen re-run the original command.\n\n{TOS_MESSAGE}\n\n{DISABLE_STEP}"
        return Padding(Panel(body, title=self.TITLE, padding=(1, 2)), (1, 0))

    def to_hint_text(self) -> str:
        """Return the guide message as plain text, without Rich panel formatting."""
        return self.to_panel().renderable.renderable

    def __str__(self) -> str:
        console = Console(file=StringIO(), width=MAX_WIDTH)
        console.print(self.to_panel())
        return console.file.getvalue()
