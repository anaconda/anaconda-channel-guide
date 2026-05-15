from anaconda_channel_guide.plugin import handle_pnfe
from conda.plugins.types import CondaExceptionObserver
from conda.plugins import hookimpl

@hookimpl
def conda_exception_observers():
    def on_package_not_found(event):
        print(">>> CHANNEL GUIDE PLUGIN FIRED <<<")
        # print(f"Packages: {event.exc_value.packages}")
        # print(f"Channels: {event.channels}")

        # TODO: when sending the info to API does it need name and version?
        main_x_configured = "main-x" in event.channels
        missing_packages = [str(pkg) for pkg in event.exc_value.packages]

        #TODO: get authenticated status from conda
        authenticated = False

        #TODO: testing purposes only. Needs to be rewrote once API is setup.
        #handle_pnfe(missing_packages, main_x_configured, authenticated)
        message = handle_pnfe(missing_packages, main_x_configured, authenticated)
        if message:
            print(message)

    yield CondaExceptionObserver(
        name="channel-guide",
        hook=on_package_not_found,
        watch_for={"PackagesNotFoundError"},
    )