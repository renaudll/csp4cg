"""Qt related utilities."""
import contextlib
from typing import Any, Iterable

from PySide2.QtCore import Qt, QObject, QModelIndex, QAbstractItemModel
from PySide2.QtWidgets import QFileDialog, QAbstractItemView


def iter_selected_rows_data(view: QAbstractItemView) -> Iterable[Any]:
    """Helper, iter each view row user role."""
    model = view.model()
    selection_model = view.selectionModel()
    rows = {index.row() for index in selection_model.selectedIndexes()}
    for row in rows:
        index = model.index(row, 0)
        yield model.data(index, Qt.UserRole)


@contextlib.contextmanager
def context_append_row(model: QAbstractItemModel, num_row: int):
    """Helper, context manager that add N rows at the end of a model."""
    row_count = model.rowCount()
    model.beginInsertRows(QModelIndex(), row_count, row_count + num_row - 1)
    yield
    model.endInsertRows()


@contextlib.contextmanager
def context_reset_model(*models: QAbstractItemModel):
    """Helper, context manager that reset the model."""
    for model in models:
        model.beginResetModel()
    yield
    for model in models:
        model.endResetModel()


def show_save_dialog(parent: QObject, title: str, filter_: str):
    """Show a file save_as dialog."""
    return QFileDialog.getSaveFileName(parent, title, filter=filter_)[0]


def show_open_dialog(parent: QObject, title: str, filter_: str):
    """Show a file open dialog."""
    return QFileDialog.getOpenFileName(parent, title, filter=filter_)[0]
