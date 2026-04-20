from PySide6.QtCore import Slot, QMargins, QSortFilterProxyModel
from PySide6.QtWidgets import QWidget, QTableView, QVBoxLayout, QHeaderView
from pandas import DataFrame

from model.tablemodel import TableModel
from .customization import PaginationPanel, Pagination


class FinanceReport(QWidget):
    _data: DataFrame = None

    def __init__(self, data: DataFrame, column_name: tuple = None):
        super().__init__()
        self._data = data

        # 分页面板
        count = data.shape[0] if data is not None else 0
        self.page_panel = PaginationPanel(total=count, page_size=15)
        self.page_panel.page_changed.connect(self.change_page)

        # 表格面板
        self.table_mode = TableModel(None, column_name)
        if self._data is not None:
            self.table_mode.load_data(self._data.iloc[0:15])
        self.tabel_panel = TablePanel(self.table_mode)

        layout = QVBoxLayout()
        layout.setContentsMargins(QMargins())
        # layout.addWidget(self.search_panel, 1)
        layout.addWidget(self.tabel_panel, 9)
        layout.addWidget(self.page_panel, 1)
        self.setLayout(layout)

    @Slot(Pagination)
    def change_page(self, pages: Pagination):
        start = (pages.current_page - 1) * pages.page_size
        end = pages.current_page * pages.page_size
        end = pages.total if end > pages.total else end
        self.table_mode.load_data(self._data.iloc[start:end])


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


__all__ = ["FinanceReport"]

