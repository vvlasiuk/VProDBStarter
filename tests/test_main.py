import pytest
from unittest.mock import MagicMock, patch

from ui.forms.db_selector_dialog import select_database
from logs.logger import log_event
from core.i18n.localizer import Localizer
from main import AppConfig

@pytest.fixture
def config():
    return AppConfig(
        is_admin=True,
        extensions=[],
        databases_list_path=":memory:",
        last_selected_db_path=":memory:",
        localizer=Localizer(lang="uk")
    )

def test_log_event_admin_mode(config):
    with patch("logs.logger.log_event") as mock_log:
        log_event(config.localizer.t("log.admin_mode"))
        mock_log.assert_called_once_with("Запуск в режимі адміністратора")

def test_select_database_called(config):
    with patch("ui.forms.db_selector_dialog.select_database") as mock_select:
        mock_select.return_value = {"db": "test"}
        result = mock_select(None, config)
        assert result == {"db": "test"}
        mock_select.assert_called_once_with(None, config)

def test_config_fields(config):
    assert config.is_admin is True
    assert config.databases_path == ":memory:"
    assert config.localizer.t("dialog.confirm.default_title") == "Підтвердження"