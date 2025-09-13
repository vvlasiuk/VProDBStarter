from PyQt6.QtWidgets import QLabel

def customize_database_selector_dialog(dialog):
    target_label = dialog.findChild(QLabel, "select_label")
    if target_label:
        target_label.setStyleSheet("color: #1976d2; font-weight: bold; font-size: 16px;")
