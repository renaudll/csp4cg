from PySide2 import QtCore, QtGui

import datetime
import operator
import itertools
from typing import List, Sequence, Any
from csp4cg.tasks import Artist, Shot, ShotAssignment


class BaseTableModel(QtCore.QAbstractTableModel):
    _HEADERS = ()
    _EDITABLE_COLUMNS = set()

    def __init__(self, parent, data: Sequence[object]):
        super().__init__(parent)
        self._data = data

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self._data)

    def columnCount(self, parent=None, *args, **kwargs):
        return len(self._HEADERS)

    def headerData(self, section, orientation, role=None):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self._HEADERS[section].title()
        super().headerData(section, orientation, role=role)

    def flags(self, index):
        flags = super().flags(index)
        if index.column() in self._EDITABLE_COLUMNS:
            flags |= QtCore.Qt.EditRole
        return flags

    def data(self, index, role=None):
        if role in (QtCore.Qt.DisplayRole, QtCore.Qt.EditRole):
            shot = self._data[index.row()]
            attr = self._HEADERS[index.column()]
            value = getattr(shot, attr)
            return str(value)
        if role == QtCore.Qt.UserRole:
            return self._data[index.row()]

    def setData(self, index, value, role=None):
        if role == QtCore.Qt.EditRole:
            shot = self._data[index.row()]
            attr = self._HEADERS[index.column()]
            setattr(shot, attr, value)
            self.dataChanged.emit(index, index, QtCore.Qt.DisplayRole)
            return True
        return super().setData(index, value, role=role)


class ArtistsModel(BaseTableModel):
    """Model for a list of artists."""

    _HEADERS = ("name", "availability", "tags")
    _EDITABLE_COLUMNS = {0, 1}

    def __init__(self, data: List[Artist], parent=None):
        super().__init__(parent, data)

    def setData(self, index, value, role=None):
        if index.column() == 1:  # case availability
            value = int(value)
        return super().setData(index, value, role=role)


class ShotListModel(BaseTableModel):
    """Model for a list of shots."""

    _HEADERS = ("name", "duration", "tags")
    _EDITABLE_COLUMNS = {0, 1}

    def __init__(self, data: Sequence[Shot], parent=None):
        super().__init__(parent, data)

    def setData(self, index, value, role=None):
        if index.column() == 1:  # cast shot duration
            value = datetime.timedelta(hours=float(value))
        return super().setData(index, value, role=role)


RoleXCoord = QtCore.Qt.UserRole + 1001
RoleYCoord = QtCore.Qt.UserRole + 1002
RoleWidth = QtCore.Qt.UserRole + 1003
RoleArtist = QtCore.Qt.UserRole + 1004
RoleShot = QtCore.Qt.UserRole + 1005
RoleHighlight = QtCore.Qt.UserRole + 1006


class ShotAssignmentModel(QtGui.QStandardItemModel):
    def __init__(self, parent, data):
        super().__init__(parent)
        self.setItemRoleNames(
            {
                RoleXCoord: b"coordX",
                RoleYCoord: b"coordY",
                RoleArtist: b"artist",
                RoleShot: b"shot",
                RoleWidth: b"gantBarWidth",
                RoleHighlight: b"highlight",
                QtCore.Qt.DisplayRole: b"display",
            }
        )
        self.set_internal_data(data)

    def set_internal_data(self, data: List[ShotAssignment]):
        self.clear()

        # Organize assignments by artists (x axis)
        data = sorted(
            data, key=lambda assignment_: (assignment_.artist, assignment_.shot)
        )
        for y_coord, (_, assignments) in enumerate(
            itertools.groupby(data, operator.attrgetter("artist"))
        ):
            x_coord = 0.0
            for assignment in assignments:
                item = QtGui.QStandardItem(
                    f"{assignment.artist.name} have {assignment.shot.name} "
                    f"({x_coord}, {y_coord})"
                )
                width = assignment.shot.duration.total_seconds() / 60 / 60  # hours
                item.setData(x_coord, RoleXCoord)
                item.setData(y_coord, RoleYCoord)
                item.setData(width, RoleWidth)
                item.setData(assignment.artist.name, RoleArtist)
                item.setData(assignment.shot.name, RoleShot)
                item.setData(True, RoleHighlight)
                item.setData(assignment, QtCore.Qt.UserRole)
                self.appendRow(item)
                x_coord += width


class ShotAssignmentProxyModel(QtCore.QIdentityProxyModel):
    def __init__(self, parent):
        super().__init__(parent)
        self._highlights = []

    def set_hightlights(self, assignments):
        self._highlights = assignments

    def data(self, index: QtCore.QModelIndex, role: int = ...) -> Any:
        if role == RoleHighlight:
            data = super().data(index, QtCore.Qt.UserRole)
            return not self._highlights or data in self._highlights
        return super().data(index, role)
