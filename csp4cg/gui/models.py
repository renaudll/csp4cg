import datetime
import typing

from PySide2 import QtGui, QtCore


class BaseListModel(QtGui.QStandardItemModel):
    _ATTRS = []

    def __init__(self, entries):
        super().__init__()
        self._data = entries
        self._update()

    def setData(
        self, index: QtCore.QModelIndex, value: typing.Any, role: int = ...
    ) -> bool:
        """Re-implement QtCore.QAbstractItemModel.setData. Update internal data.

        :param index:
        :param value:
        :param role:
        :return:
        """
        col = index.column()
        row = index.row()
        attr = self._ATTRS[col]
        artist = self._data[row]
        setattr(artist, attr, value)
        return True

    def columnWidth(self, index: QtCore.QModelIndex):
        # https://www.youtube.com/watch?v=vwukO5Vusv8 at 12:47
        return 20

    def _update(self):
        self.clear()
        for entry in self._data:
            self.addItem(entry)

    def addItem(self, *args):
        # TODO: Use custom role instead of display?
        items = []
        for arg in args:
            item = QtGui.QStandardItem(str(arg))
            item.setData("test", QtCore.Qt.UserRole + 100)
            items.append(item)
        self.appendRow(items)


class AssignmentsModel(BaseListModel):
    """Qt Model that list artist/shot assignation."""

    _ATTRS = ["name", "shots", "workload"]

    def addItem(self, entry):
        artist, shots = entry
        workload = sum((shot.duration for shot in shots), datetime.timedelta())
        shots = " ,".join(shot.name for shot in shots)
        workload = "%s hours" % (workload.total_seconds() / 60 / 60)
        super(AssignmentsModel, self).addItem(artist.name, shots, workload)


class ArtistsModel(BaseListModel):
    """Qt Model that list artists."""

    _ATTRS = ["name", "availability"]

    def addItem(self, artist):
        super(ArtistsModel, self).addItem(artist.name, artist.availability)


class ShotListModel(BaseListModel):
    """Qt Model that list shots."""

    _ATTRS = ["name", "duration"]
