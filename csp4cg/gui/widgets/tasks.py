"""Widget that display a list of assignable tasks."""
# pylint: disable=no-member
import datetime
import itertools
import operator
from typing import Sequence, Dict, Any, Iterable, Callable, Generator, Tuple

from PySide2.QtCore import (
    QObject,
    QSortFilterProxyModel,
    QModelIndex,
    Qt,
    QAbstractListModel,
    QEvent,
    Signal,
)
from PySide2.QtWidgets import (
    QWidget,
    QStyleOptionViewItem,
    QComboBox,
    QItemDelegate,
    QHBoxLayout,
    QLineEdit,
    QVBoxLayout,
    QAbstractItemView,
    QPushButton,
    QDockWidget,
    QHeaderView,
)

from csp4cg.core import Context, Assignment
from csp4cg.gui._manager import Manager
from csp4cg.gui._utils import context_reset_model, iter_selected_rows_data
from csp4cg.gui.widgets import _base
from .._utils import show_save_dialog, show_open_dialog

RoleTaskXCoord = Qt.UserRole + 1001  # 1257
RoleTaskYCoord = Qt.UserRole + 1002  # 1258
RoleTaskWidth = Qt.UserRole + 1003  # 1259
RoleTaskArtist = Qt.UserRole + 1004  # 1260
RoleTaskLocked = Qt.UserRole + 1006  # 1262
RoleTaskDuration = Qt.UserRole + 1007  # 1263
RoleTaskTags = Qt.UserRole + 1008  # 1264
RoleTaskName = Qt.UserRole + 1009  # 1265
RoleAssignment = Qt.UserRole + 1010  # 1266


class TasksWidget(QDockWidget):
    """Widget that display a list of assignable tasks."""

    taskDeleted = Signal()

    def __init__(self, parent: QObject, manager: Manager):
        super().__init__(parent)
        self._manager = manager

        self.setWindowTitle("Tasks")

        # Build widget
        self.search_field = QLineEdit(self)
        self.table = _base.ExcelLikeTableView(self)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.button_add = QPushButton("Add", self)
        self.button_remove = QPushButton("Remove", self)
        self.button_import = QPushButton("Import", self)
        self.button_export = QPushButton("Export", self)

        # Build layout
        layout_footer = QHBoxLayout()
        layout_footer.addWidget(self.search_field)
        layout_footer.addWidget(self.button_add)
        layout_footer.addWidget(self.button_remove)
        layout_footer.addWidget(self.button_import)
        layout_footer.addWidget(self.button_export)
        layout_content = QVBoxLayout()
        layout_content.addLayout(layout_footer)
        layout_content.addWidget(self.table)

        main_widget = QWidget()
        main_widget.setLayout(layout_content)
        self.setWidget(main_widget)

        # Configure model
        self.model = TasksListModel(self, self._manager.context)
        model_table = TasksListToTableProxyModel(self)
        model_table.setSourceModel(self.model)
        model_table_proxy = QSortFilterProxyModel(self)
        model_table_proxy.setSourceModel(model_table)

        # Configure view
        self.table.setModel(model_table_proxy)
        self.artist_delegate = ArtistDelegate(self, self._manager)
        self.table.setItemDelegateForColumn(2, self.artist_delegate)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Connect signals
        for signal, callback in (
            (self.model.dataChanged, self._on_data_changed),
            (self.button_add.pressed, self.add_task),
            (self.button_remove.pressed, self.remove_tasks),
            (self.button_export.pressed, self.export_tasks),
            (self.button_import.pressed, self.import_tasks),
            (
                self.search_field.textChanged,
                model_table_proxy.setFilterWildcard,
            ),
        ):
            signal.connect(callback)

    def add_task(self):
        """Add a task to the list."""
        with context_reset_model(self.model):  # TODO: Use _context_insert_row
            self._manager.add_task()

    def remove_tasks(self):
        """Remove selected tasks from the list."""
        tasks = tuple(self._iter_selected())
        if not tasks:
            return

        with context_reset_model(self.model):
            self._manager.remove_tasks(tasks)

        self.taskDeleted.emit()

    def import_tasks(self):
        """Import the list of tasks from a .csv file."""
        path = show_open_dialog(self, "Import Shots", "CSV (*.csv)")
        if not path:
            return

        with context_reset_model(self.model):
            self._manager.import_tasks(path)

    def export_tasks(self):
        """Export the list of tasks to a .csv file."""
        path = show_save_dialog(self, "Export Shots", "CSV (*.csv)")
        if not path:
            return
        self._manager.export_tasks(path)

    def _on_data_changed(
        self, top_left, bottom_right, roles
    ):  # pylint: disable=unused-argument
        if {RoleTaskArtist, RoleTaskDuration, RoleTaskTags} & set(roles):
            self._manager.set_dirty()

    def _iter_selected(self):
        return iter_selected_rows_data(self.table)


