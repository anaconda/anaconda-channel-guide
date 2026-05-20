from __future__ import annotations

from typing import TYPE_CHECKING

from conda.plugins import hookimpl
from conda.plugins.types import CondaExceptionObserver

from anaconda_channel_guide.plugin import handle_pnfe

if TYPE_CHECKING:
    from collections.abc import Iterable

    from conda.plugins.types import CondaExceptionEvent


def on_package_not_found(event: CondaExceptionEvent) -> None:
    # TODO: when sending the info to API does it need name and version?
    main_x_configured = "main-x" in event.channels
    missing_packages = [str(pkg) for pkg in event.exc_value.packages]

    # TODO: get authenticated status from conda
    authenticated = False

    handle_pnfe(missing_packages, main_x_configured, authenticated)


@hookimpl
def conda_exception_observers() -> Iterable[CondaExceptionObserver]:
    yield CondaExceptionObserver(
        name="channel-guide",
        hook=on_package_not_found,
        watch_for={"PackagesNotFoundError"},
    )
