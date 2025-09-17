# from config.config_manager import load_config, save_config
# from core.db.connection import test_connection
# from core.db.initializer import initialize_database
from ui.forms.db_selector_dialog import select_database
from logs.logger import log_event
from dataclasses import dataclass

from PyQt6.QtWidgets import QApplication
import sys
import importlib
import importlib.util
import os
import argparse
from core.config_paths import CONFIG_DIR
from core.i18n.localizer import Localizer

@dataclass
class AppConfig:
    is_admin: bool
    extensions: list
    config_path: str
    last_selected_path: str
    localizer: Localizer

def load_extensions() -> list:
    extensions = []
    ext_dir = os.path.join(os.path.dirname(__file__), "extensions")
    for root, dirs, files in os.walk(ext_dir):
        for fname in files:
            if fname.endswith(".py") and fname != "__init__.py":
                rel_path = os.path.relpath(os.path.join(root, fname), os.path.dirname(__file__))
                mod_name = rel_path[:-3].replace(os.sep, ".")
                spec = importlib.util.spec_from_file_location(mod_name, os.path.join(root, fname))
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                extensions.append(mod)
    return extensions

def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Конфігуратор ERP-модуля")
    parser.add_argument(
        '--mode',
        choices=['admin', 'user'],
        required=True,
        help='Режим запуску: admin або user'
    )
    return parser.parse_args()

def main():
    args = get_args()
    extensions = load_extensions()

    app = QApplication(sys.argv)
    app.setStyle("Fusion") #WindowsVista

    config = AppConfig(
        is_admin=(args.mode == "admin"),
        extensions=extensions,
        config_path=str(CONFIG_DIR / "databases.json"),
        last_selected_path=str(CONFIG_DIR / "last_selected_db.json"),
        localizer=Localizer()
    )

    if config.is_admin:
        log_event("Запуск в режимі адміністратора")

    select_database(None, config)

    return

if __name__ == "__main__":
    main()