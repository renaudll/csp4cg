"""Widget displaying a list of artists."""
# pylint: disable=no-member
from typing import Dict, Any

from PySide2.QtCore import (
    QObject,
    QSortFilterProxyModel,
    Signal,
    Qt,
    QAbstractListModel,
    QModelIndex,
)
from PySide2.QtWidgets import (
    QWidget,
    QDockWidget,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QTableView,
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
)

from csp4cg.core import Artist, Context
from csp4cg.gui._manager import Manager
from csp4cg.gui._utils import (
    show_open_dialog,
    show_save_dialog,
    context_reset_model,
    iter_selected_rows_data,
)
from csp4cg.gui.widgets import _base

RoleArtistName = Qt.UserRole + 1001  # 1257
RoleArtistAvailability = Qt.UserRole + 1002  # 1258
RoleArtistTags = Qt.UserRole + 1003  # 1259


class ArtistsWidget(QDockWidget):
    """Widget displaying a list of artists."""

    artistDeleted = Signal()

    def __init__(self, parent: QObject, manager: Manager):
        super().__init__(parent)
        self.setWindowTitle("Artists")
        self._manager = manager

        # Build widgets
        self.search_field = QLineEdit(self)
        self.table = QTableView(self)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.button_add = QPushButton("Add", self)
        self.button_remove = QPushButton("Remove", self)
        self.button_import = QPushButton("Import", self)
        self.button_export = QPushButton("Export", self)

        # Build layout
        layout_main = QVBoxLayout()
        layout_footer = QHBoxLayout()
        layout_footer.addWidget(self.search_field)
        layout_footer.addWidget(self.button_add)
        layout_footer.addWidget(self.button_remove)
        layout_footer.addWidget(self.button_import)
        layout_footer.addWidget(self.button_export)
        layout_main.addLayout(layout_footer)
        layout_main.addWidget(self.table)

        main_widget = QWidget(self)
        main_widget.setLayout(layout_main)
        self.setWidget(main_widget)

        # Configure model
        self.model = ArtistsListModel(self, self._manager.context)
        self._model_table = ArtistListToTableProxyModel(self)
        self._model_table.setSourceModel(self.model)
        self._model_table_proxy = QSortFilterProxyModel(self)
        self._model_table_proxy.setSourceModel(self._model_table)

        # Configure view
        self.table.setModel(self._model_table_proxy)

        # Connect signals
        for signal, callback in (
            (self.model.dataChanged, self._on_data_changed),
            (self.button_add.pressed, self._on_add),
            (self.button_remove.pressed, self._on_remove),
            (self.button_export.pressed, self._on_export),
            (self.button_import.pressed, self._on_import),
            (
                self.search_field.textChanged,
                self._model_table_proxy.setFilterWildcard,
            ),
        ):
            signal.connect(callback)

    def _on_add(self):
        """Add an artist to the list."""
        with context_reset_model(self.model):
            self._manager.add_artist()

    def _on_remove(self):
        """Remove selected artists from the list."""
        artists = tuple(self._iter_selected())
        if not artists:
            return

        with context_reset_model(self.model):
            self._manager.remove_artists(artists)
        self.artistDeleted.emit()

    def _on_export(self):
        """Export the list of artists to a .csv file."""
        path = show_save_dialog(self, "Export Artist", "CSV (*.csv)")
        if not path:
            return
        self._manager.export_artists(path)

    def _on_import(self):
        """Import the list of artists from a .csv file."""
        path = show_open_dialog(self, "Import Artists", "CSV (*.csv)")
        if not path:
            return

        with context_reset_model(self.model):
            self._manager.import_artists(path)

    def _on_data_changed(
        self, top_left, bottom_right, roles
    ):  # pylint: disable=unused-argument
        """Called when the internal data changed. Notify if the change affect the solve."""
        if {RoleArtistAvailability, RoleArtistTags} & set(roles):
            self._manager.set_dirty()

    def _iter_selected(self):
        return iter_selected_rows_data(self.table)


class ArtistsListModel(QAbstractListModel):
    """Model for a list of artists."""

    def __init__(self, parent: QObject, context: Context):
        super().__init__(parent)
        self._context = context
        self.set_context(context)

    def roleNames(self) -> Dict:
        return {
            RoleArtistName: b"name",
            RoleArtistAvailability: b"availability",
            RoleArtistTags: b"tags",
        }

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.EditRole) -> bool:
        artist = self._context.artists[index.row()]

        setter = {
            Qt.EditRole: _set_artist_name,
            RoleArtistName: _set_artist_name,
            RoleArtistAvailability: _set_artist_availability,
            RoleArtistTags: _set_artist_tags,
        }.get(role)

        if not setter:
            raise NotImplementedError(f"setData not implemented for role {role}")

        if setter(artist, value):
            self.dataChanged.emit(index, index, [role])
            return True
        return False

    def rowCount(  # pylint: disable=unused-argument
        self, parent: QModelIndex = QModelIndex()
    ) -> int:
        return len(self._context.artists) if self._context else 0

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        artist = self._context.artists[index.row()]
        if role == Qt.UserRole:
            return artist
        if role in (Qt.DisplayRole, Qt.EditRole, RoleArtistName):
            return artist.name
        if role == RoleArtistAvailability:
            return str(artist.availability)
        if role == RoleArtistTags:
            return ",".join(f"{name}:{weight}" for name, weight in artist.tags.items())
        return None

    def set_context(self, context: Context):
        """Reset the model with a new context."""
        self.beginResetModel()
        self._context = context
        self.endResetModel()


def _set_artist_name(artist: Artist, value: str) -> bool:
    """Set an artist name from a string value.

    :param artist: An artist
    :param value: The artist new name
    :return: Was the artist name changed?
    """
    if artist.name == value:
        return False
    artist.name = value
    return True


def _set_artist_availability(artist: Artist, value: str) -> bool:
    """Set an artist availability from a string value.

    :param artist: An artist
    :param value: The artist availability as a string
    :return: Was the artist availability changed?
    """
    availability = int(value)
    if artist.availability == availability:
        return False
    artist.availability = availability
    return True


def _set_artist_tags(artist: Artist, value: str) -> bool:
    """Set an artist tags from a string value.

    :param artist: An artist
    :param value: The artist tags as a string
    :return: Was the artist tags changed?
    """
    try:
        tags = {
            key: int(val)
            for key, val in (token.split(":", 1) for token in value.split(",") if token)
        }
    except ValueError:
        return False
    if artist.tags == tags:
        return False
    artist.tags = tags
    return True


class ArtistListToTableProxyModel(_base.BaseTableProxyModel):
    """Proxy model that adapt an artists list model to a table model."""

    _HEADERS = ("name", "availability", "tags")
    _ROLES = (RoleArtistName, RoleArtistAvailability, RoleArtistTags)

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        return super().flags(index) | Qt.ItemIsEditable
