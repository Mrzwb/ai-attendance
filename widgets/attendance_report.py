from PySide6.QtCore import QSortFilterProxyModel, QMargins, Qt, QSize, Slot
from PySide6.QtWidgets import QTableView, QHeaderView, QVBoxLayout, QWidget, QFormLayout, QPushButton, QLineEdit, \
    QLabel, QGridLayout, QSizePolicy, QHBoxLayout, QLayoutItem
from pandas import DataFrame

from model.tablemodel import TableModel
from .customization import PaginationPanel, Pagination


class AttendanceReport(QWidget):
    _data: DataFrame = None

    def __init__(self, data: DataFrame):
        super().__init__()
        self._data = data

        # 分页面板
        count = data.shape[0] if data is not None else 0
        self.page_panel = PaginationPanel(total=count, page_size=15)
        self.page_panel.page_changed.connect(self.change_page)

        # 表格面板
        self.table_mode = TableModel()
        if self._data is not None:
            self.table_mode.load_data(self._data.iloc[0:15])
        self.tabel_panel = TablePanel(self.table_mode)

        # 查询面板
        #self.search_panel = SearchPanel(data)

        layout = QVBoxLayout()
        layout.setContentsMargins(QMargins())
        #layout.addWidget(self.search_panel, 1)
        layout.addWidget(self.tabel_panel, 9)
        layout.addWidget(self.page_panel, 1)
        self.setLayout(layout)

    @Slot(Pagination)
    def change_page(self, pages: Pagination):
        start = (pages.current_page - 1) * pages.page_size
        end = pages.current_page * pages.page_size
        end = pages.total if end > pages.total else end
        self.table_mode.load_data(self._data.iloc[start:end])

class SearchPanel(QWidget):

    def __init__(self, data: DataFrame):
        super().__init__()
        self._search_button = QPushButton("查询")
        self._search_button.setFixedHeight(25)
        self._name_label = QLabel("&姓名:")
        self._name_line_edit = QLineEdit()
        self._name_line_edit.setClearButtonEnabled(True)
        self._name_label.setBuddy(self._name_line_edit)
        self._emp_no_label = QLabel("&工号:")
        self._emp_no_line_edit = QLineEdit()
        self._emp_no_line_edit.setClearButtonEnabled(True)
        self._emp_no_label.setBuddy(self._emp_no_line_edit)

        grid_layout = QGridLayout(self)
        grid_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        grid_layout.addWidget(self._name_label, 0, 0)
        grid_layout.addWidget(self._name_line_edit, 0, 1, 0, 1)
        grid_layout.addWidget(self._emp_no_label, 0, 2)
        grid_layout.addWidget(self._emp_no_line_edit, 0, 3, 0, 1)
        grid_layout.addWidget(self._search_button, 0, 4)


class TablePanel(QTableView):

    def __init__(self, model: TableModel):
        super().__init__()

        # QTableView Headers
        self.horizontal_header = self.horizontalHeader()
        self.vertical_header = self.verticalHeader()
        self.horizontal_header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.vertical_header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.horizontal_header.setStretchLastSection(True)
        self.setSelectionBehavior(self.SelectionBehavior.SelectRows)

        # QTableView model
        proxy_model = QSortFilterProxyModel(self)
        proxy_model.setSourceModel(model)
        proxy_model.setDynamicSortFilter(True)
        self.setModel(proxy_model)


__all__ = ["AttendanceReport"]
