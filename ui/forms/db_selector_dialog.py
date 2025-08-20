import json
from pathlib import Path
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QPushButton
from PyQt6.QtCore import Qt
from core.i18n.localizer import Localizer

CONFIG_PATH = Path("config/databases.json")

class DatabaseSelectorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        localizer = Localizer()

        self.setWindowTitle(localizer.t("form.database.title")) 
        self.setModal(True)
        self.selected_config = None

        layout = QVBoxLayout(self)

        self.databases = self.load_databases()
        self.list_widget = QListWidget()
        self.list_widget.addItems(self.databases.keys())
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        layout.addWidget(self.list_widget)

        confirm_btn = QPushButton(localizer.t("button.select"))
        confirm_btn.clicked.connect(self.confirm_selection)
        layout.addWidget(confirm_btn)

        self.resize(400, 300)

    def load_databases(self) -> dict[str, dict]:
        try:
            with CONFIG_PATH.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Помилка завантаження баз: {e}")
            return {}

    def confirm_selection(self):
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            db_name = selected_items[0].text()
            self.selected_config = self.databases.get(db_name)
        self.accept()

def select_database(parent=None) -> dict | None:
    dialog = DatabaseSelectorDialog(parent)
    result = dialog.exec()
    return dialog.selected_config if result == QDialog.DialogCode.Accepted else None