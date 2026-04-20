import asyncio
import gc
import io
import threading
from typing import Union, override

from PySide6 import QtCore
from PySide6.QtGui import QPalette, QFont, QColor, QTextCursor
from pandas import DataFrame
from typing_extensions import final

from data import read_excel, is_excel, concat_excel, AttendanceHelper, RangeObject
from model.templates import REPORT_HEADER_FIA
from .attendance_chart import AttendanceChart
from .attendance_report import AttendanceReport
from .customization import FlowLayout
from .dialog import AnalysisDialog
from .finance_report import FinanceReport
from .utils import UITools
from llms.chat_client import FreeClient
from llms.chat_async_client import strat_chat_thread

from PySide6.QtCore import Qt, QFileInfo, QMargins, Slot
from PySide6.QtWidgets import QWidget, QHBoxLayout, QListWidget, QListWidgetItem, QLabel, QPushButton, QVBoxLayout, \
    QTabWidget, QMessageBox, QGridLayout, QFormLayout, QTextBrowser, QGroupBox, \
    QScrollArea, QCheckBox, QApplication


class AttendanceHome(QWidget):
    # 合并数据
    _merger_data: DataFrame

    # 大模型
    _chat_client = FreeClient()

    # 问数线程池
    _threads: list[threading.Thread] = []

    def __init__(self):
        super().__init__()
        self._tab_widget = QTabWidget()
        self._tab_home = HomeTab(self)
        self._tab_widget.addTab(self._tab_home, "首页")
        self._button_reset = QPushButton("重置")
        self._button_reset.setObjectName("button_reset")
        self._button_analysis = QPushButton("智能分析")
        self._button_analysis.setObjectName("button_analyse")
        self._dialog = AnalysisDialog(self._tab_home)
        self._dialog.confirm_clicked.connect(self._show_tabs)
        UITools.attach_button_click(self._button_reset, self.reset)
        UITools.attach_button_click(self._button_analysis, self.analyse)

        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        button_layout.addWidget(self._button_reset)
        button_layout.addWidget(self._button_analysis)
        main_layout = QVBoxLayout()
        main_layout.addWidget(self._tab_widget, 4)
        main_layout.addLayout(button_layout, 1)
        self.setLayout(main_layout)

    def read_from_file(self, filename):
        """ Read data in from a file. """
        if is_excel(filename):
            try:
                file = QFileInfo(filename)
                data = read_excel(filename)
                self._tab_home.load_file(file, data)
            except (IOError, ValueError, ImportError):
                QMessageBox.information(self, "警告", f"不能打开文件: {filename}")
        else:
            QMessageBox.critical(self, "警告", "仅支持Excel文件 (xls,xlsx)")

    def write_to_file(self, filename):
        pass

    def reset(self):
        self._tab_home.reset_and_clean_memory()
        self._clean_tabs()
        self._dialog.reset()
        self._chat_client.close()

    def analyse(self):
        self._dialog.show()

    def _clean_tabs(self) -> None:
        """
            保留第一个tab页
        :return:
        """
        count = self._tab_widget.count()
        while count > 1:
            self._tab_widget.removeTab(1)
            count = self._tab_widget.count()

    @Slot(int)
    def _show_tabs(self, checked_id: int):
        if checked_id == 1:
            self._merger_data = concat_excel(self._tab_home.get_data_list())

            text_browser = QTextBrowser(self)
            text_browser.setContentsMargins(QMargins(15, 25, 15, 25))
            self._tab_widget.addTab(text_browser, f"智能分析")
            if self._merger_data is not None:

                ## 同步方式
                stream = self._chat_client.response_with_stream(f"""
                请依据以下提供合并数据的前50行样本，分析下考勤报表:
                {self._merger_data.head(50)}
                """)
                for s in stream:
                    text = s.choices[0].delta.content
                    point_size = text_browser.font().pointSize()
                    if text == '<think>':
                        text = "深度思考\U0001f30d:"
                        text_browser.setTextColor(Qt.GlobalColor.darkGray)
                        text_browser.setFontPointSize(point_size - 1)
                    if text == '</think>':
                        text = ""
                        text_browser.setTextColor(Qt.GlobalColor.black)
                        text_browser.setFontPointSize(point_size)
                    text_browser.insertPlainText(text)
                    text_browser.moveCursor(QTextCursor.MoveOperation.End)
                    QApplication.processEvents(QtCore.QEventLoop.ProcessEventsFlag.AllEvents)

                # 异步方式
                # my_thread = strat_chat_thread((f"""请依据以下提供合并数据的前50行样本，分析下考勤报表:
                # {self._merger_data.head(50)}""", text_browser, self._chat_client))

            report = AttendanceReport(self._merger_data)
            self._tab_widget.addTab(report, f"考勤报表")

            result = AttendanceHelper.statistic(self._merger_data)
            if result is not None:
                count = AttendanceHelper.get_itr_count(result.index)
                left_bracket = "(" if count > 1 else ''
                right_bracket = ")" if count > 1 else ''
                for i in range(count):
                    title_seq = i + 1 if count > 1 else ''
                    charts = AttendanceChart(self._merger_data, RangeObject(8 * i, 8 * (i + 1)))
                    self._tab_widget.addTab(charts, f"考勤图表{left_bracket}{title_seq}{right_bracket}")
            else:
                charts = AttendanceChart(self._merger_data)
                self._tab_widget.addTab(charts, f"考勤图表")

        elif checked_id == 2:
            self._merger_data = concat_excel(self._tab_home.get_data_list())

            text_browser = QTextBrowser(self)
            self._tab_widget.addTab(text_browser, f"财务分析")
            if self._merger_data is not None:
                strat_chat_thread(f"""
                请依据以下提供合并数据的前50行样本，分析下财务报表:
                {self._merger_data.head(50)}
                """, text_browser, self._chat_client).start()

            report = FinanceReport(self._merger_data, REPORT_HEADER_FIA)
            self._tab_widget.addTab(report, f"财务报表")

        else:
            self._merger_data = concat_excel(self._tab_home.get_data_list())
            if self._merger_data is not None:
                report = FinanceReport(self._merger_data, tuple(self._merger_data.columns))
                self._tab_widget.addTab(report, f"合并报表")

        for t in self._threads:
            print(f"{t.name}, {t.is_alive()}")


