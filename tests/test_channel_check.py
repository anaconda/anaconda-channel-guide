import responses
from anaconda_channel_guide.channel_check import check_package_availability, BASE_URL

MOCK_RESPONSE = {"numpy": ["1.24", "1.25"], "six": []}


#TODO: what will the real BASE_URL be?

@responses.activate
def test_check_package_availability():
    responses.post(
        BASE_URL,
        json=MOCK_RESPONSE,
        status=200,
    )

    result = check_package_availability(["numpy", "six"])

    assert result == MOCK_RESPONSE


