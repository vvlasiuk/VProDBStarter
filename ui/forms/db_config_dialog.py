from PyQt6.QtWidgets import QDialog, QLineEdit, QFormLayout, QPushButton, QHBoxLayout, QApplication, QMessageBox
import sys
from core.i18n.localizer import Localizer
import json
from pathlib import Path
import uuid
from core.config_paths import CONFIG_DIR
from core.db.initializer import initialize_database, delete_database

def show_create_db_dialog(parent=None):
    localizer = Localizer()
    dialog = QDialog(parent)
    dialog.setWindowTitle(localizer.t("form.config.title"))

    layout = QFormLayout()

    name = QLineEdit()
    server = QLineEdit()
    port = QLineEdit()
    database = QLineEdit()
    user = QLineEdit()
    password = QLineEdit()

    password.setEchoMode(QLineEdit.EchoMode.Password)

    layout.addRow(localizer.t("label.name"), name)
    layout.addRow(localizer.t("label.server"), server)
    layout.addRow(localizer.t("label.port"), port)
    layout.addRow(localizer.t("label.database"), database)
    layout.addRow(localizer.t("label.user_sa"), user)
    layout.addRow(localizer.t("label.password_sa"), password)

    # --- Додаємо кнопки "Зберегти" та "Відмінити" поруч ---
    btn_layout = QHBoxLayout()
    btn_save = QPushButton(localizer.t("button.save"))
    btn_cancel = QPushButton(localizer.t("button.cancel"))
    btn_layout.addWidget(btn_save)
    btn_layout.addWidget(btn_cancel)
    layout.addRow(btn_layout)

    dialog.setLayout(layout)

    CONFIG_PATH = CONFIG_DIR / "databases.json"

    def on_save():
        db_cfg = {
            "server": server.text(),
            "port": port.text(),
            "database": database.text(),
            "user": user.text(),
            "password": password.text()
        }
        try:
            initialize_database(db_cfg)
        except Exception as e:
            QMessageBox.critical(dialog, localizer.t("form.config.title"), f"Помилка створення бази: {e}")
            return

        # Зчитуємо існуючі бази
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                databases = json.load(f)
        else:
            databases = {}

        db_name = name.text()
        # Додаємо/оновлюємо запис
        databases[db_name] = {
            "id": str(uuid.uuid4()),
            "server": server.text(),
            "port": port.text(),
            "database": database.text(),
            "user": "Адміністратор"
            # Пароль не зберігаємо тут!
        }

        # Записуємо у файл
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(databases, f, ensure_ascii=False, indent=2)

        dialog.accept()

    def on_cancel():
        dialog.reject()

    btn_save.clicked.connect(on_save)
    btn_cancel.clicked.connect(on_cancel)

    if dialog.exec():
        return {
            "server": server.text(),
            "port": port.text(),
            "database": database.text(),
            "user": user.text(),
            "password": password.text()
        }
    return None

def show_edit_config_dialog(parent=None, db_name=""):
    localizer = Localizer()
    dialog = QDialog(parent)
    dialog.setWindowTitle(localizer.t("form.config.title"))

    layout = QFormLayout()

    server = QLineEdit()
    port = QLineEdit()
    database = QLineEdit()

    layout.addRow(localizer.t("label.server"), server)
    layout.addRow(localizer.t("label.port"), port)
    layout.addRow(localizer.t("label.database"), database)

    # --- Додаємо кнопки "Зберегти" та "Відмінити" поруч ---
    btn_layout = QHBoxLayout()
    btn_save = QPushButton(localizer.t("button.save"))
    btn_cancel = QPushButton(localizer.t("button.cancel"))
    btn_layout.addWidget(btn_save)
    btn_layout.addWidget(btn_cancel)
    layout.addRow(btn_layout)

    dialog.setLayout(layout)

    CONFIG_PATH = CONFIG_DIR / "databases.json"

    def on_save():
        db_cfg = {
            "server": server.text(),
            "port": port.text(),
            "database": database.text()
        }

        # Зчитуємо існуючі бази
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                databases = json.load(f)
        else:
            databases = {}
        # Оновлюємо дані для db_name, якщо такий є
        if db_name and db_name in databases:
            databases[db_name]["server"] = db_cfg["server"]
            databases[db_name]["port"] = db_cfg["port"]
            databases[db_name]["database"] = db_cfg["database"]

            # Записуємо у файл
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(databases, f, ensure_ascii=False, indent=2)
        dialog.accept()  # ← ДОДАЙТЕ ЦЕ

    def on_cancel():
        dialog.reject()

    btn_save.clicked.connect(on_save)
    btn_cancel.clicked.connect(on_cancel)

    # Перед dialog.exec()
    if db_name and CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            databases = json.load(f)
        if db_name in databases:
            db = databases[db_name]
            server.setText(db.get("server", ""))
            port.setText(db.get("port", ""))
            database.setText(db.get("database", ""))

    if dialog.exec():
        return {
            "server": server.text(),
            "port": port.text(),
            "database": database.text()
        }
    return None