class HomeTab(QWidget):
    _current_file: dict = {"columns": [], "data": None}

    _cache_files: dict = {}

    # 优化重复点击
    _cursor_name: str = None

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        # left ui
        self.menu_title = QLabel("<h4>我的数据</h4>")
        self.menu_title.setFixedWidth(60)
        self.menu_widget = QListWidget()
        form_layout = QFormLayout()
        form_layout.setContentsMargins(QMargins())
        form_layout.addRow(self.menu_title)
        form_layout.addRow(self.menu_widget)
        UITools.attach_list_click(self.menu_widget, self.click_list_item)

        # right ui
        self.panel_title = QLabel("<h4>文件描述</h4>")
        self.panel_title.setFixedWidth(60)
        self.panel_header = QScrollArea()
        self.panel_header.setWidgetResizable(True)
        self.panel_header.setMinimumHeight(50)
        self.panel_header.setMaximumHeight(int(self.window().height() * 0.2))
        self.panel_header.setBackgroundRole(QPalette.ColorRole.Light)
        self.panel_header_gbox = QGroupBox("表头信息")
        self.panel_header_gbox.setLayout(FlowLayout())
        self.panel_header.setWidget(self.panel_header_gbox)
        self.panel_content = QTextBrowser()
        self.panel_content.setContentsMargins(QMargins())
        self.panel_content.setStyleSheet("""
            border: 1 solid #e6e6e6
        """)

        grid_layout = QGridLayout()
        grid_layout.setContentsMargins(QMargins())
        grid_layout.addWidget(self.panel_title, 0, 0)
        grid_layout.addWidget(self.panel_header, 1, 0)
        grid_layout.addWidget(self.panel_content, 2, 0)
        layout = QHBoxLayout()
        layout.addLayout(form_layout, 1)
        layout.addLayout(grid_layout, 4)
        self.setLayout(layout)

    def add_list_item(self, file_info: QFileInfo):
        item = QListWidgetItem(f"{file_info.fileName()}")
        item.setToolTip(file_info.path())
        self.menu_widget.addItem(item)

    def show_header(self, file_name: str, data: DataFrame):
        if self._cursor_name != file_name:
            columns = self._current_file["columns"]
            newColumns = []

            for c in columns:
                c.setParent(None)
                self.panel_header_gbox.layout().removeWidget(c)

            if file_name in self._cache_files:
                newColumns = self.get_cache_file(file_name)["columns"]
                for cc in newColumns:
                    self.panel_header_gbox.layout().addWidget(cc)
            else:
                for column in data.columns:
                    check_box = QCheckBox(column)
                    check_box.setChecked(True)
                    self.panel_header_gbox.layout().addWidget(check_box)
                    newColumns.append(check_box)
            self._current_file["columns"] = newColumns

    def show_content(self, file_name: str, data: DataFrame):
        if self._cursor_name != file_name:
            html_buffer = io.StringIO()
            data.describe(include="all").to_html(buf=html_buffer)
            html_str = html_buffer.getvalue()
            html_buffer.close()
            self.panel_content.setText(html_str)
            self._current_file["data"] = data
            self._cursor_name = file_name

    def load_file(self, file_info: QFileInfo, data: DataFrame):
        file_name = file_info.fileName()
        if file_name in self._cache_files:
            QMessageBox.information(self, "提示", f"存在同名文件: {file_name}")
        else:
            self.add_list_item(file_info)
            self.show_header(file_name, data)
            self.show_content(file_name, data)
            self.set_cache_file(file_name, self._current_file.copy())

    def set_cache_file(self, file_name: str, current_file: dict):
        self._cache_files[file_name] = current_file

    def get_cache_file(self, file_name: str):
        return self._cache_files.get(file_name)

    @Slot()
    def click_list_item(self, item: QListWidgetItem):
        file_name = item.text()
        if file_name in self._cache_files:
            data = self._cache_files[file_name]["data"]
            self.show_header(file_name, data)
            self.show_content(file_name, data)

    def reset_and_clean_memory(self):
        # reset UI
        self.panel_content.clear()
        self.menu_widget.clear()
        columns = self._current_file["columns"]
        for cl in columns:
            cl.setParent(None)
            self.panel_header_gbox.layout().removeWidget(cl)

        # clean UI
        UITools.clear_ui_checkbox([self._current_file])
        UITools.clear_ui_checkbox(list(self._cache_files.values()))

        # clean memory
        self._current_file = {"columns": [], "data": None}
        self._cache_files = {}
        self._cursor_name = None

        # gc
        gc.collect()

    def get_data_list(self) -> list:
        data_list = []
        for file in self._cache_files.values():
            selected_columns = file["data"][[combox.text() for combox in file["columns"] if combox.isChecked()]]
            data_list.append(selected_columns)
        return data_list


__all__ = ["AttendanceHome"]
