# Copyright (C) 2025 zhouwb <zhouwb15@chinaunicom.cn>
from dataclasses import dataclass

from PySide6.QtCore import Qt, QSize, Slot, Signal, QObject
from PySide6.QtGui import QPalette, QAction, QMouseEvent
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QSizePolicy, QComboBox


@dataclass
class Pagination:
    total: int
    current_page: int = 1
    page_size: int = 15

    def __init__(self, /, count: int, page_size: int):
        self.total = count
        self.page_size = page_size

    # 下一页
    def next(self):
        if self.current_page < self.page_count:
            self.current_page += 1

    # 上一页
    def prev(self):
        if self.current_page > 1:
            self.current_page -= 1

    # 首页
    def first(self):
        self.current_page = 1

    # 最后一页
    def last(self):
        self.current_page = self.page_count

    # 跳至第几页
    def go(self, value):
        if 1 <= value <= self.page_count:
            self.current_page = value

    # 总页数
    @property
    def page_count(self):
        return self.total // self.page_size + 1


class PaginationPanel(QWidget):
    _limit_len: int = 7

    page_changed = Signal(Pagination)

    def __init__(self, *, total: int, page_size: int, choose_page_size: bool = True):
        super().__init__()
        self.pagination = Pagination(total, page_size)
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.horizontal_layout = QHBoxLayout()
        self.horizontal_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.main_layout.addLayout(self.horizontal_layout)
        self.create_view()
        if choose_page_size:
            self.create_combox()

    def create_view(self):
        page_count = self.pagination.page_count
        current_page = self.pagination.current_page

        if page_count > 1:
            self.create_label("上一页")
            times = current_page // self._limit_len
            times = times - 1 if current_page % self._limit_len == 0 else times
            start_num = self._limit_len * times + 1
            while start_num <= page_count:
                label = self.create_label(f"{start_num}")
                if start_num == current_page:
                    label.setStyleSheet("font:bold;color:#565DDE;min-width:20px;")
                if start_num % self._limit_len == 0:
                    break
                start_num += 1
            self.create_label("下一页")

    def create_label(self, text: str):
        _label = PaginationLabel(text)
        _label.clicked.connect(self.click_label)
        self.horizontal_layout.addWidget(_label)
        return _label

    @Slot(str)
    def click_label(self, text: str):
        match text:
            case "上一页":
                self.pagination.prev()
            case "下一页":
                self.pagination.next()
            case _:
                self.pagination.current_page = int(text)
        self.clean_layout()
        self.create_view()
        self.page_changed.emit(self.pagination)

    def create_combox(self):
        if self.pagination.page_count > 1:
            _combox = QComboBox()
            _combox.addItem("15", 15)
            _combox.addItem("50", 50)
            _combox.addItem("100", 100)
            _combox.currentTextChanged.connect(self.change_combox)
            self.main_layout.addWidget(_combox)

    @Slot(str)
    def change_combox(self, value):
        self.pagination.page_size = int(value)
        self.pagination.current_page = 1
        self.clean_layout()
        self.create_view()
        self.page_changed.emit(self.pagination)

    def clean_layout(self):
        item = self.horizontal_layout.takeAt(0)
        while item:
            widget = item.widget()
            widget.setParent(None)
            self.horizontal_layout.removeWidget(widget)
            self.horizontal_layout.removeItem(item)
            del widget
            del item
            item = self.horizontal_layout.takeAt(0)


class PaginationLabel(QLabel):
    clicked = Signal(str)

    def __init__(self, text: str):
        super().__init__(text)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.adjustSize()
        self.setStyleSheet("""
            QLabel {
                min-width: 20px;
            }
            QLabel:hover {
                background-color: #efefef;
            }
        """)

    def mousePressEvent(self, ev: QMouseEvent, /):
        super().mouseReleaseEvent(ev)
        self.clicked.emit(self.text())

    def mouseReleaseEvent(self, ev: QMouseEvent, /):
        super().mouseReleaseEvent(ev)
