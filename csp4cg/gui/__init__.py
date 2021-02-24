import os
import datetime
import contextlib

import csp4cg
from PySide2 import QtCore, QtWidgets
from .models import ArtistsModel, ShotListModel, ShotAssignmentModel
from ortools.sat.python import cp_model
from .ui import main_window as _uiDef
from csp4cg.tasks import Artist, Shot

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
        super(WorkerThread, self).__init__(parent)

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
        super(MainWindow, self).__init__(parent)
        self._thread = WorkerThread()
        self._solution_count = 0
        self.model_assignments = ShotAssignmentModel(self, {})
        self.model_artist = ArtistsModel(_CONFIG.artists, parent=self)
        self.model_shots = ShotListModel(_CONFIG.shots, parent=self)

        # self.ui = QtUiTools.QUiLoader(self).load(os.path.join(_DIR, "main.ui"), parent)
        self.ui = _uiDef.Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.progressBar.setHidden(True)

        self.ui.table_artists.setModel(self.model_artist)
        self.ui.table_shots.setModel(self.model_shots)
        self.ui.button_play.pressed.connect(self.play)
        self.ui.button_stop.pressed.connect(self.stop)

        self.ui.widget_gantt.rootContext().setContextProperty(
            "artists", self.model_artist
        )
        self.ui.widget_gantt.rootContext().setContextProperty(
            "assignments", self.model_assignments
        )
        self.ui.widget_gantt.setSource(QtCore.QUrl(_QML))

        self.ui.button_add_artist.pressed.connect(self.add_artist)
        self.ui.button_remove_artists.pressed.connect(self.remove_artists)
        self.ui.button_add_shot.pressed.connect(self.add_shot)
        self.ui.button_remove_shots.pressed.connect(self.remove_shots)

        self._thread.started.connect(self.on_solve_start)
        self._thread.finished.connect(self.on_solve_end)
        self._thread.signals.foundSolution.connect(self.on_solution_found)

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
        self.ui.horizontalSpacer_progress.changeSize(1, 0, QtWidgets.QSizePolicy.MinimumExpanding)

    def play(self):
        """Start the solve process."""
        self._solution_count = 0
        self._thread.start()

    def stop(self):
        """Stop the solve process."""
        self._thread.cancel()  # TODO: Find how to KILL the thread


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
    app = QtWidgets.QApplication([])
    win = MainWindow()
    win.show()
    app.exec_()
