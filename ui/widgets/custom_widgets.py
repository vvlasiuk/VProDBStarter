from PyQt6.QtWidgets import QLabel, QPushButton, QComboBox, QHBoxLayout, QMessageBox

class CustomLabel(QLabel):
    def __init__(self, text="", object_name=None, style=None, parent=None, layout=None):
        super().__init__(text, parent)
        
        if object_name:
            self.setObjectName(object_name)
        
        if style:
            self.setStyleSheet(style)

        if layout is not None:
            layout.addWidget(self)

class CustomButton(QPushButton):
    def __init__(self, text="", object_name=None, style=None, parent=None, layout=None):
        super().__init__(text, parent)
        # self.setText(text)
        # if object_name:
        #     self.setObjectName(object_name)
        # if style:
        #     self.setStyleSheet(style)
        # if layout is not None:
        #     layout.addWidget(self)

class CustomComboBox(QComboBox):
    def __init__(self, object_name=None, style=None, parent=None, layout=None):
        super().__init__(parent)
        # if object_name:
        #     self.setObjectName(object_name)
        # if style:
        #     self.setStyleSheet(style)
        # if layout is not None:
        #     layout.addWidget(self)

class ConfirmDialog(QMessageBox):
    def __init__(
        self,
        parent=None,
        localizer=None,
        title=None,
        text=None,
        yes_text=None,
        no_text=None
    ):
        super().__init__(parent)

        if localizer:
            self.localizer = localizer
        else: 
            if parent and parent.config:
                self.localizer = parent.config.localizer

        self.setWindowTitle(title or self.localizer.t("dialog.confirm.default_title"))
        self.setText(text or self.localizer.t("dialog.confirm.default_text"))

        self.yes_button = self.addButton(yes_text or self.localizer.t("dialog.confirm.default_yes"), QMessageBox.ButtonRole.YesRole)
        self.no_button  = self.addButton(no_text or self.localizer.t("dialog.confirm.default_no"), QMessageBox.ButtonRole.NoRole)

        self.setDefaultButton(self.no_button)

    def exec_and_confirm(self):
        self.exec()
        return self.clickedButton() == self.yes_button