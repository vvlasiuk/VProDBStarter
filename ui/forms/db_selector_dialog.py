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
from core.config_paths import CONFIG_DIR
from core.secure_config import load_password_for_db
from PyQt6.QtWidgets import QMenu, QInputDialog
from collections import OrderedDict
from ui.forms.context_menu_utils import build_context_menu
from ui.widgets.custom_widgets import CustomLabel

# Визначаємо шлях до "Мої документи"\Vlas Pro Enterprise\config\databases.json
# CONFIG_PATH = CONFIG_DIR / "databases.json"
# LAST_SELECTED_PATH = CONFIG_DIR / "last_selected_db.json"

class DatabaseListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.setObjectName("database_list_widget")
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.databases = self.load_databases()

    def load_databases(self) -> dict:
        config_path = Path(self.config.config_path)
        if not config_path.parent.exists():
            config_path.parent.mkdir(parents=True, exist_ok=True)
        if not config_path.exists():
            with config_path.open("w", encoding="utf-8") as f:
                f.write("{}")
            return {}
        try:
            with config_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Помилка завантаження баз: {e}")
            return {}

    def refresh(self, selected_db_name: str = None):
         # Якщо ім'я бази не передано — отримати поточний вибір
        if selected_db_name is None and self.currentItem():
            selected_db_name = self.currentItem().text()
 
        self.databases = self.load_databases()
        self.clear()
        self.addItems(self.databases.keys())
       
        # Спозиціонуватися на доданій базі
        if selected_db_name:
            items = self.database_list_widget.findItems(selected_db_name, Qt.MatchFlag.MatchExactly)
            if items:
                self.database_list_widget.setCurrentItem(items[0])

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

        CustomLabel(
            localizer.t("form.database.select_label"),
            object_name="select_label",
            layout=main_layout
        )

        # self.databases = self.load_databases()

        self.database_list_widget = DatabaseListWidget()

        # self.list_widget = QListWidget()
        self.database_list_widget.addItems(self.databases.keys())
        left_layout.addWidget(self.database_list_widget)

        self.database_list_widget.customContextMenuRequested.connect(self.show_list_context_menu)

        # Оновлюємо info_label при зміні вибору
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

        # Встановлюємо останній вибраний елемент, якщо він є
        last_selected = self.load_last_selected_db(config)
        if last_selected and last_selected in self.databases:
            items = self.list_widget.findItems(last_selected, Qt.MatchFlag.MatchExactly)
            if items:
                self.list_widget.setCurrentItem(items[0])
        elif self.list_widget.count() > 0:
            # Якщо не збережено або не знайдено — вибрати перший рядок
            self.list_widget.setCurrentRow(0)
            self.update_fields_on_selection()

        self.setLayout(main_layout)
        self.resize(500, 400)

        # --- HOOK для плагінів ---
        if config.extensions:
            for ext in config.extensions:
                if hasattr(ext, "customize_database_selector_dialog"):
                    ext.customize_database_selector_dialog(self)

    # def load_databases(self) -> dict[str, dict]:
    #     # Перевіряємо існування каталогу
    #     config_path = Path(self.config.config_path)
    #     if not config_path.parent.exists():
    #         config_path.parent.mkdir(parents=True, exist_ok=True)
    #     if not config_path.exists():
    #         with config_path.open("w", encoding="utf-8") as f:
    #             f.write("{}")
    #         return {}
    #     try:
    #         with config_path.open("r", encoding="utf-8") as f:
    #             return json.load(f)
    #     except Exception as e:
            print(f"Помилка завантаження баз: {e}")
            return {}

    def save_databases(self, config):
        config_path = Path(config.config_path)
        try:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with config_path.open("w", encoding="utf-8") as f:
                json.dump(self.databases, f, ensure_ascii=False, indent=2)
        except Exception as e:
            QMessageBox.warning(self, "Помилка", f"Не вдалося зберегти бази: {e}")

    def login_database(self):
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            db_name = selected_items[0].text()
            self.selected_config = self.databases.get(db_name)
            self.save_last_selected_db(db_name)
        self.accept()

    def load_last_selected_db(self, config) -> str | None:
        last_selected_path = Path(config.last_selected_path)
        try:
            if last_selected_path.exists():
                with last_selected_path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("last_selected")
        except Exception as e:
            print(f"Помилка завантаження last_selected_db: {e}")
        return None

    def save_last_selected_db(self, db_name: str):
        last_selected_path = Path(self.config.last_selected_path)
        try:
            last_selected_path.parent.mkdir(parents=True, exist_ok=True)
            with last_selected_path.open("w", encoding="utf-8") as f:
                json.dump({"last_selected": db_name}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Помилка збереження last_selected_db: {e}")

    def update_fields_on_selection(self):

        self.user_combo.clear()
        self.info_label.clear()

        current_item = self.database_list_widget.currentItem()
        if not current_item:
            return

        db_name = current_item.text()
        with Path(self.config.config_path).open("r", encoding="utf-8") as f:
            all_databases = json.load(f)
        db_info = all_databases.get(db_name, {})

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

    def show_list_context_menu(self, pos):
        item = self.database_list_widget.itemAt(pos)

        # Створюємо меню через build_context_menu (уніфікований стиль)
        menu, rename_action, delete_action, edit_conn_action, add_action, create_db_action, delete_db_action = build_context_menu(self)

        action = menu.exec(self.database_list_widget.mapToGlobal(pos))
        if item:
            db_name = item.text()
        else: 
            db_name = ""

        if action == rename_action:
            new_name, ok = QInputDialog.getText(self, "Змінити назву", "Нова назва:", text=db_name)
            if ok and new_name and new_name != db_name:
                # Зберігаємо позицію старого ключа
                keys = list(self.databases.keys())
                idx = keys.index(db_name)
                value = self.databases.pop(db_name)
                # Створюємо OrderedDict з новим ключем на тій же позиції
                items = list(self.databases.items())
                items.insert(idx, (new_name, value))
                self.databases = OrderedDict(items)
                self.save_databases()
                self.list_widget.clear()
                self.list_widget.addItems(self.databases.keys())
                # Вибрати перейменований елемент
                items = self.database_list_widget.findItems(new_name, Qt.MatchFlag.MatchExactly)
                if items:
                    self.list_widget.setCurrentItem(items[0])
        elif action == delete_action:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Підтвердження вилучення")
            msg_box.setText("Робочий простір буде вилучений зі списку. Ви впевнені?")
            yes_button = msg_box.addButton("ТАК", QMessageBox.ButtonRole.YesRole)
            no_button = msg_box.addButton("НІ", QMessageBox.ButtonRole.NoRole)
            msg_box.setDefaultButton(yes_button)
            msg_box.exec()

            if msg_box.clickedButton() == yes_button:
                self.databases.pop(db_name, None)
                self.save_databases()
                self.database_list_widget.clear()
                self.database_list_widget.addItems(self.databases.keys())
                self.update_fields_on_selection()
        elif action == edit_conn_action:
            result = show_edit_config_dialog(self, db_name)
            if result:
                # Спозиціонуватися на доданій базі
                db_name = result.get("name")
                self.update_fields_on_selection()
        elif action == add_action:
            result = show_add_config_dialog(self)
            if result:
                with CONFIG_PATH.open("r", encoding="utf-8") as f:
                    self.databases = json.load(f)
                self.list_widget.clear()
                self.list_widget.addItems(self.databases.keys())
                items = self.list_widget.findItems(result.get("name"), Qt.MatchFlag.MatchExactly)
                if items:
                    self.database_list_widget.setCurrentItem(items[0])
                    self.update_fields_on_selection()
        elif action == create_db_action:
            result = show_create_db_dialog(self)
            if result:
                # Оновити список баз
                # self.databases = self.load_databases()
                # self.database_list_widget.clear()
                # self.database_list_widget.addItems(self.databases.keys())
                self.database_list_widget.refresh(result.get("name"))

                # # Спозиціонуватися на доданій базі
                # db_name = result.get("name")
                # if db_name:
                #     items = self.database_list_widget.findItems(db_name, Qt.MatchFlag.MatchExactly)
                #     if items:
                #         self.database_list_widget.setCurrentItem(items[0])
        elif action == delete_db_action:
            result = show_delete_db_dialog(self, db_name)

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



