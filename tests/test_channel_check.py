import pytest
from conda.models.match_spec import MatchSpec
from conda.models.records import PackageRecord
from pytest_mock import MockerFixture

from anaconda_channel_guide.channel_check import (
    MAIN_X_CHANNEL_URL,
    is_available_on_main_x,
)

PYCHOIR_RECORD = PackageRecord(name="pychoir", version="0.0.30", build="pypi_0", build_number=0)
SUBDIRS = ("linux-64", "noarch")


@pytest.mark.parametrize(("query_result", "expected"), [((PYCHOIR_RECORD,), True), ((), False)])
def test_package_found_on_main_x(mocker: MockerFixture, query_result: list, expected: bool) -> None:
    """A non-empty main-x query result reports the package as available (True);
    an empty result reports it as unavailable (False).
    """
    mocker.patch(
        "anaconda_channel_guide.channel_check.SubdirData"
    ).query_all.return_value = query_result
    assert is_available_on_main_x(["pychoir"], subdirs=SUBDIRS) is expected


def test_package_record_with_channel(mocker: MockerFixture) -> None:
    """A PackageRecord whose MatchSpec carries a channel is rejected."""
    mock_sd = mocker.patch("anaconda_channel_guide.channel_check.SubdirData")
    mock_sd.query_all.return_value = (PYCHOIR_RECORD,)
    assert is_available_on_main_x([PYCHOIR_RECORD], subdirs=SUBDIRS) is False
    mock_sd.query_all.assert_not_called()


def test_query_raises_exception(mocker: MockerFixture) -> None:
    """A failed main-x query is treated as 'not available' rather than crashing."""
    mocker.patch(
        "anaconda_channel_guide.channel_check.SubdirData"
    ).query_all.side_effect = Exception()
    assert is_available_on_main_x(["pychoir"], subdirs=SUBDIRS) is False


def test_query_receives_correct_args(mocker: MockerFixture) -> None:
    """Subdirs and channels are forwarded to query_all."""
    mock_sd = mocker.patch("anaconda_channel_guide.channel_check.SubdirData")
    mock_sd.query_all.return_value = (PYCHOIR_RECORD,)
    is_available_on_main_x(["pychoir"], subdirs=SUBDIRS)
    mock_sd.query_all.assert_called_once_with(
        MatchSpec("pychoir"), channels=[MAIN_X_CHANNEL_URL], subdirs=SUBDIRS
    )


def test_channel_pinned_spec(mocker: MockerFixture) -> None:
    """Specs pinned to another channel, returns False."""
    mock_sd = mocker.patch("anaconda_channel_guide.channel_check.SubdirData")

    assert is_available_on_main_x(["conda-forge::numpy"], subdirs=SUBDIRS) is False
    mock_sd.query_all.assert_not_called()