def show_add_config_dialog(parent=None):
    localizer = Localizer()
    dialog = QDialog(parent)
    dialog.setWindowTitle(localizer.t("form.config.title"))

    layout = QFormLayout()

    name = QLineEdit()
    server = QLineEdit()
    port = QLineEdit()
    database = QLineEdit()

    layout.addRow(localizer.t("label.name"), name)  
    layout.addRow(localizer.t("label.server"), server)
    layout.addRow(localizer.t("label.port"), port)
    layout.addRow(localizer.t("label.database"), database)

    # --- Додаємо кнопки "Зберегти" та "Відмінити" поруч ---
    btn_layout = QHBoxLayout()
    btn_save = QPushButton(localizer.t("button.save"))
    btn_cancel = QPushButton(localizer.t("button.cancel"))
    btn_layout.addWidget(btn_save)
    btn_layout.addWidget(btn_cancel)
    layout.addRow(btn_layout)

    dialog.setLayout(layout)

    CONFIG_PATH = CONFIG_DIR / "databases.json"

    db_name = ""

    def on_save():
        
        db_cfg = {
            "server": server.text(),
            "port": port.text(),
            "database": database.text()
        }

        # Зчитуємо існуючі бази
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                databases = json.load(f)
        else:
            databases = {}
            
        db_name = name.text()
        if db_name:
            databases[db_name] = {
                "id": str(uuid.uuid4()),
                "server": db_cfg["server"],
                "port": db_cfg["port"],
                "database": db_cfg["database"]
                # "name": db_name, 
            }
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(databases, f, ensure_ascii=False, indent=2)
            dialog.accept()

    def on_cancel():
        dialog.reject()

    btn_save.clicked.connect(on_save)
    btn_cancel.clicked.connect(on_cancel)

    # # Перед dialog.exec()
    # if db_name and CONFIG_PATH.exists():
    #     with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    #         databases = json.load(f)
    #     if db_name in databases:
    #         db = databases[db_name]
    #         server.setText(db.get("server", ""))
    #         port.setText(db.get("port", ""))
    #         database.setText(db.get("database", ""))

    if dialog.exec():
        return {
            "name": name.text(),
            "server": server.text(),
            "port": port.text(),
            "database": database.text()
        }
    return None

def show_delete_db_dialog(parent=None, db_name=""):
    localizer = Localizer()
    dialog = QDialog(parent)
    dialog.setWindowTitle(localizer.t("form.config.title"))

    layout = QFormLayout()

    name = QLineEdit()
    server = QLineEdit()
    port = QLineEdit()
    database = QLineEdit()
    user = QLineEdit()
    password = QLineEdit()

    name.setDisabled(True)
    server.setDisabled(True)
    port.setDisabled(True)
    database.setDisabled(True)

    password.setEchoMode(QLineEdit.EchoMode.Password)

    layout.addRow(localizer.t("label.name"), name)
    layout.addRow(localizer.t("label.server"), server)
    layout.addRow(localizer.t("label.port"), port)
    layout.addRow(localizer.t("label.database"), database)
    layout.addRow(localizer.t("label.user_sa"), user)
    layout.addRow(localizer.t("label.password_sa"), password)

    # --- Додаємо кнопки "Зберегти" та "Відмінити" поруч ---
    btn_layout = QHBoxLayout()
    btn_delete = QPushButton(localizer.t("button.delete"))
    btn_cancel = QPushButton(localizer.t("button.cancel"))
    btn_layout.addWidget(btn_delete)
    btn_layout.addWidget(btn_cancel)
    layout.addRow(btn_layout)

    dialog.setLayout(layout)

    CONFIG_PATH = CONFIG_DIR / "databases.json"

    def on_delete():
        # db_name = name.text()

        db_cfg = {
            "server": server.text(),
            "port": port.text(),
            "database": database.text(),
            "user": user.text(),
            "password": password.text()
        }
        try:
            delete_database(db_cfg)
        except Exception as e:
            QMessageBox.critical(dialog, localizer.t("form.config.title"), f"Помилка видалення бази: {e}")
            return
      # Зчитуємо існуючі бази
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                databases = json.load(f)
        else:
            databases = {}

        # Видаляємо запис, якщо він існує
        if db_name in databases:
            del databases[db_name]

            # Записуємо у файл
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(databases, f, ensure_ascii=False, indent=2)

        dialog.accept()

    def on_cancel():
        dialog.reject()    

    btn_delete.clicked.connect(on_delete)
    btn_cancel.clicked.connect(on_cancel)

    if db_name and CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            databases = json.load(f)
        if db_name in databases:
            db = databases[db_name]
            name.setText(db_name)
            server.setText(db.get("server", ""))
            port.setText(db.get("port", ""))
            database.setText(db.get("database", ""))

    if dialog.exec():
        return {
            "name": name.text(),
            "server": server.text(),
            "port": port.text(),
            "database": database.text()
        }
    return None        