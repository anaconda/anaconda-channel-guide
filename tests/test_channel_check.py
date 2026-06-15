import pytest
from conda.models.records import PackageRecord
from pytest_mock import MockerFixture

from anaconda_channel_guide.channel_check import (
    get_packages_on_main_x,
)


@pytest.mark.parametrize(("query_result", "expected"), [(["rec"], True), ([], False)])
def test_get_packages_on_main_x(mocker: MockerFixture, query_result: list, expected: bool) -> None:
    """A non-empty main-x query result reports the package as available (True);
    an empty result reports it as unavailable (False).
    """
    mocker.patch(
        "anaconda_channel_guide.channel_check.SubdirData"
    ).query_all.return_value = query_result
    assert get_packages_on_main_x(["pychoir"]) is expected


def test_package_record_returns_false(mocker: MockerFixture) -> None:
    """A PackageRecord input is rejected by the guard."""
    mocker.patch("anaconda_channel_guide.channel_check.SubdirData")
    record = PackageRecord(name="pychoir", version="0.0.30", build="pypi_0", build_number=0)
    assert get_packages_on_main_x([record]) is False
