from __future__ import annotations

from typing import TYPE_CHECKING

from conda.models.match_spec import MatchSpec
from rich.console import Console

# Cap rendered box width so it stays readable on wide terminals.
MAX_WIDTH = 84

LOGIN_STEP = "Log in:\n    $ anaconda login"
CONFIG_STEP = (
    "Add the 'main-x' channel:\n"
    "    $ conda config --append channels https://repo.anaconda.cloud/repo/main-x"
)
DISABLE_STEP = (
    "To disable these notifications, please run:\n"
    "    $ conda config --set plugins.anaconda_channel_guide false"
)
TOS_MESSAGE = (
    "By accessing main-x, you agree to Anaconda's Terms of Service:\n"
    "    https://www.anaconda.com/legal/terms/terms-of-service"
)


if TYPE_CHECKING:
    from collections.abc import Iterable


class ChannelGuideBox:
    """Plain-text channel guide message for PNFE remediation."""

    TITLE = "Anaconda Channel Guide"

    def __init__(self, packages: Iterable[str | MatchSpec], steps: list[str]) -> None:
        """
        :param packages: Packages that triggered the PNFE
        :param steps: Numbered action items for the user
        """
        self.packages = packages
        self.steps = steps

    def _intro_line(self) -> str:
        names = [pkg.name if isinstance(pkg, MatchSpec) else pkg for pkg in self.packages]
        if len(names) == 1:
            return f"'{names[0]}' is available in Anaconda's 'main-x' channel."
        if len(names) == 2:
            return f"'{names[0]}' and '{names[1]}' are available in Anaconda's 'main-x' channel."
        *rest, last = names
        joined = ", ".join(f"'{n}'" for n in rest)
        return f"{joined}, and '{last}' are available in Anaconda's 'main-x' channel."

    @staticmethod
    def _render_block(block: str, prefix: str = "", indent: str = "     ") -> list[str]:
        title, *command_lines = block.splitlines()
        return [f"{prefix}{title}", *(f"{indent}{c.strip()}" for c in command_lines)]

    def plain_text_message(self) -> str:
        width = self._width()
        steps = [*self.steps, "Re-run the original command."]

        parts = [f" {self.TITLE} ".center(width, "-"), self._intro_line()]
        for i, step in enumerate(steps, 1):
            parts += self._render_block(step, prefix=f"     {i}. ", indent="          ")
        parts.append("-" * width)
        for block in (TOS_MESSAGE, DISABLE_STEP):
            parts += self._render_block(block)

        return "\n" + "\n\n".join(parts)

    def to_hint_text(self) -> str:
        """Return the guide message for conda's CondaErrorHint API."""
        return self.plain_text_message()

    @staticmethod
    def _width() -> int:
        """Fit the real terminal width, capped at MAX_WIDTH so it stays readable.

        Rich is used only to detect the terminal size here, not to render the box.
        """
        return min(Console().size.width, MAX_WIDTH)
