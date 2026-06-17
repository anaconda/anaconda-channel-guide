import pytest
from conda.models.records import PackageRecord
from pytest_mock import MockerFixture

from anaconda_channel_guide.channel_check import (
    MAIN_X_CHANNEL_URL,
    is_available_on_main_x,
)


@pytest.mark.parametrize(("query_result", "expected"), [(["rec"], True), ([], False)])
def test_is_available_on_main_x(mocker: MockerFixture, query_result: list, expected: bool) -> None:
    """A non-empty main-x query result reports the package as available (True);
    an empty result reports it as unavailable (False).
    """
    mocker.patch(
        "anaconda_channel_guide.channel_check.SubdirData"
    ).query_all.return_value = query_result
    assert is_available_on_main_x(["pychoir"]) is expected


def test_package_record_returns_false(mocker: MockerFixture) -> None:
    """A PackageRecord input is rejected by the guard."""
    mocker.patch("anaconda_channel_guide.channel_check.SubdirData")
    record = PackageRecord(name="pychoir", version="0.0.30", build="pypi_0", build_number=0)
    assert is_available_on_main_x([record]) is False


def test_query_failure_returns_false(mocker: MockerFixture) -> None:
    """A failed main-x query is treated as 'not available' rather than crashing."""
    mocker.patch(
        "anaconda_channel_guide.channel_check.SubdirData"
    ).query_all.side_effect = Exception()
    assert is_available_on_main_x(["pychoir"]) is False


def test_platform_specific_hit(mocker: MockerFixture) -> None:
    """Package found for the user's platform reports available."""
    mock_sd = mocker.patch("anaconda_channel_guide.channel_check.SubdirData")
    mock_sd.query_all.return_value = ["rec"]

    assert is_available_on_main_x(["numpy"], subdirs=("linux-64", "noarch")) is True
    mock_sd.query_all.assert_called_once_with(
        "numpy", channels=[MAIN_X_CHANNEL_URL], subdirs=("linux-64", "noarch")
    )


def test_noarch_hit(mocker: MockerFixture) -> None:
    """A noarch-only package is found when noarch is in the subdirs."""
    mock_sd = mocker.patch("anaconda_channel_guide.channel_check.SubdirData")
    mock_sd.query_all.return_value = ["rec"]

    assert is_available_on_main_x(["pychoir"], subdirs=("osx-arm64", "noarch")) is True
    mock_sd.query_all.assert_called_once_with(
        "pychoir", channels=[MAIN_X_CHANNEL_URL], subdirs=("osx-arm64", "noarch")
    )


def test_platform_specific_miss(mocker: MockerFixture) -> None:
    """Package exists on main-x but not for this platform — reports unavailable."""
    mock_sd = mocker.patch("anaconda_channel_guide.channel_check.SubdirData")
    mock_sd.query_all.return_value = []

    assert is_available_on_main_x(["numpy"], subdirs=("osx-arm64", "noarch")) is False
    mock_sd.query_all.assert_called_once_with(
        "numpy", channels=[MAIN_X_CHANNEL_URL], subdirs=("osx-arm64", "noarch")
    )
