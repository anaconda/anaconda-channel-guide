import responses
from anaconda_channel_guide.plugin import handle_pnfe
from anaconda_channel_guide.channel_check import BASE_URL


FOUND_RESPONSE = {"numpy": ["1.24", "1.25"]}
NOT_FOUND_RESPONSE = {"numpy": []}


@responses.activate
def test_handle_pnfe_configured_not_authenticated():
    """Verifies that a user with main-x configured but not logged in is prompted to log in.
    """
    responses.post(BASE_URL, json=FOUND_RESPONSE, status=200)

    result = handle_pnfe(["numpy"], main_x_configured=True, authenticated=False)
    assert result == "Please login to your account to continue."


@responses.activate
def test_handle_pnfe_configured_not_found():
    """Verifies that when the package is not on main-x, the plugin falls through to default PNFE behavior.
    """
    responses.post(BASE_URL, json=NOT_FOUND_RESPONSE, status=200)

    result = handle_pnfe(["numpy"], main_x_configured=True, authenticated=False)
    assert result is None


@responses.activate
def test_handle_pnfe_not_configured_authenticated():
    """Verifies that a logged-in user without main-x configured is prompted to add the channel.
    """
    responses.post(BASE_URL, json=FOUND_RESPONSE, status=200)

    result = handle_pnfe(["numpy"], main_x_configured=False, authenticated=True)
    assert result == "Please configure your main-x channel to continue."


@responses.activate
def test_handle_pnfe_not_configured_not_authenticated():
    """Verifies that a user without main-x configured and not logged in is prompted to do both.
    """
    responses.post(BASE_URL, json=FOUND_RESPONSE, status=200)

    result = handle_pnfe(["numpy"], main_x_configured=False, authenticated=False)
    assert result == "Please login to your account and configure your main-x channel to continue."


@responses.activate
def test_handle_pnfe_not_configured_not_found():
    """Verifies that when the package is not on main-x, the plugin falls through to default PNFE behavior.
    """
    responses.post(BASE_URL, json=NOT_FOUND_RESPONSE, status=200)

    result = handle_pnfe(["numpy"], main_x_configured=False, authenticated=False)
    assert result is None


@responses.activate
def test_handle_pnfe_fully_setup():
    """Verifies that a fully set up user (authenticated with main-x configured) gets no prompt, even if the package exists on main-x.
    """
    responses.post(BASE_URL, json=FOUND_RESPONSE, status=200)
    result = handle_pnfe(["numpy"], main_x_configured=True, authenticated=True)
    assert result is None