"""Widget that display weighted task groups."""
# pylint: disable=no-member
from typing import Any

from PySide2.QtCore import (
    QObject,
    QSortFilterProxyModel,
    Qt,
    QAbstractItemModel,
    QModelIndex,
)
from PySide2.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QAbstractItemView,
    QHBoxLayout,
    QPushButton,
    QTableView,
    QDockWidget,
    QHeaderView,
)

from csp4cg.core import Context
from csp4cg.gui._manager import Manager
from csp4cg.gui._utils import iter_selected_rows_data
from csp4cg.gui.widgets._base import BaseTableProxyModel
from ._base import ExcelLikeTableView


TasksGroupTasksRole = Qt.UserRole + 1
TasksGroupWeightRole = Qt.UserRole + 2


class TasksGroupsWidget(QDockWidget):
    """Widget that display weighted task groups."""

    def __init__(self, parent: QObject, manager: Manager, widget_tasks):
        super().__init__(parent)
        self._manager = manager
        self._tasks_widgets = widget_tasks

        self.setWindowTitle("Task Groups")

        # Build widgets
        self.search_field = QLineEdit(self)
        self.table = ExcelLikeTableView(self)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.button_add = QPushButton("Add", self)
        self.button_remove = QPushButton("Remove", self)
        self.button_import = QPushButton("Import", self)
        self.button_export = QPushButton("Export", self)

        # Build layout
        layout_header = QHBoxLayout()
        layout_header.addWidget(self.search_field)
        layout_header.addWidget(self.button_add)
        layout_header.addWidget(self.button_remove)
        layout_header.addWidget(self.button_import)
        layout_header.addWidget(self.button_export)
        layout_main = QVBoxLayout()
        layout_main.addLayout(layout_header)
        layout_main.addWidget(self.table)

        main_widget = QWidget(self)
        main_widget.setLayout(layout_main)
        self.setWidget(main_widget)

        # Configure model
        self.model = TaskGroupsItemModel(context=self._manager.context, parent=self)
        self._model_table = TaskGroupsTableProxyModel()
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
        """Add a task group from selected shots."""
        shots = tuple(iter_selected_rows_data(self._tasks_widgets.table))
        if len(shots) <= 1:
            return

        self.model.beginResetModel()
        self._manager.add_tasks_group(shots)
        self.model.endResetModel()

    def _on_remove(self):
        """Remove selected task groups."""
        groups = tuple(iter_selected_rows_data(self.table))
        if not groups:
            return

        self.model.beginResetModel()
        self._manager.remove_task_groups(groups)
        self.model.endResetModel()

    def _on_import(self):
        raise NotImplementedError

    def _on_export(self):
        raise NotImplementedError

    def _on_data_changed(
        self, top_left, bottom_right, roles
    ):  # pylint: disable=unused-argument
        if TasksGroupWeightRole in set(roles):
            self._manager.set_dirty()


class TaskGroupsItemModel(QAbstractItemModel):
    """Model displaying task groups."""

    def __init__(self, context: Context, parent: QObject):
        super().__init__(parent)
        self._context = context

    def set_context(self, context):
        """Update the model with a new context."""
        self.beginResetModel()
        self._context = context
        self.endResetModel()

    def rowCount(  # pylint: disable=unused-argument
        self, parent: QModelIndex = Qt.EditRole
    ) -> int:
        return len(self._context.combinations) if self._context else 0

    def data(self, index: QModelIndex, role: int = Qt.EditRole) -> Any:
        row = index.row()
        group = self._context.combinations[row]

        if role == Qt.UserRole:
            return group

        if role == TasksGroupTasksRole:
            return ",".join(sorted(task.name for task in group.tasks))

        if role == TasksGroupWeightRole:
            return str(group.weight)

        return None

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.EditRole) -> bool:
        if role == TasksGroupWeightRole:
            self._context.combinations[index.row()].weight = int(value)
            self.dataChanged.emit(index, index, [role])
            return True

        raise NotImplementedError(f"setData not implemented for role {role}")


class TaskGroupsTableProxyModel(BaseTableProxyModel):
    """A proxy model that adapt a taskgroup item model to a table model."""

    _HEADERS = ("Shots", "Weight")
    _ROLES = (TasksGroupTasksRole, TasksGroupWeightRole)

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        flags = super().flags(index)
        if index.column() == 1:
            flags |= Qt.ItemIsEditable
        return flags
