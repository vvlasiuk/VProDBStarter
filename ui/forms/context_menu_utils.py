from PyQt6.QtWidgets import QMenu, QWidgetAction, QWidget, QLabel, QHBoxLayout
from PyQt6.QtGui import QIcon, QFont, QCursor
from PyQt6.QtCore import QSize, Qt

class HoverMenuItem(QWidget):
    def __init__(self, icon_path, text, icon_size=12, parent=None):
        super().__init__(parent)
       # self.default_bg = "#fefefe"
        self.setAutoFillBackground(True)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(10)

        icon_label = QLabel()
        icon_label.setPixmap(QIcon(icon_path).pixmap(QSize(icon_size, icon_size)))
        self.text_label = QLabel(text)
        self.text_label.setFont(QFont("Segoe UI", 10))
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self.hover_bg = "#c5d8f5"
        self.default_bg = self.text_label.styleSheet()

        layout.addWidget(icon_label)
        layout.addWidget(self.text_label)
        layout.addStretch()
        self.set_text_bg(self.default_bg)

    def enterEvent(self, event):
        self.set_text_bg(self.hover_bg)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.set_text_bg(self.default_bg)
        super().leaveEvent(event)

    def set_text_bg(self, color):
        self.text_label.setStyleSheet(f"background-color: {color};")

def create_menu_item(icon_path: str, text: str, icon_size: int = 12) -> QWidget:
    widget = QWidget()
    layout = QHBoxLayout(widget)
    layout.setContentsMargins(12, 6, 12, 6)
    layout.setSpacing(10)

    icon_label = QLabel()
    icon_label.setPixmap(QIcon(icon_path).pixmap(QSize(icon_size, icon_size)))

    text_label = QLabel(text)
    text_label.setFont(QFont("Segoe UI", 10))
    text_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)  # ← Додаємо вирівнювання

    layout.addWidget(icon_label)
    layout.addWidget(text_label)
    layout.addStretch()  # ← Додаємо stretch, щоб текст не був по центру

    return widget

def build_context_menu(parent=None) -> QMenu:
    menu = QMenu(parent)
    menu.setStyleSheet("""
        QMenu {
            background-color: #fefefe;
            border: 1px solid #ccc;
        }
    """)
    # "Змінити назву"
    rename_action = QWidgetAction(menu)
    rename_action.setDefaultWidget(HoverMenuItem("assets/icons/rename.svg", "Змінити назву"))
    menu.addAction(rename_action)

    # "Змінити параметри підключення"
    edit_conn_action = QWidgetAction(menu)
    edit_conn_action.setDefaultWidget(HoverMenuItem("assets/icons/settings.svg", "Змінити параметри підключення"))
    menu.addAction(edit_conn_action)

    # "Видалити зі списку"
    delete_action = QWidgetAction(menu)
    delete_action.setDefaultWidget(HoverMenuItem("assets/icons/delete.svg", "Видалити зі списку"))
    menu.addAction(delete_action)

    return menu, rename_action, delete_action, edit_conn_action