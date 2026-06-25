from __future__ import annotations

from typing import TYPE_CHECKING

from conda.base.context import context
from conda.plugins import hookimpl
from conda.plugins.types import CondaExceptionObserver, CondaPreCommand

from anaconda_channel_guide.plugin import handle_pnfe, is_logged_in, is_main_x_configured
from anaconda_channel_guide.prefetch import prefetch_main_x_repodata

if TYPE_CHECKING:
    from collections.abc import Iterable

    from conda.plugins.types import CondaExceptionEvent


def on_package_not_found(event: CondaExceptionEvent) -> None:
    #  Return immediately in offline mode — availability checks require network access.
    if event.offline:
        return
    main_x_configured = is_main_x_configured(event)
    authenticated = is_logged_in()

    handle_pnfe(event.exc_value.packages, main_x_configured, authenticated, subdirs=context.subdirs)


@hookimpl
def conda_exception_observers() -> Iterable[CondaExceptionObserver]:
    yield CondaExceptionObserver(
        name="channel-guide",
        hook=on_package_not_found,
        watch_for={"PackagesNotFoundError"},
    )


@hookimpl
def conda_pre_commands() -> Iterable[CondaPreCommand]:
    yield CondaPreCommand(
        name="channel-guide-main-x-prefetch",
        action=prefetch_main_x_repodata,
        run_for={"create", "env_create", "env_update", "install"},
    )
