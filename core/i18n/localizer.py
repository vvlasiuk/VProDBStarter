# core/i18n/localizer.py

import json
import os

class Localizer:
    def __init__(self, lang=None):
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        settings_path = os.path.join(project_root, "config", "settings.json")

        if lang is None:
            with open(settings_path, "r", encoding="utf-8") as f:
                settings = json.load(f)
            lang_code = settings.get("language", "uk")
        else:
            lang_code = lang

        lang_path = os.path.join(project_root, "config", "lang", f"{lang_code}.json")

        with open(lang_path, "r", encoding="utf-8") as f:
            self.translations = json.load(f)

    def t(self, key: str) -> str:
        parts = key.split(".")
        value = self.translations
        try:
            for part in parts:
                value = value[part]
            return value
        except (KeyError, TypeError):
            print(f"[WARN] Відсутній переклад для ключа: {key}")
            return f"[{key}]"