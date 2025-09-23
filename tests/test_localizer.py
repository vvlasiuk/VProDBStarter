import os
import json
import tempfile
import pytest
from core.i18n.localizer import Localizer

@pytest.fixture
def lang_json(tmp_path):
    # Створюємо тимчасовий файл локалізації
    lang_data = {
        "dialog": {
            "confirm": {
                "default_title": "Підтвердження",
                "yes": "ТАК"
            }
        },
        "log": {
            "admin_mode": "Запуск в режимі адміністратора"
        }
    }
    lang_file = tmp_path / "uk.json"
    with open(lang_file, "w", encoding="utf-8") as f:
        json.dump(lang_data, f)
    return lang_file

@pytest.fixture
def settings_json(tmp_path):
    # Створюємо тимчасовий settings.json
    settings_data = {"language": "uk"}
    settings_file = tmp_path / "settings.json"
    with open(settings_file, "w", encoding="utf-8") as f:
        json.dump(settings_data, f)
    return settings_file

@pytest.fixture
def localizer(monkeypatch, lang_json, settings_json):
    # Підміняємо шляхи до файлів у Localizer
    project_root = lang_json.parent.parent
    monkeypatch.setattr(os.path, "abspath", lambda x: str(project_root))
    monkeypatch.setattr(os.path, "dirname", lambda x: str(project_root / "core" / "i18n"))
    # Підміняємо open для settings.json і lang.json
    orig_open = open
    def fake_open(path, *args, **kwargs):
        if "settings.json" in path:
            return orig_open(settings_json, *args, **kwargs)
        if "uk.json" in path:
            return orig_open(lang_json, *args, **kwargs)
        return orig_open(path, *args, **kwargs)
    monkeypatch.setattr("builtins.open", fake_open)
    return Localizer(lang="uk")

def test_translation_found(localizer):
    assert localizer.t("dialog.confirm.default_title") == "Підтвердження"
    assert localizer.t("dialog.confirm.yes") == "ТАК"
    assert localizer.t("log.admin_mode") == "Запуск в режимі адміністратора"

def test_translation_missing(localizer, capsys):
    result = localizer.t("dialog.confirm.no_such_key")
    captured = capsys.readouterr()
    assert "[WARN] Відсутній переклад для ключа: dialog.confirm.no_such_key" in captured.out
    assert result == "[dialog.confirm.no_such_key]"

def test_nested_translation(localizer):
    assert localizer.t("dialog.confirm.default_title") == "Підтвердження"

def test_language_from_settings(monkeypatch, lang_json, settings_json):
    # Перевірка, що мова береться з settings.json, якщо lang не передано
    project_root = lang_json.parent.parent
    monkeypatch.setattr(os.path, "abspath", lambda x: str(project_root))
    monkeypatch.setattr(os.path, "dirname", lambda x: str(project_root / "core" / "i18n"))
    orig_open = open
    def fake_open(path, *args, **kwargs):
        if "settings.json" in path:
            return orig_open(settings_json, *args, **kwargs)
        if "uk.json" in path:
            return orig_open(lang_json, *args, **kwargs)
        return orig_open(path, *args, **kwargs)
    monkeypatch.setattr("builtins.open", fake_open)
    loc = Localizer()
    assert loc.t("dialog.confirm.default_title") == "Підтвердження"