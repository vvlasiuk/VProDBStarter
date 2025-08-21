import os
import json
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QWidget, QMessageBox, QLabel
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from core.i18n.localizer import Localizer

# Визначаємо шлях до "Мої документи"\Vlas Pro Enterprise\config\databases.json
DOCUMENTS = Path(os.environ.get("USERPROFILE", r"C:\Users\Default"))
CONFIG_PATH = DOCUMENTS / "Vlas Pro Enterprise" / "config" / "databases.json"

class DatabaseSelectorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        localizer = Localizer()

        self.setWindowTitle(localizer.t("form.database.title")) 
        self.setWindowIcon(QIcon("assets/app_icon.ico"))
        self.setModal(True)
        self.selected_config = None

        # Основний горизонтальний layout
        main_layout = QHBoxLayout(self)

        # Ліва частина: вертикальний layout для напису, списку та підпису знизу
        left_layout = QVBoxLayout()
        label = QLabel(localizer.t("form.database.select_label"))
        left_layout.addWidget(label)

        self.databases = self.load_databases()
        self.list_widget = QListWidget()
        self.list_widget.addItems(self.databases.keys())
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        left_layout.addWidget(self.list_widget)

        # Додаємо підпис для відображення server#database
        self.info_label = QLabel("")
        left_layout.addWidget(self.info_label)

        # Оновлюємо info_label при зміні вибору
        self.list_widget.currentItemChanged.connect(self.update_info_label)
        self.update_info_label()

        main_layout.addLayout(left_layout)

        # Права частина: кнопки одна під одною
        button_layout = QVBoxLayout()
        
#        label = QLabel(localizer.t("form.database.select_label"))
#        button_layout.addWidget(label)

        self.confirm_btn = QPushButton(localizer.t("button.select"))
        self.add_btn = QPushButton(localizer.t("button.add"))
        self.delete_btn = QPushButton(localizer.t("button.delete"))

        self.confirm_btn.clicked.connect(self.confirm_selection)
        self.add_btn.clicked.connect(self.add_database)
        self.delete_btn.clicked.connect(self.delete_database)

        button_layout.addWidget(self.confirm_btn)
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()

        button_widget = QWidget()
        button_widget.setLayout(button_layout)
        main_layout.addWidget(button_widget)

        self.setLayout(main_layout)
        self.resize(400, 300)

    def load_databases(self) -> dict[str, dict]:
        # Перевіряємо існування каталогу
        if not CONFIG_PATH.parent.exists():
            CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        # Перевіряємо існування файлу, якщо нема — створюємо порожній файл
        if not CONFIG_PATH.exists():
            with CONFIG_PATH.open("w", encoding="utf-8") as f:
                f.write("{}")
            return {}
        try:
            with CONFIG_PATH.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Помилка завантаження баз: {e}")
            return {}

    def save_databases(self):
        try:
            CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            with CONFIG_PATH.open("w", encoding="utf-8") as f:
                json.dump(self.databases, f, ensure_ascii=False, indent=2)
        except Exception as e:
            QMessageBox.warning(self, "Помилка", f"Не вдалося зберегти бази: {e}")

    def confirm_selection(self):
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            db_name = selected_items[0].text()
            self.selected_config = self.databases.get(db_name)
        self.accept()

    def add_database(self):
        QMessageBox.information(self, self.windowTitle(), Localizer().t("msg.add_not_implemented"))

    def delete_database(self):
        localizer = Localizer()
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, self.windowTitle(), localizer.t("msg.select_for_delete"))
            return
        db_name = selected_items[0].text()
        reply = QMessageBox.question(
            self, self.windowTitle(),
            localizer.t("msg.confirm_delete").replace("{db}", db_name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.databases.pop(db_name, None)
            self.save_databases()
            self.list_widget.clear()
            self.list_widget.addItems(self.databases.keys())
            self.update_info_label()

    def update_info_label(self):
        current_item = self.list_widget.currentItem()
        if current_item:
            db_name = current_item.text()
            db = self.databases.get(db_name)
            if db:
                self.info_label.setText(f"{db['server']}#{db['database']}")
                return
        self.info_label.setText("")

def select_database(parent=None) -> dict | None:
    dialog = DatabaseSelectorDialog(parent)
    result = dialog.exec()
    return dialog.selected_config if result == QDialog.DialogCode.Accepted else None