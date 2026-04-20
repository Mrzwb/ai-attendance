from PySide6.QtGui import QAction
from PySide6.QtWidgets import QListWidget, QPushButton


class UITools:

    @staticmethod
    def create_action(parent, text, widget, slot):
        """ Helper function to save typing when populating menus
            with action.
        """
        action = QAction(text, parent)
        widget.addAction(action)
        action.triggered.connect(slot)
        return action

    @staticmethod
    def attach_list_click(parent: QListWidget, slot):
        parent.itemClicked.connect(slot)

    @staticmethod
    def attach_button_click(parent: QPushButton, slot):
        parent.clicked.connect(slot)

    @staticmethod
    def clear_ui_checkbox(files: list[dict]):
        """
        删除表头控件，避免内存泄露
        :return:
        """
        for file in files:
            for column_ui in file["columns"]:
                del column_ui
