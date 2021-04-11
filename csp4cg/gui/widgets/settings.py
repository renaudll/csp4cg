"""Widget that display current solver settings."""
# pylint: disable=no-member
from typing import Any

from PySide2.QtCore import QObject, QAbstractTableModel, QModelIndex, Qt
from PySide2.QtWidgets import (
    QVBoxLayout,
    QDockWidget,
    QWidget,
    QHeaderView,
    QAbstractItemView,
)

from csp4cg.core._types import Settings
from ._base import ExcelLikeTableView
from .._manager import Manager


class SettingsWidget(QDockWidget):
    """Widget that display current solver settings."""

    def __init__(self, parent: QObject, manager: Manager):
        super().__init__(parent)

        self.setWindowTitle("Settings")

        self._manager = manager

        # Build widgets
        self.table = ExcelLikeTableView(self)
        self.table.verticalHeader().hide()
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)

        # Build layout
        layout_main = QVBoxLayout()
        layout_main.addWidget(self.table)

        main_widget = QWidget(self)
        main_widget.setLayout(layout_main)
        self.setWidget(main_widget)

        # Configure model
        self.model = SettingsModel(self._manager.context.settings, self)
        self.table.setModel(self.model)


class SettingsModel(QAbstractTableModel):
    """Model that display solver settings."""

    _HEADERS = ("Name", "Value")
    _ATTRS = (
        "weight_tags",
        "weight_equal_hours_by_artists",
        "weight_equal_tasks_count_by_artists",
    )

    def __init__(self, settings: Settings, parent: QObject = None):
        super().__init__(parent)
        self._settings = settings

    def set_settings(self, settings: Settings):
        """Reset the model with new settings."""
        self.beginResetModel()
        self._settings = settings
        self.endResetModel()

    def columnCount(  # pylint: disable=unused-argument
        self, parent: QModelIndex = QModelIndex()
    ) -> int:
        return len(self._HEADERS)

    def rowCount(  # pylint: disable=unused-argument
        self, parent: QModelIndex = QModelIndex()
    ) -> int:
        return len(self._ATTRS)

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole
    ) -> Any:
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._HEADERS[section]
        return super().headerData(section, orientation, role)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if role == Qt.DisplayRole:
            attr = self._ATTRS[index.row()]
            if index.column() == 0:
                return attr
            return str(getattr(self._settings, attr))  # column 1
        return None

    def setData(
        self, index: QModelIndex, value: Any, role: int = Qt.DisplayRole
    ) -> bool:
        if role == Qt.EditRole and index.column() == 1:
            attr = self._ATTRS[index.row()]
            try:
                value = int(value)  # Note: All settings are int for now.
            except ValueError:
                return False
            setattr(self._settings, attr, value)
            self.dataChanged.emit(index, index, [role])
            return True
        return super().setData(index, value, role)

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        flags = super().flags(index)
        if index.column() == 1:
            flags |= Qt.ItemIsEditable
        return flags