class TasksListModel(QAbstractListModel):
    """Widget displaying tasks."""

    def __init__(self, parent: QObject, context: Context):
        super().__init__(parent)
        self._context = context
        self._extra_roles = {}  # type: Dict[int, Dict[int, Any]]

    def roleNames(self) -> Dict:
        return {
            RoleTaskXCoord: b"coordX",
            RoleTaskYCoord: b"coordY",
            RoleTaskWidth: b"gantBarWidth",
            RoleTaskArtist: b"artist",
            RoleTaskLocked: b"locked",
            RoleTaskDuration: b"duration",
            RoleTaskTags: b"tags",
            RoleTaskName: b"name",
        }

    def rowCount(  # pylint: disable=unused-argument
        self, parent: QModelIndex = QModelIndex()
    ) -> int:
        return len(self._context.tasks) if self._context else 0

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        row = index.row()
        task = self._context.tasks[row]
        if role in (Qt.DisplayRole, Qt.EditRole, RoleTaskName):
            return task.name
        if role == Qt.UserRole:
            return task
        if role == RoleTaskDuration:
            return str(task.duration.total_seconds() / 60 / 60)  # hours
        if role == RoleTaskWidth:
            return task.duration.total_seconds() / 60 / 60  # hours
        if role == RoleTaskTags:
            return ",".join(task.tags)
        if role == RoleTaskLocked:
            return any(
                assignment.task == task for assignment in self._context.assignments
            )
        if role in (
            RoleTaskXCoord,
            RoleTaskYCoord,
            RoleTaskArtist,
            RoleAssignment,
        ):
            try:
                return self._extra_roles[row][role]
            except (IndexError, KeyError):  # cache need to be regenerated
                self.resetInternalData()
            return self._extra_roles[row][role]

        return None

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.EditRole) -> bool:
        task = self._context.tasks[index.row()]

        if role == RoleTaskName:
            if value == task.name:
                return False
            task.name = value
            self.dataChanged.emit(index, index, [role])
            return True

        if role == RoleTaskDuration:
            try:
                value = datetime.timedelta(hours=float(value))
            except ValueError:
                return False
            if value == task.duration:
                return False
            task.duration = value
            self.dataChanged.emit(index, index, [role])
            return True

        if role == RoleTaskTags:
            value = [name.strip() for name in value.split(",")]
            value = [name for name in value if name]
            if value == task.tags:
                return False
            task.tags = value
            self.dataChanged.emit(index, index, [role])
            return True

        if role == RoleTaskLocked:
            assignment = self.data(index, RoleAssignment)  # type: Assignment
            if value:
                self._context.assign(assignment.task, assignment.artist)
            else:
                self._context.unassign(assignment.task)
            self.dataChanged.emit(index, index, [role])
            return True

        if role == RoleTaskArtist:
            artist = next(
                (artist for artist in self._context.artists if artist.name == value)
            )
            self._context.assign(task, artist)
            self.resetInternalData()
            # TODO: The BaseTableProxyModel prevent the locked column to be invalidated...
            self.dataChanged.emit(index, index, [role])
            return True

        raise NotImplementedError(f"setData not implemented for role {role}")

    def set_context(self, context: Context):
        """Update the model with a new context."""
        self.beginResetModel()
        self._context = context
        self.resetInternalData()
        self.endResetModel()

    def resetInternalData(self):
        """Recompute the extra roles cache."""
        self._extra_roles = [
            {
                RoleTaskXCoord: 0.0,
                RoleTaskYCoord: 0.0,
                RoleTaskArtist: None,
                RoleAssignment: None,
            }
            for _ in range(self.rowCount())
        ]

        index_by_task = {task: index for index, task in enumerate(self._context.tasks)}

        # Join hard assignments and current assignments
        assignments = set(self._context.solution) | set(self._context.assignments)

        for assignment, x_coord, y_coord in _iter_assignments_coords(assignments):
            index = index_by_task[assignment.task]
            self._extra_roles[index].update(
                {
                    RoleTaskXCoord: x_coord,
                    RoleTaskYCoord: y_coord,
                    RoleAssignment: assignment,
                    RoleTaskArtist: assignment.artist.name,
                }
            )


