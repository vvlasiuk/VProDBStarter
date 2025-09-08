def on_app_start(app, window):
    # Додаємо напис "Плагін" у верхню частину форми
    from PyQt6.QtWidgets import QLabel
    # plugin_label = QLabel("Плагін")
    # plugin_label.setStyleSheet("color: #1976d2; font-weight: bold; font-size: 16px;")
    # # Додаємо напис у головний layout (першим елементом)
    # if hasattr(window, 'layout'):
    #     layout = window.layout()
    #     if layout:
    #         layout.insertWidget(0, plugin_label)
    # elif hasattr(window, 'main_layout'):
    #     layout = window.main_layout
    #     if layout:
    #         layout.insertWidget(0, plugin_label)

    target_label = window.findChild(QLabel, "select_db_label")
    if target_label:
        target_label.setStyleSheet("color: #1976d2; font-weight: bold; font-size: 16px;")
    # Змінюємо колір кнопки "login_btn"
    # if hasattr(window, "login_btn"):
    #     window.login_btn.setStyleSheet("background-color: #1976d2; color: white; font-weight: bold;")