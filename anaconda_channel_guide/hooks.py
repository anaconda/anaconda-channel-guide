from conda.plugins.types import CondaExceptionObserver
from conda.plugins import hookimpl

@hookimpl
def conda_exception_observers():
    def on_package_not_found(event):
        print(">>> CHANNEL GUIDE PLUGIN FIRED <<<")
        print(f"Packages: {event.exc_value.packages}")
        print(f"Channels: {event.channels}")

    yield CondaExceptionObserver(
        name="channel-guide",
        hook=on_package_not_found,
        watch_for={"PackagesNotFoundError"},
    )