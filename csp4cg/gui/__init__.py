"""Main Window"""
import contextlib
import csv
import dataclasses
import datetime
import os
from typing import Type, List

import csp4cg
from PySide2 import QtCore, QtWidgets
from .models import (
    ArtistsModel,
    ShotListModel,
    ShotAssignmentModel,
    ShotAssignmentProxyModel,
)
from ortools.sat.python import cp_model
from .ui import main_window as _uiDef
from csp4cg.tasks import Artist, Shot, ShotAssignment

_DIR = os.path.dirname(__file__)
_CONFIG_PATH = os.path.join("data", "tasks.yml")
_CONFIG = csp4cg.tasks.Config.from_path(_CONFIG_PATH)
_QML = os.path.join(_DIR, "gantt.qml")


class CustomPrinter(cp_model.CpSolverSolutionCallback):
    """Print that compute the assignments."""

    def __init__(self, solver, callback):
        super().__init__()
        self._solver = solver
        self._callback = callback
        self._cancel = False

    def cancel(self):
        self._cancel = True

    def on_solution_callback(self):
        """Called on each new solution."""
        solution = self._solver.get_assignments(getter=self.BooleanValue)
        self._callback(solution)
        if self._cancel:
            self.StopSearch()


class WorkerSignals(QtCore.QObject):  # TODO: Why is this necessary?
    foundSolution = QtCore.Signal(object)


class WorkerThread(QtCore.QThread):
    """Worker thread for running background tasks."""

    foundSolution = QtCore.Signal(object)  # list of assignment

    def __init__(self, parent=None):
        super().__init__(parent)

        self.signals = WorkerSignals()
        self._config = _CONFIG
        self._solver = None
        self._printer = None

    def onSolutionFound(self, solution):
        self.signals.foundSolution.emit(solution)

    def run(self):
        self._solver = csp4cg.tasks.Solver(self._config)
        self._printer = CustomPrinter(self._solver, self.signals.foundSolution.emit)
        self._solver.printer = self._printer
        self._solver.solve()

    def cancel(self):
        self._printer.cancel()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._thread = WorkerThread()
        self._solution_count = 0
        self.model_assignments = ShotAssignmentModel(self, {})
        self.model_assignments_proxy = ShotAssignmentProxyModel(self)
        self.model_assignments_proxy.setSourceModel(self.model_assignments)
        self.model_artist = ArtistsModel(_CONFIG.artists, parent=self)
        self.model_artist_proxy = QtCore.QSortFilterProxyModel(self)
        self.model_artist_proxy.setSourceModel(self.model_artist)
        self.model_shots = ShotListModel(_CONFIG.shots, parent=self)
        self.model_shots_proxy = QtCore.QSortFilterProxyModel(self)
        self.model_shots_proxy.setSourceModel(self.model_shots)

        # TODO: Using QtUiTools, the Window shows up empty... why?
        # self.ui = QtUiTools.QUiLoader(self).load(
        #     os.path.join(_DIR, "ui", "main_window.ui"), parent
        # )
        self.ui = _uiDef.Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.progressBar.setHidden(True)

        self.ui.table_artists.setModel(self.model_artist_proxy)
        self.ui.table_shots.setModel(self.model_shots_proxy)
        self.ui.button_play.pressed.connect(self.play)
        self.ui.button_stop.pressed.connect(self.stop)

        for property_, model in (
            ("artists", self.model_artist),
            ("artistsSelectionModel", self.ui.table_artists.selectionModel()),
            ("shots", self.model_shots),
            ("assignments", self.model_assignments_proxy),
        ):
            self.ui.widget_gantt.rootContext().setContextProperty(property_, model)
        self.ui.widget_gantt.setSource(QtCore.QUrl(_QML))

        # TODO: Find a way to make it work directly with QML
        # self.ui.table_artists.selectionModel().selectionChanged.connect(
        #     self.on_artist_selection_changed
        # )
        self.ui.table_shots.selectionModel().selectionChanged.connect(
            self.on_shot_selection_changed
        )

        self.ui.button_add_artist.pressed.connect(self.add_artist)
        self.ui.button_remove_artists.pressed.connect(self.remove_artists)
        self.ui.button_export_artists.pressed.connect(self.export_artists)
        self.ui.button_import_artists.pressed.connect(self.import_artists)
        self.ui.button_add_shot.pressed.connect(self.add_shot)
        self.ui.button_remove_shots.pressed.connect(self.remove_shots)
        self.ui.button_export_shots.pressed.connect(self.export_shots)
        self.ui.button_import_shots.pressed.connect(self.import_shots)
        self.ui.button_export_assignments.pressed.connect(self.export_assignments)

        self.ui.lineEdit_search_artists.textChanged.connect(
            self.model_artist_proxy.setFilterWildcard
        )
        self.ui.lineEdit_search_shots.textChanged.connect(
            self.model_shots_proxy.setFilterWildcard
        )

        self._thread.started.connect(self.on_solve_start)
        self._thread.finished.connect(self.on_solve_end)
        self._thread.signals.foundSolution.connect(self.on_solution_found)

    def _iter_assignments(self, key=None):
        num_assignments = self.model_assignments.rowCount()
        for row in range(num_assignments):
            index = self.model_assignments.index(row, 0)
            assignment = self.model_assignments.data(index, QtCore.Qt.UserRole)
            if not key or key(assignment):
                yield assignment

    def on_artist_selection_changed(self, selected, deselected):
        rows = {
            index.row()
            for index in self.ui.table_artists.selectionModel().selectedRows()
        }

        artists = [
            self.model_artist.data(self.model_artist.index(row, 0), QtCore.Qt.UserRole)
            for row in rows
        ]
        assignments = tuple(
            self._iter_assignments(lambda assignment_: assignment_.artist in artists)
        )

        with _context_reset_model(self.model_assignments):
            self.model_assignments_proxy.set_hightlights(assignments)

    def _iter_selected_shots(self):
        model = self.model_shots
        rows = {
            index.row() for index in self.ui.table_shots.selectionModel().selectedRows()
        }
        for row in rows:
            index = model.index(row, 0)
            yield model.data(index, QtCore.Qt.UserRole)

    def on_shot_selection_changed(self, selected, deselected):
        shots = tuple(self._iter_selected_shots())
        assignments = tuple(
            self._iter_assignments(lambda assignment_: assignment_.shot in shots)
        )

        with _context_reset_model(self.model_assignments):
            self.model_assignments_proxy.set_hightlights(assignments)

    def add_artist(self):
        """Add an artist to the list."""
        model = self.model_artist
        id_ = max(artist.id for artist in _CONFIG.artists) + 1
        artist = Artist(id_, "New Artist", {}, 100)

        with _context_append_row(model, 1):
            _CONFIG.artists.append(artist)

    def remove_artists(self):
        """Remove selected artists from the list."""
        model = self.model_artist
        rows = {index.row() for index in self.ui.table_artists.selectedIndexes()}
        if not rows:
            return

        with _context_reset_model(model):
            for row in sorted(rows, reverse=True):
                del _CONFIG.artists[row]

    def export_artists(self):
        """Export the list of artists to a .csv file."""
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Export Artist", filter="CSV (*.csv)"
        )
        if not path:
            return
        _export(Artist, path, _CONFIG.artists)

    def import_artists(self):
        """Import the list of artists from a .csv file."""
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Import Artists", filter="CSV (*.csv)"
        )
        if not path:
            return
        _import(Artist, path, _CONFIG.artists, self.model_artist)

    def add_shot(self):
        """Add a shot to the list."""
        model = self.model_shots
        id_ = max(shot.id for shot in _CONFIG.shots) + 1
        shot = Shot(id_, "New Shot", datetime.timedelta(hours=1), [])

        with _context_append_row(model, 1):
            _CONFIG.shots.append(shot)

    def remove_shots(self):
        """Remove selected shots from the list."""
        model = self.model_shots
        rows = {index.row() for index in self.ui.table_shots.selectedIndexes()}
        if not rows:
            return

        with _context_reset_model(model):
            for row in sorted(rows, reverse=True):
                del _CONFIG.artists[row]

    def import_shots(self):
        """Import the list of shots from a .csv file."""
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Import Shots", filter="CSV (*.csv)"
        )
        if not path:
            return
        _import(Shot, path, _CONFIG.shots, self.model_shots)

    def export_shots(self):
        """Export the list of shots to a .csv file."""
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Export Shots", filter="CSV (*.csv)"
        )
        if not path:
            return
        _export(Shot, path, _CONFIG.shots)

    def export_assignments(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Export Assignations", filter="CSV (*.csv)"
        )
        if not path:
            return
        _export(ShotAssignment, self.model_assignments, path)

    def on_solve_start(self):
        """Called when the solve start."""
        self.ui.progressBar.setVisible(True)
        self.ui.horizontalSpacer_progress.changeSize(0, 0, QtWidgets.QSizePolicy.Fixed)
        self.ui.label_progress.setText(f"Number of iterations: {self._solution_count}")

    def on_solution_found(self, shots_by_artists):
        """Called when the solver found a solution."""
        self._solution_count += 1
        self.ui.label_progress.setText(f"Number of iterations: {self._solution_count}")
        self.model_assignments.set_internal_data(shots_by_artists)

    def on_solve_end(self):
        """Called when the solve end."""
        self.ui.progressBar.setVisible(False)
        self.ui.horizontalSpacer_progress.changeSize(
            1, 0, QtWidgets.QSizePolicy.MinimumExpanding
        )

    def play(self):
        """Start the solve process."""
        self._solution_count = 0
        self._thread.start()

    def stop(self):
        """Stop the solve process."""
        self._thread.cancel()  # TODO: Find how to KILL the thread


