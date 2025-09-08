from html import parser
from config.config_manager import load_config, save_config
from core.db.connection import test_connection
from core.db.initializer import initialize_database
# from ui.forms.db_config_dialog import show_config_dialog
from ui.forms.db_selector_dialog import select_database
from logs.logger import log_event

from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
import sys
import importlib
import importlib.util
import os
import argparse

def launch_main_ui(extensions):
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle("VLAS PRO: Управлінський облік (client).")
    layout = QVBoxLayout()
    layout.addWidget(QLabel("✅ Підключення до бази даних успішне."))
    layout.addWidget(QLabel("🧠 Головний інтерфейс буде тут..."))
    window.setLayout(layout)

    # Викликаємо хуки розширень для UI
    for ext in extensions:
        if hasattr(ext, "on_app_start"):
            ext.on_app_start(app, window)

    window.show()
    app.exec()

def load_extensions():
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

def main():

    parser = argparse.ArgumentParser(description="Конфігуратор ERP-модуля")
    parser.add_argument(
        '--mode',
        choices=['admin', 'user'],
        required=True,
        help='Режим запуску: admin або user'
    )

    args = parser.parse_args()

    extensions = load_extensions()

    if not QApplication.instance():
        app = QApplication(sys.argv)
        app.setStyle("Fusion") #WindowsVista

    app.setProperty("mode_admin", args.mode == "admin")

    if app.property("mode_admin"):
        log_event("Запуск в режимі адміністратора")
    else:
        log_event("Запуск в режимі користувача")

    cfg = select_database(None, app, extensions)
    if cfg:
        log_event(f"✅ Базу обрано: {cfg['database']} на {cfg['server']}")
        for ext in extensions:
            if hasattr(ext, "on_database_selected"):
                ext.on_database_selected(cfg)   
    else:
        log_event("❌ Базу не обрано — вихід")
        return

    cfg = load_config()
    if not cfg:
        return

        log_event("⚠️ Конфігурація відсутня — відкриваємо діалог")
        cfg = show_config_dialog()
        if cfg:
            save_config(cfg)
            log_event("📥 Конфігурація збережена")
        else:
            log_event("❌ Немає конфігурації — вихід")
            return

    if test_connection(cfg):
        log_event("✅ Підключення успішне")
    else:
        log_event("❌ Підключення не вдалося — повторне введення")
        # cfg = show_config_dialog()
        # if cfg:
        #     save_config(cfg)
        #     initialize_database(cfg)
        #     log_event("🛠️ База створена")
        # else:
        #     log_event("❌ Вихід без конфігурації")
        #     return

    launch_main_ui(extensions)

if __name__ == "__main__":
    main()