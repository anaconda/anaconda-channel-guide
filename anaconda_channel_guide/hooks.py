from __future__ import annotations

from typing import TYPE_CHECKING

from conda.plugins import hookimpl
from conda.plugins.types import CondaExceptionObserver

from anaconda_channel_guide.box import render_channel_guide
from anaconda_channel_guide.plugin import handle_pnfe, is_logged_in, is_main_x_configured

if TYPE_CHECKING:
    from collections.abc import Iterable

    from conda.plugins.types import CondaExceptionEvent


def on_package_not_found(event: CondaExceptionEvent) -> None:
    # TODO: when sending the info to API does it need name and version?
    main_x_configured = is_main_x_configured(event)
    missing_packages = [str(pkg) for pkg in event.exc_value.packages]
    authenticated = is_logged_in()

    result = handle_pnfe(missing_packages, main_x_configured, authenticated)
    if result:
        render_channel_guide(result)


@hookimpl
def conda_exception_observers() -> Iterable[CondaExceptionObserver]:
    yield CondaExceptionObserver(
        name="channel-guide",
        hook=on_package_not_found,
        watch_for={"PackagesNotFoundError"},
    )
