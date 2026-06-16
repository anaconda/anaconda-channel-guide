import pytest
from conda.models.records import PackageRecord
from pytest_mock import MockerFixture

from anaconda_channel_guide.channel_check import (
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
