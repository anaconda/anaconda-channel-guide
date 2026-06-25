from __future__ import annotations

from typing import TYPE_CHECKING

from conda.base.context import context
from conda.common.configuration import PrimitiveParameter
from conda.plugins import hookimpl
from conda.plugins.types import CondaExceptionObserver, CondaSetting

from anaconda_channel_guide.plugin import handle_pnfe, is_logged_in, is_main_x_configured

if TYPE_CHECKING:
    from collections.abc import Iterator

    from conda.plugins.types import CondaExceptionEvent


def on_package_not_found(event: CondaExceptionEvent) -> None:
    if not context.plugins.anaconda_channel_guide:
        return
    # TODO: when sending the info to API does it need name and version?
    main_x_configured = is_main_x_configured(event)
    missing_packages = [str(pkg) for pkg in event.exc_value.packages]
    authenticated = is_logged_in()

    handle_pnfe(missing_packages, main_x_configured, authenticated)


@hookimpl
def conda_exception_observers() -> Iterator[CondaExceptionObserver]:
    yield CondaExceptionObserver(
        name="channel-guide",
        hook=on_package_not_found,
        watch_for={"PackagesNotFoundError"},
    )


@hookimpl
def conda_settings() -> Iterator[CondaSetting]:
    """Return a list of settings that can be configured by the user."""
    yield CondaSetting(
        name="anaconda_channel_guide",
        description="Whether Anaconda Channel Guide is enabled",
        parameter=PrimitiveParameter(True, element_type=bool),
    )