def _export(cls: Type, path: str, data: List):
    """Export data to a .csv file.

    :param cls: The data class to export.
    :param path: Path to the .csv file.
    :param data: Registry of existing data to export.
    """
    fields = dataclasses.fields(cls)
    with open(path, "w") as fp:
        writer = csv.writer(fp)
        for entry in data:
            writer.writerow([str(getattr(entry, field.name)) for field in fields])


def _import(cls: Type, path: str, data: List, model: QtCore.QAbstractItemModel):
    """Import data from a .csv file.

    :param cls: The data class to instantiate.
    :param path: Path to the .csv file.
    :param data: Registry of existing data
    :param model: A model to notify before and after the update.
    """
    fields = dataclasses.fields(cls)
    with _context_reset_model(model):
        del data[:]
        with open(path) as fp:
            reader = csv.reader(fp)
            for row in reader:
                dict_ = {field.name: row for field, row in zip(fields, row)}
                entry = cls(**dict_)
                data.append(entry)


@contextlib.contextmanager
def _context_append_row(model: QtCore.QAbstractItemModel, num_row: int):
    """Helper, context manager that add N rows at the end of a model."""
    row_count = model.rowCount()
    model.beginInsertRows(QtCore.QModelIndex(), row_count, row_count + num_row - 1)
    yield
    model.endInsertRows()


@contextlib.contextmanager
def _context_reset_model(model: QtCore.QAbstractItemModel):
    """Helper, context manager that reset the model."""
    model.beginResetModel()
    yield
    model.endResetModel()


def main():
    # QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QtWidgets.QApplication([])
    win = MainWindow()
    win.show()
    app.exec_()
