from config.config_manager import load_config, save_config
from core.db.connection import test_connection
from core.db.initializer import initialize_database
from ui.forms.db_config_dialog import show_config_dialog
from ui.forms.db_selector_dialog import select_database
from logs.logger import log_event

from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
import sys

def launch_main_ui():
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle("VLAS PRO: Управлінський облік (client).")
    layout = QVBoxLayout()
    layout.addWidget(QLabel("✅ Підключення до бази даних успішне."))
    layout.addWidget(QLabel("🧠 Головний інтерфейс буде тут..."))
    window.setLayout(layout)
    window.show()
    app.exec()

def main():
    log_event("log.bootstrap.start")

    if not QApplication.instance():
        app = QApplication(sys.argv)
        app.setStyle("WindowsVista") #Fusion

    cfg = select_database()
    if cfg:
        log_event(f"✅ Базу обрано: {cfg['database']} на {cfg['server']}")
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
        cfg = show_config_dialog()
        if cfg:
            save_config(cfg)
            initialize_database(cfg)
            log_event("🛠️ База створена")
        else:
            log_event("❌ Вихід без конфігурації")
            return

    launch_main_ui()

if __name__ == "__main__":
    main()