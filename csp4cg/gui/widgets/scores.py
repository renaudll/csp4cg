"""Widgets displaying details about the current solve score."""
from typing import Optional

from PySide2.QtCore import QModelIndex, QSortFilterProxyModel, Qt, QObject
from PySide2.QtGui import QColor, QStandardItemModel, QStandardItem
from PySide2.QtWidgets import (
    QWidget,
    QHeaderView,
    QTableView,
    QHBoxLayout,
    QVBoxLayout,
    QCheckBox,
    QLineEdit,
    QAbstractItemView,
    QDockWidget,
)


_COLOR_BONUS = QColor(50, 100, 50)
_COLOR_MALUS = QColor(100, 50, 50)
RoleScore = Qt.UserRole + 1


class ScoresWidget(QDockWidget):
    """Widget that display a solution scores."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Scores")

        # Build widgets
        self.search_field = QLineEdit(self)
        self.checkbox_positive = QCheckBox("Positive", self)
        self.checkbox_positive.setChecked(True)
        self.checkbox_negative = QCheckBox("Negative", self)
        self.checkbox_negative.setChecked(True)
        self.checkbox_neutral = QCheckBox("Neutral", self)
        self.table = QTableView(self)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)

        # Build layout
        layout_header = QHBoxLayout()
        layout_header.addWidget(self.search_field)
        layout_header.addWidget(self.checkbox_positive)
        layout_header.addWidget(self.checkbox_negative)
        layout_header.addWidget(self.checkbox_neutral)

        layout_main = QVBoxLayout()
        layout_main.addLayout(layout_header)
        layout_main.addWidget(self.table)

        main_widget = QWidget(self)
        main_widget.setLayout(layout_main)
        self.setWidget(main_widget)

        # Configure models
        self.model = PointsTableModel(self)
        self._proxy_model = ScoreProxyModel()
        self._proxy_model.setSourceModel(self.model)
        self._proxy_model.sort(1, Qt.AscendingOrder)  # sort by lowest score by default

        # Configure table
        self.table.setModel(self._proxy_model)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Connect signals
        for signal, callback in (
            (self.search_field.textChanged, self._proxy_model.setFilterWildcard),
            (self.checkbox_positive.stateChanged, self._proxy_model.set_positive),
            (self.checkbox_negative.stateChanged, self._proxy_model.set_negative),
            (self.checkbox_neutral.stateChanged, self._proxy_model.set_neutral),
        ):
            signal.connect(callback)


class PointsTableModel(QStandardItemModel):
    """Table model that display a solution scores."""

    def __init__(self, parent: QObject):
        super().__init__(parent)

        self.setHorizontalHeaderLabels(["Name", "Score"])

    def set_scores(self, statistics):
        """Update the model with a new solution."""
        self.clear()

        for name, score in statistics:
            items = [QStandardItem(name), QStandardItem(str(score))]
            color = _color_from_score(score)

            for item in items:
                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                item.setData(score, RoleScore)
                if color:
                    item.setData(color, Qt.BackgroundColorRole)

            self.appendRow(items)


class ScoreProxyModel(QSortFilterProxyModel):
    """Widgets displaying details about the current solve score."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self._show_positive = True
        self._show_negative = True
        self._show_neutral = False

    def set_positive(self, state: bool):
        """Show/hide positive scores."""
        self._show_positive = state
        self.invalidateFilter()

    def set_negative(self, state: bool):
        """Show/hide negative scores."""
        self._show_negative = state
        self.invalidateFilter()

    def set_neutral(self, state: bool):
        """Show/hide neutral scores."""
        self._show_neutral = state
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        # Filter by wildcard
        if not super().filterAcceptsRow(source_row, source_parent):
            return False

        # Otherwise filter by score
        score = self.sourceModel().data(
            self.sourceModel().index(source_row, 0), RoleScore
        )
        if score > 0:
            return self._show_positive
        if score < 0:
            return self._show_negative
        return self._show_neutral


def _color_from_score(score: int) -> Optional[QColor]:
    if score > 0:
        return _COLOR_BONUS
    if score < 0:
        return _COLOR_MALUS
    return None
