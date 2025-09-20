import os
import json
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QMessageBox, QComboBox, QLineEdit
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon
from core.db.db_utils import check_sql_database_exists, fetch_users_list
from ui.forms.db_config_dialog import show_edit_config_dialog, show_add_config_dialog, show_create_db_dialog, show_delete_db_dialog
# from core.config_paths import CONFIG_DIR
from core.secure_config import load_password_for_db
from PyQt6.QtWidgets import QMenu, QInputDialog
from collections import OrderedDict
from ui.forms.context_menu_utils import build_context_menu
from ui.widgets.custom_widgets import ConfirmDialog, CustomLabel
from core.files_storage.DatabaseListStorage import DatabaseListStorage, LastSelectedDbStorage

class DatabaseListWidget(QListWidget):
    def __init__(self, parent=None, config=None, db_selector_dialog=None):
        super().__init__(parent)
        self.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.setObjectName("database_list_widget")
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        self.config                   = config
        self.db_selector_dialog       = db_selector_dialog
        self.db_list_storage          = DatabaseListStorage(config.databases_list_path)
        self.last_selected_db_storage = LastSelectedDbStorage(config.last_selected_db_path)

        self.customContextMenuRequested.connect(self.show_context_menu)

    def load_databases(self) -> dict:
        return self.db_list_storage.load()

    def get_current_db_name(self) -> str | None:
        current_item = self.currentItem()
        if current_item:
            return current_item.text()
        return None
    
    def get_db_info(self, db_name: str) -> dict:
        return self.db_list_storage.get_db_info(db_name)

    def get_db_info_by_id(self, db_id: str) -> dict | None:
        if db_id is None:
            return None
        
        all_databases = self.load_databases()
        for db_name, db_info in all_databases.items():
            if db_info.get("id") == db_id:
                db_info_with_name = db_info.copy()
                db_info_with_name["name"] = db_name
                return db_info_with_name
        return None    
    
    def load_last_selected_db(self) -> str | None:
        return self.last_selected_db_storage.load()

    def save_last_selected_db(self, db_id: str, db_user: str) -> None:
        return self.last_selected_db_storage.save(db_id=db_id, db_user=db_user)

    def show_context_menu(self, pos):
        
        localizer=self.config.localizer

        item = self.itemAt(pos)
        if item:
            db_name = item.text()
        else: 
            db_name = ""

        menu, rename_action, delete_action, edit_conn_action, add_action, create_db_action, delete_db_action = build_context_menu(self)

        if not db_name:
            rename_action.setEnabled(False)
            delete_action.setEnabled(False)
            edit_conn_action.setEnabled(False)
            delete_db_action.setEnabled(False)

        action = menu.exec(self.mapToGlobal(pos))

        if action == rename_action:
            new_name, ok = QInputDialog.getText(self, localizer.t("dialog.rename.title"), localizer.t("dialog.rename.label"), text=db_name)            
            if ok and new_name and new_name != db_name:
                self.db_list_storage.rename(db_name, new_name)
                self.refresh(selected_db_name=new_name)

        elif action == delete_action:
            confirm = ConfirmDialog(self, title=localizer.t("dialog.confirm.delete_title"),
                                    text=localizer.t("dialog.confirm.delete_workspace_text").format(name=db_name))            
            if confirm.exec_and_confirm():
                self.db_list_storage.delete(db_name)
                self.refresh()

        elif action == edit_conn_action:
            result = show_edit_config_dialog(self, db_name)
            if result:
                self.db_selector_dialog.update_fields_on_selection()
        
        elif action == add_action:
            result = show_add_config_dialog(self)
            if result:
                self.refresh(result.get("name"))
                self.db_selector_dialog.update_fields_on_selection()
   
        elif action == create_db_action:
            result = show_create_db_dialog(self)
            if result:
                self.refresh(result.get("name"))
        
        elif action == delete_db_action:
            result = show_delete_db_dialog(self, db_name)
            if result:
                self.refresh()

    def refresh(self, selected_db_name: str = None):

        if selected_db_name is None: 
            if self.currentItem():
                 # Якщо ім'я бази не передано — отримати поточний вибір
                selected_db_name = self.currentItem().text()
            else:
                # Останя база в котру виконано вхід
                last_selected_db = self.load_last_selected_db()
                if last_selected_db:
                    db_id = last_selected_db.get("db_id", None)
                    db_info = self.get_db_info_by_id(db_id)
                    if db_info:
                        selected_db_name = db_info.get("name", None)
                    
                    self.db_selector_dialog.last_selected_user = last_selected_db.get("user", None)
                    # if last_user:
                    #     self.db_selector_dialog.user_combo.setCurrentText(last_user)

        self.clear()
        self.databases = self.load_databases()
        self.addItems(self.databases.keys())
       
        # Спозиціонуватися на базі
        if selected_db_name:
            items = self.findItems(selected_db_name, Qt.MatchFlag.MatchExactly)
            if items:
                self.setCurrentItem(items[0])

        # Викликаємо оновлення полів у діалозі
        if self.db_selector_dialog:
            self.db_selector_dialog.update_fields_on_selection()

