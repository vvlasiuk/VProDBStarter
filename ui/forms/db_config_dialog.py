from PyQt6.QtWidgets import QDialog, QLineEdit, QFormLayout, QPushButton, QApplication
import sys
from core.i18n.localizer import Localizer

def show_config_dialog(lang="uk"):
    localizer = Localizer()
    #app = QApplication(sys.argv)
    dialog = QDialog()
    dialog.setWindowTitle(localizer.t("dialog.config.title"))

    layout = QFormLayout()

    server = QLineEdit()
    database = QLineEdit()
    user = QLineEdit()
    password = QLineEdit()
    password.setEchoMode(QLineEdit.EchoMode.Password)

    layout.addRow(localizer.t("label.server"), server)
    layout.addRow(localizer.t("label.database"), database)
    layout.addRow(localizer.t("label.user"), user)
    layout.addRow(localizer.t("label.password"), password)

    btn = QPushButton(localizer.t("button.save"))
    layout.addWidget(btn)

    dialog.setLayout(layout)

    def on_save():
        dialog.accept()

    btn.clicked.connect(on_save)
    if dialog.exec():
        return {
            "server": server.text(),
            "database": database.text(),
            "user": user.text(),
            "password": password.text()
        }
    return None