import pytest
from unittest.mock import MagicMock, patch
import sys
import os
from ui.forms.db_selector_dialog import select_database
import logs.logger 
# import log_event
from core.i18n.localizer import Localizer
from main import AppConfig, load_extensions, get_args

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
        logs.logger.log_event(config.localizer.t("log.admin_mode"))
        mock_log.assert_called_once_with("Запуск в режимі адміністратора")

def test_select_database_called(config):
    with patch("ui.forms.db_selector_dialog.select_database") as mock_select:
        mock_select.return_value = {"db": "test"}
        result = mock_select(None, config)
        assert result == {"db": "test"}
        mock_select.assert_called_once_with(None, config)

def test_appconfig_fields(config):
    assert config.is_admin is True
    assert config.extensions == []
    assert config.databases_list_path == ":memory:"
    assert config.last_selected_db_path == ":memory:"
    assert config.localizer is not None
    assert config.localizer.t("dialog.confirm.default_title") == "Підтвердження"

def test_load_extensions_empty(tmp_path, monkeypatch):
    # Підмінити extensions на порожню папку
    ext_dir = tmp_path / "extensions"
    ext_dir.mkdir()
    monkeypatch.setattr(os.path, "dirname", lambda _: str(tmp_path))
    monkeypatch.setattr(os, "walk", lambda d: [(str(ext_dir), [], [])])
    assert load_extensions() == []    

def test_get_args_admin(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["main.py", "--mode", "admin"])
    args = get_args()
    assert args.mode == "admin"

def test_get_args_user(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["main.py", "--mode", "user"])
    args = get_args()
    assert args.mode == "user"    

def test_main_admin(monkeypatch):
    # Мокаємо всі зовнішні залежності
    monkeypatch.setattr(sys, "argv", ["main.py", "--mode", "admin"])
    with patch("main.load_extensions", return_value=[]), \
         patch("main.select_database") as mock_select, \
         patch("main.log_event") as mock_log, \
         patch("main.Localizer", return_value=MagicMock()), \
         patch("main.QApplication") as mock_app:
        from main import main
        main()
        mock_log.assert_called_once()
        mock_select.assert_called_once()    

def test_main_user(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["main.py", "--mode", "user"])
    with patch("main.load_extensions", return_value=[]), \
         patch("main.select_database") as mock_select, \
         patch("main.log_event") as mock_log, \
         patch("main.Localizer", return_value=MagicMock()), \
         patch("main.QApplication") as mock_app:
        from main import main
        main()
        mock_log.assert_not_called()
        mock_select.assert_called_once()        