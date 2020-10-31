"""Model base classes."""
# pylint: disable=unused-argument
from typing import Any, Tuple

from PySide2.QtCore import QObject, QIdentityProxyModel, QModelIndex, Qt


class BaseTableProxyModel(QIdentityProxyModel):
    """Proxy model that display a list model as a table model using a different role per column."""

    _HEADERS = ()  # type: Tuple[str, ...]
    _ROLES = ()  # type: Tuple[int, ...]

    def columnCount(self, parent=None):
        return len(self._HEADERS)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return self.sourceModel().rowCount(parent)

    def flags(self, index):
        # We don't use the index as it will only work for the first column.
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData(self, section, orientation, role=None):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._HEADERS[section].title()
        return super().headerData(section, orientation, role=role)

    def data(self, index, role=None):
        source_index = self.mapToSource(index)
        if role in (Qt.DisplayRole, Qt.EditRole):
            role = self._ROLES[index.column()]
        return self.sourceModel().data(source_index, role)

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.EditRole) -> bool:
        if role == Qt.EditRole:
            role = self._ROLES[index.column()]
        return super().setData(index, value, role)

    # We need to re-implement index, parent, mapToSource and mapFromSource to expose extra rows.
    # https://www.qtcentre.org/threads/63199-Add-virtual-rows-amp-columns-to-a-proxy-model

    def index(
        self, row: int, column: int, parent: QModelIndex = QModelIndex()
    ) -> QModelIndex:
        return self.createIndex(row, column, parent)

    def parent(self, index: QModelIndex) -> QObject:  # type: ignore
        return QModelIndex()  # work only for non-tree models

    def mapFromSource(self, sourceIndex: QModelIndex) -> QModelIndex:
        return self.index(sourceIndex.row(), sourceIndex.column(), QModelIndex())

    def mapToSource(self, proxyIndex: QModelIndex) -> QModelIndex:
        if not self.sourceModel() or not proxyIndex.isValid():
            return QModelIndex()
        # Note: I would expect to use self.sourceModel().index(...) here.
        # However doing so make columns at index >1 non-editable...
        return self.index(proxyIndex.row(), proxyIndex.column(), QModelIndex())
