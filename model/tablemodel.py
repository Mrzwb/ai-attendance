from __future__ import annotations

from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QColor
from pandas import DataFrame
import numpy as np
from model.templates import REPORT_HEADER_ATT


class TableModel(QAbstractTableModel):
    _column_name: tuple = REPORT_HEADER_ATT
    _value: np.ndarray
    column_count: int
    row_count: int

    def __init__(self, data: DataFrame = None, column_name: tuple = None):
        QAbstractTableModel.__init__(self)
        if column_name is not None:
            self._column_name = column_name
        self.load_data(data)

    def load_data(self, data: DataFrame):
        self.beginResetModel()
        self._value = [] if data is None else data.values
        self.column_count = len(self._column_name)
        self.row_count = len(self._value)
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        return self.row_count

    def columnCount(self, parent=QModelIndex()):
        return self.column_count

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        """ Set the headers to be displayed. """
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return self._column_name[section]
        else:
            return f"{section + 1}" if section != -1 else None

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        if not 0 <= index.row() < self.row_count:
            return None

        if not 0 < self.row_count:
            return None

        if not index.column() < self._value.shape[1]:
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            return self._value[index.row(), index.column()]
        elif role == Qt.ItemDataRole.BackgroundRole:
            return QColor(Qt.GlobalColor.white)
        elif role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        return None

    def insertRows(self, position, rows=1, index=QModelIndex()):
        """ Insert a row into the model. """
        self.beginInsertRows(QModelIndex(), position, position + rows - 1)
        """
         to-do
        """
        self.endInsertRows()
        return True

    def removeRows(self, position, rows=1, index=QModelIndex()):
        """ Remove a row from the model. """
        self.beginRemoveRows(QModelIndex(), position, position + rows - 1)
        """
         to-do
        """
        self.endRemoveRows()
        return True

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        """ Adjust the data (set it to <value>) depending on the given
            index and role.
        """
        if role != Qt.ItemDataRole.EditRole:
            return False

        if index.isValid() and 0 <= index.row() < self.row_count:
            """
            to-do
            """
            self.dataChanged.emit(index, index, 0)
            return True

        return False

    def flags(self, index):
        """ Set the item flags at the given index. Seems like we're
            implementing this function just to see how it's done, as we
            manually adjust each tableView to have NoEditTriggers.
        """
        if not index.isValid():
            return Qt.ItemFlag.ItemIsEnabled
        return Qt.ItemFlag(QAbstractTableModel.flags(self, index)
                            | Qt.ItemFlag.ItemIsEnabled)
