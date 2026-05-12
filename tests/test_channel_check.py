import responses
from anaconda_channel_guide.channel_check import is_package_on_main_x, BASE_URL

MOCK_RESPONSE = {"numpy": ["1.24", "1.25"], "six": []}


@responses.activate
def test_is_package_on_main_x():
    """Verifies that is_package_on_main_x posts the package list and returns the parsed API response.
    """
    # TODO: what will the real BASE_URL be?
    responses.post(
        BASE_URL,
        json=MOCK_RESPONSE,
        status=200,
    )

    result = is_package_on_main_x(["numpy", "six"])

    assert result == MOCK_RESPONSE


