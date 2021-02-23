import os

import csp4cg
from PySide2 import QtCore, QtUiTools, QtWidgets
from .models import ArtistsModel, ShotListModel, ShotAssignmentModel
from ortools.sat.python import cp_model
from . import _uiDef

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

    def on_solution_callback(self):
        """Called on each new solution."""
        solution = self._solver.get_assignments_2(getter=self.BooleanValue)
        self._callback(solution)


class WorkerSignals(QtCore.QObject):  # TODO: Why is this necessary?
    foundSolution = QtCore.Signal(object)


class Worker(QtCore.QRunnable):
    """Worker thread for running background tasks."""

    foundSolution = QtCore.Signal(object)  # TODO: Solution should be a list of assignments

    def __init__(self):
        super(Worker, self).__init__()
        self.signals = WorkerSignals()
        self._config = csp4cg.tasks.Config.from_path(_CONFIG_PATH)
        self._solver = csp4cg.tasks.Solver(self._config)
        self._printer = CustomPrinter(self._solver, self.signals.foundSolution.emit)
        self._solver.printer = self._printer

    def onSolutionFound(self, solution):
        self.signals.foundSolution.emit(solution)

    @QtCore.Slot()
    def run(self):
        self._solver.solve()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self._threadpool = QtCore.QThreadPool()
        self.model_assignments = ShotAssignmentModel(self, {})
        self.model_artist = ArtistsModel(_CONFIG.artists, parent=self)
        self.model_shots = ShotListModel(_CONFIG.shots, parent=self)

        # self.ui = QtUiTools.QUiLoader(self).load(os.path.join(_DIR, "main.ui"), parent)
        self.ui = _uiDef.Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.table_artists.setModel(self.model_artist)
        self.ui.table_shots.setModel(self.model_shots)
        self.ui.button_play.pressed.connect(self.play)
        self.ui.button_stop.pressed.connect(self.stop)

        self.ui.widget_gantt.rootContext().setContextProperty("artists", self.model_artist)
        self.ui.widget_gantt.rootContext().setContextProperty("assignments", self.model_assignments)
        self.ui.widget_gantt.setSource(QtCore.QUrl(_QML))

    def update_assignations(self, shots_by_artists):
        self.model_assignments.set_internal_data(shots_by_artists)

    def play(self):
        # self.model_assignments.clear()
        worker = Worker()
        worker.signals.foundSolution.connect(self.update_assignations)
        self._threadpool.start(worker)

    def stop(self):
        self._threadpool.stop()

def main():

    app = QtWidgets.QApplication([])
    win = MainWindow()
    win.show()
    app.exec_()