class TasksListToTableProxyModel(_base.BaseTableProxyModel):
    """Proxy model that adapt a tasks list model to a table model."""

    _HEADERS = ("Name", "Duration", "Artist", "Locked", "Tags")
    _ROLES = (
        RoleTaskName,
        RoleTaskDuration,
        RoleTaskArtist,
        RoleTaskLocked,
        RoleTaskTags,
    )

    def data(self, index, role=Qt.DisplayRole) -> Any:
        if index.column() == 3 and role == Qt.CheckStateRole:
            state = super().data(index, RoleTaskLocked)
            return Qt.Checked if state else Qt.Unchecked

        if index.column() == 3 and role == Qt.DisplayRole:
            return ""

        return super().data(index, role)

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.EditRole) -> bool:
        if role == Qt.CheckStateRole:
            role = RoleTaskLocked
        return super().setData(index, value, role)

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        flags = super().flags(index)
        if index.column() == 3:  # locked
            flags |= Qt.ItemIsUserCheckable
        else:
            flags |= Qt.ItemIsEditable
        return flags


class ArtistDelegate(QItemDelegate):
    """Delegate for a cell representing an artist."""

    def __init__(self, parent: QObject, manager: Manager):
        super().__init__(parent)
        self._manager = manager

    def eventFilter(self, obj: QComboBox, event: QEvent):
        """Event filter that ensure the QComboBox popup as soon as the delegate is created."""
        # src: https://forum.qt.io/topic/51476/qcombobox-delegate-best-way-to-show-the-popup-menu-immediately
        if event.type() == QEvent.FocusIn and event.reason() != Qt.PopupFocusReason:
            obj.showPopup()
        return super().eventFilter(obj, event)

    def createEditor(  # pylint: disable=unused-argument
        self,
        parent: QWidget,
        option: QStyleOptionViewItem,
        index: QModelIndex,
    ) -> QWidget:
        """Create the delegate editor."""
        widget = QComboBox(parent)
        widget.addItems([artist.name for artist in self._manager.context.artists])
        widget.currentIndexChanged.connect(  # pylint: disable=no-member
            self._on_current_index_changed
        )
        return widget

    def setEditorData(self, editor: QComboBox, index: QModelIndex):
        """Update the editor."""
        items = [artist.name for artist in self._manager.context.artists]
        current = index.model().data(index, RoleTaskArtist)
        try:
            row = items.index(current)
        except ValueError:  # None is not in list
            row = -1
        editor.blockSignals(True)
        editor.setCurrentIndex(row)
        editor.blockSignals(False)

    def setModelData(self, editor, model, index):
        """Update the model."""
        model.setData(index, editor.currentText())

    def _on_current_index_changed(self):
        """Called when the combobox current index changed."""
        self.commitData.emit(self.sender())  # pylint: disable=no-member


def _iter_assignments_coords(
    assignments: Sequence[Assignment],
) -> Generator[Tuple[Assignment, float, float], None, None]:
    """Compute assignments x/y coordinates on the gantt."""
    assignments = sorted(assignments, key=operator.attrgetter("task"))
    artists = sorted({assignment.artist for assignment in assignments})
    for artist, artist_assignments in _groupby_sorted(
        assignments, operator.attrgetter("artist")
    ):
        y_coord = float(artists.index(artist))
        x_coord = 0.0
        for assignment in artist_assignments:
            width = assignment.task.duration.total_seconds() / 60 / 60  # hours
            yield assignment, x_coord, y_coord
            x_coord += width


def _groupby_sorted(iterable: Iterable, func: Callable):
    """Wrapper around itertools groupby that ensure data is sorted before grouping."""
    yield from itertools.groupby(sorted(iterable, key=func), func)
