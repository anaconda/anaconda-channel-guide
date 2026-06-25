from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from anaconda_channel_guide.hooks import conda_settings, on_package_not_found

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


def test_conda_settings() -> None:
    """
    Ensure the correct conda settings are returned
    """
    settings = list(conda_settings())

    assert len(settings) == 1
    assert settings[0].name == "anaconda_channel_guide"
    assert settings[0].description == "Whether Anaconda Channel Guide is enabled"
    assert settings[0].parameter.default.value is True


@pytest.mark.parametrize(
    "enabled",
    [pytest.param(True, id="enabled"), pytest.param(False, id="disabled")],
)
def test_enable_disable_plugin(enabled: bool, mocker: MockerFixture) -> None:
    """
    Make sure that nothing is returned when the plugin is disabled via settings
    """
    mocker.patch("anaconda_channel_guide.hooks.context.plugins.anaconda_channel_guide", enabled)
    event = mocker.MagicMock()
    mock_handle = mocker.patch("anaconda_channel_guide.hooks.handle_pnfe")
    on_package_not_found(event)
    assert mock_handle.called is enabled