class DatabaseSelectorDialog(QDialog):
    def __init__(self, parent=None, config=None):
        super().__init__(parent)

        localizer = config.localizer

        self.config = config

        self.setWindowTitle(localizer.t("form.database.title")) 
        self.setWindowIcon(QIcon("assets/app_icon.ico"))
        self.setModal(True)
        self.selected_config = None

        
        main_layout = QVBoxLayout(self) # Основний горизонтальний layout

        left_layout = QVBoxLayout()   # Ліва частина: вертикальний layout
        right_layout = QVBoxLayout()  # Права частина: вертикальний layout

        # Показали верхній підпис
        CustomLabel(
            localizer.t("form.database.select_label"),
            object_name="select_label",
            layout=main_layout
        )

        # Показали список баз
        self.database_list_widget = DatabaseListWidget(config=self.config, db_selector_dialog=self)
        left_layout.addWidget(self.database_list_widget)
        self.database_list_widget.currentItemChanged.connect(self.update_fields_on_selection)

        user_row      = QHBoxLayout()  # Група "Користувач"
        password_row  = QHBoxLayout()  # Група "Пароль"

        right_layout.addLayout(user_row)
        right_layout.addLayout(password_row)

        user_label = CustomLabel(
            localizer.t("form.database.user_label"),
            object_name="user_label",
            layout=user_row
        )

        self.user_combo = QComboBox()
        self.user_combo.setEditable(True)
        user_row.addWidget(self.user_combo)

        password_label = CustomLabel(
            localizer.t("form.database.password_label"),
            object_name="password_label",
            layout=password_row
        )

        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        password_row.addWidget(self.password_edit)

        # --- Встановлюємо однакову ширину для user_label та password_label ---
        label_width = max(user_label.sizeHint().width(), password_label.sizeHint().width())
        user_label.setFixedWidth(label_width)
        password_label.setFixedWidth(label_width)

        # Далі кнопки
        self.login_btn = QPushButton(localizer.t("button.login"))

        # Встановлюємо ширину login_btn як у user_combo
        self.login_btn.setFixedWidth(self.user_combo.sizeHint().width())

        # Додаємо login_btn у горизонтальний layout для вирівнювання вправо
        login_row = QHBoxLayout()
        login_row.addStretch()
        login_row.addWidget(self.login_btn)
        right_layout.addLayout(login_row)

        self.login_btn.clicked.connect(self.login_database)

        right_layout.addStretch()

        # Новий горизонтальний layout для лівої і правої частини
        content_layout = QHBoxLayout()
        content_layout.addLayout(left_layout)
        content_layout.addLayout(right_layout)

        main_layout.addLayout(content_layout)

        # Додаємо підпис для відображення server#database
        self.info_label = CustomLabel(
                "",
                object_name="info_label",
                layout=main_layout
            )

        self.setLayout(main_layout)
        self.resize(500, 400)

        self.database_list_widget.refresh()

       # --- HOOK для плагінів ---
        if config.extensions:
            for ext in config.extensions:
                if hasattr(ext, "customize_database_selector_dialog"):
                    ext.customize_database_selector_dialog(self)

    def save_databases(self, config):
        config_path = Path(config.config_path)
        try:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with config_path.open("w", encoding="utf-8") as f:
                json.dump(self.databases, f, ensure_ascii=False, indent=2)
        except Exception as e:
            QMessageBox.warning(self, "Помилка", f"Не вдалося зберегти бази: {e}")

    def login_database(self):
        db_name = self.database_list_widget.get_current_db_name()
        db_id   = self.database_list_widget.get_db_info(db_name=db_name).get("id", "")
        db_user = self.user_combo.currentText()
        if db_id and db_user:
            self.selected_config = db_name
            self.database_list_widget.save_last_selected_db(db_id, db_user)
        self.accept()

    def update_fields_on_selection(self):

        self.user_combo.clear()
        self.info_label.clear()

        current_item = self.database_list_widget.currentItem()
        if not current_item:
            return

        db_name = current_item.text()
        db_info = self.database_list_widget.get_db_info(db_name)

        # Встановлюємо користувача з поля "user" у файлі
        server   = db_info.get("server", "")
        database = db_info.get("database", "")
        user     = db_info.get("user", "")
        port     = db_info.get("port", "")
        sa_password = ""
        sa_user     = ""

        if server and database:
            self.info_label.setText(f"{server}#{port}#{database}")
        else:
            self.info_label.clear()

        if database:
            creds = load_password_for_db(database)
            sa_password = creds.get('pass', '')
            sa_user     = creds.get('user', '')

        def check_db():
            # ДОДАЙТЕ ЦЕЙ БЛОК ПЕРЕД СТВОРЕННЯМ НОВОГО ПОТОКУ
            if hasattr(self, "db_thread") and self.db_thread.isRunning():
                self.db_thread.quit()
                self.db_thread.wait()

            def on_finished(db_exists):
                self.user_combo.setEnabled(db_exists)
                self.password_edit.setEnabled(db_exists)
                self.login_btn.setEnabled(db_exists)
                if db_exists:
                    self.info_label.setStyleSheet("color: green;")
                else:
                    self.info_label.setStyleSheet("color: red;")

            def on_users_ready(users):
                self.user_combo.clear()
                if users:
                    self.user_combo.addItems(users)
                    if self.last_selected_user and self.last_selected_user in users:
                        self.user_combo.setCurrentText(self.last_selected_user)
                    else:
                        self.user_combo.setCurrentText(users[0])
                else:
                    self.user_combo.setCurrentText("")

            if server and database and port and sa_password and sa_user:
                cfg = {
                    "server": server,
                    "database": database,
                    "port": port,
                    "user": sa_user,
                    "password": sa_password
                }
                self.db_thread = DBCheckThread(cfg, self)
                self.db_thread.finished.connect(on_finished)
                self.db_thread.users_ready.connect(on_users_ready)
                self.db_thread.start()
            else:
                on_finished(False)

        check_db()  # ← ДОДАЙТЕ ЦЕЙ ВИКЛИК

    def closeEvent(self, event):
        # Якщо потік існує і ще працює — дочекатися завершення
        if hasattr(self, "db_thread") and self.db_thread.isRunning():
            self.db_thread.quit()
            self.db_thread.wait()
        super().closeEvent(event)

class DBCheckThread(QThread):
    finished = pyqtSignal(bool)
    users_ready = pyqtSignal(list)  # Додаємо новий сигнал

    def __init__(self, cfg, dialog):
        super().__init__()
        self.cfg = cfg
        self.dialog = dialog

    def run(self):
        result = check_sql_database_exists(self.cfg)
        self.finished.emit(result)
        if result:
            users = fetch_users_list(self.cfg)
            self.users_ready.emit(users)  # Передаємо список користувачів

def select_database(parent=None, config=None) -> dict | None:

    dialog = DatabaseSelectorDialog(parent, config)
    result = dialog.exec()

    return dialog.selected_config if result == QDialog.DialogCode.Accepted else None



