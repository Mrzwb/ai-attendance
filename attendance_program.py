from PySide6.QtCore import Slot, QSize
from PySide6.QtWidgets import QMainWindow, QFileDialog

from widgets import UITools
from widgets import AttendanceHome


class MainWindow(QMainWindow):
    __title = "智能考勤"
    __menus = {"file": "&文件", "tools": "&工具"}

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.__title)

        # Widget
        self._attendance_home = AttendanceHome()
        self.setCentralWidget(self._attendance_home)

        # Menu
        self.create_menus()

        # Window dimensions
        geometry = self.screen().availableGeometry()
        self.setMinimumWidth(int(geometry.width() * 0.8))
        self.setMinimumHeight(int(geometry.height() * 0.8))

    def create_menus(self):
        file_menu = self.menuBar().addMenu(self.__menus['file'])
        tool_menu = self.menuBar().addMenu(self.__menus['tools'])

        # Populate the File menu
        _open_action = UITools.create_action(self, "&打开...", file_menu, self.open_file)
        _save_action = UITools.create_action(self, "&保存为...", file_menu, self.save_file)
        _save_action.setEnabled(False)
        file_menu.addSeparator()
        exit_action = UITools.create_action(self, "&退出", file_menu, self.close)

        # Populate the Tools menu
        _model_action = UITools.create_action(self, "&模型(VIP)", tool_menu, self.open_file)
        _supervise_action = UITools.create_action(self, "&督办...", tool_menu, self.open_file)
        _export_action = UITools.create_action(self, "&导出...", tool_menu, self.open_file)
        tool_menu.addSeparator()
        _appeal_action = UITools.create_action(self, "&AI助理(VIP)", tool_menu, self.open_file)
        _model_action.setEnabled(False)
        _export_action.setEnabled(False)
        _appeal_action.setEnabled(False)
        _supervise_action.setEnabled(False)

    # Quick  gotcha:
    #
    # QFiledialog.getOpenFilename and QFileDialog.get.SaveFileName don't
    # behave in PySide6 as they do in Qt, where they return a QString
    # containing the filename.
    #
    # In PySide6, these functions return a tuple: (filename, filter)
    @Slot()
    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self)
        if filename:
            self._attendance_home.read_from_file(filename)

    @Slot()
    def save_file(self):
        filename, _ = QFileDialog.getSaveFileName(self)
        if filename:
            self._attendance_home.write_to_file(filename)
