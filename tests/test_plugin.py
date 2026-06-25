import pytest
from anaconda_auth.token import TokenNotFoundError
from conda.base.context import context
from conda.models.match_spec import MatchSpec
from conda.models.records import PackageRecord
from pytest_mock import MockerFixture

from anaconda_channel_guide.box import ChannelGuideBox
from anaconda_channel_guide.hooks import on_package_not_found
from anaconda_channel_guide.plugin import (
    MAIN_X_CHANNEL_NAME,
    MAIN_X_CHANNEL_URL,
    handle_pnfe,
    is_available_on_main_x,
    is_logged_in,
    is_main_x_configured,
)

LOGIN_CMD = "anaconda login"
CONFIG_CMD = "conda config --append channels https://repo.anaconda.cloud/repo/main-x"
SUBDIRS = ("linux-64", "noarch")

PYCHOIR_RECORD = PackageRecord(name="pychoir", version="0.0.30", build="pypi_0", build_number=0)
SUBDIRS = ("linux-64", "noarch")


@pytest.mark.parametrize(
    ("on_main_x", "main_x_configured", "authenticated"),
    [
        (False, True, False),
        (False, False, False),
        (True, True, True),
    ],
)
def test_handle_pnfe_returns_none(
    mocker: MockerFixture,
    on_main_x: bool,
    main_x_configured: bool,
    authenticated: bool,
) -> None:
    """No prompt when packages aren't on main-x, or the user is already set up."""
    mocker.patch("anaconda_channel_guide.plugin.is_available_on_main_x", return_value=on_main_x)

    result = handle_pnfe(
        ["pychoir"],
        main_x_configured=main_x_configured,
        authenticated=authenticated,
        subdirs=SUBDIRS,
    )
    assert result is None


@pytest.mark.parametrize(
    ("main_x_configured", "authenticated", "expected_steps"),
    [
        (True, False, [LOGIN_CMD]),
        (False, True, [CONFIG_CMD]),
        (False, False, [LOGIN_CMD, CONFIG_CMD]),
    ],
)
def test_handle_pnfe_prompts_required_steps(
    mocker: MockerFixture,
    main_x_configured: bool,
    authenticated: bool,
    expected_steps: list[str],
) -> None:
    """When packages are on main-x and setup is incomplete, prompt the missing steps."""
    mocker.patch("anaconda_channel_guide.plugin.is_available_on_main_x", return_value=True)

    result = handle_pnfe(
        ["pychoir"],
        main_x_configured=main_x_configured,
        authenticated=authenticated,
        subdirs=SUBDIRS,
    )
    assert isinstance(result, ChannelGuideBox)
    output = str(result)
    for step in expected_steps:
        assert step in output


@pytest.mark.parametrize("expected", [True, False])
def test_is_logged_in(mocker: MockerFixture, expected: bool) -> None:
    """Verify is_logged_in reflects token state."""
    mock_cls = mocker.patch("anaconda_channel_guide.plugin.TokenInfo")
    mock_cls.load.return_value.expired = not expected
    assert is_logged_in() == expected


def test_is_logged_in_no_token(mocker: MockerFixture) -> None:
    """Verify user is not considered logged in if no token is found."""
    mock_cls = mocker.patch("anaconda_channel_guide.plugin.TokenInfo")
    mock_cls.load.side_effect = TokenNotFoundError("no token")
    assert not is_logged_in()


@pytest.mark.parametrize(
    ("channels", "expected"),
    [
        ((MAIN_X_CHANNEL_NAME,), True),
        (("defaults", MAIN_X_CHANNEL_NAME), True),
        ((f"{MAIN_X_CHANNEL_NAME}/",), True),
        (("defaults", "conda-forge"), False),
        ((), False),
        (None, False),
    ],
)
def test_main_x_configured(
    mocker: MockerFixture,
    channels: tuple[str, ...] | None,
    expected: bool,
) -> None:
    event = mocker.MagicMock()
    event.channels = channels
    assert is_main_x_configured(event) is expected


def test_on_package_not_found_skips_offline(mocker: MockerFixture) -> None:
    """Availability checks are skipped entirely when conda is in offline mode."""
    event = mocker.MagicMock()
    event.offline = True
    mock_handle = mocker.patch("anaconda_channel_guide.hooks.handle_pnfe")
    on_package_not_found(event)
    mock_handle.assert_not_called()


@pytest.mark.parametrize(("query_result", "expected"), [((PYCHOIR_RECORD,), True), ((), False)])
def test_package_found_on_main_x(mocker: MockerFixture, query_result: list, expected: bool) -> None:
    """A non-empty main-x query result reports the package as available (True);
    an empty result reports it as unavailable (False).
    """
    mocker.patch(
        "anaconda_channel_guide.plugin.SubdirData"
    ).query_all.return_value = query_result
    assert is_available_on_main_x(["pychoir"], subdirs=SUBDIRS) is expected


def test_package_record_with_channel(mocker: MockerFixture) -> None:
    """A PackageRecord whose MatchSpec carries a channel is rejected."""
    mock_sd = mocker.patch("anaconda_channel_guide.plugin.SubdirData")
    mock_sd.query_all.return_value = (PYCHOIR_RECORD,)
    assert is_available_on_main_x([PYCHOIR_RECORD], subdirs=SUBDIRS) is False
    mock_sd.query_all.assert_not_called()


def test_query_raises_exception(mocker: MockerFixture) -> None:
    """A failed main-x query is treated as 'not available' rather than crashing."""
    mocker.patch(
        "anaconda_channel_guide.plugin.SubdirData"
    ).query_all.side_effect = Exception()
    assert is_available_on_main_x(["pychoir"], subdirs=SUBDIRS) is False


def test_query_receives_correct_args(mocker: MockerFixture) -> None:
    """Subdirs and channels are forwarded to query_all."""
    mock_sd = mocker.patch("anaconda_channel_guide.plugin.SubdirData")
    mock_sd.query_all.return_value = (PYCHOIR_RECORD,)
    is_available_on_main_x(["pychoir"], subdirs=SUBDIRS)
    mock_sd.query_all.assert_called_once_with(
        MatchSpec("pychoir"), channels=[MAIN_X_CHANNEL_URL], subdirs=SUBDIRS
    )


def test_channel_pinned_spec(mocker: MockerFixture) -> None:
    """Specs pinned to another channel, returns False."""
    mock_sd = mocker.patch("anaconda_channel_guide.plugin.SubdirData")

    assert is_available_on_main_x(["conda-forge::numpy"], subdirs=SUBDIRS) is False
    mock_sd.query_all.assert_not_called()


def test_availability_lookup_uses_index_cache(mocker: MockerFixture) -> None:
    """Use conda's cached repodata instead of refreshing on the PNFE path."""
    seen_use_index_cache = []

    def query_all(
        package: MatchSpec,
        *,
        channels: list[str],
        subdirs: tuple[str, ...],
    ) -> tuple[PackageRecord, ...]:
        assert package == MatchSpec("pychoir")
        assert channels == [MAIN_X_CHANNEL_URL]
        assert subdirs == SUBDIRS
        seen_use_index_cache.append(context.use_index_cache)
        return (PYCHOIR_RECORD,)

    mocker.patch(
        "anaconda_channel_guide.plugin.SubdirData"
    ).query_all.side_effect = query_all

    with context._override("use_index_cache", False):
        assert is_available_on_main_x(["pychoir"], subdirs=SUBDIRS) is True
        assert seen_use_index_cache == [True]
        assert context.use_index_cache is False
