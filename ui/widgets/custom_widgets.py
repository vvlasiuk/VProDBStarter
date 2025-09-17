from PyQt6.QtWidgets import QLabel, QPushButton, QComboBox, QHBoxLayout

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