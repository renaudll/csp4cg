import sys
import os

import csp4cg
from PySide2.QtWidgets import QApplication
from PySide2 import QtCore
from PySide2.QtQml import QQmlApplicationEngine
from ortools.sat.python import cp_model

from .models import AssignmentsModel, ArtistsModel, ShotListModel

_DIR = os.path.dirname(__file__)
_QML = os.path.join(_DIR, "qml", "Main.qml")
_CONFIG_PATH = os.path.join("data", "tasks.yml")
_CONFIG = csp4cg.tasks.Config.from_path(_CONFIG_PATH)


class Api(QtCore.QObject):
    def __init__(
        self,
        model: AssignmentsModel,
        model_artist: ArtistsModel,
        model_shots: ShotListModel,
    ):
        super().__init__()
        self._config = _CONFIG
        self._solver = csp4cg.tasks.Solver(self._config)
        self._printer = CustomPrinter(self._solver, self)
        self._solver._printer = self._printer
        self._model = model
        self._model_artist = model_artist
        self._model_shots = model_shots

        # TODO: Use single thread for terminate?
        self._threadpool = QtCore.QThreadPool()

    def update_assignations(self, shots_by_artists):
        self._model._data = shots_by_artists.items()
        self._model._update()

    @QtCore.Slot()
    def play(self):
        self._model.clear()
        worker = Worker(self)
        worker.signals.foundSolution.connect(self.update_assignations)
        self._threadpool.start(worker)

    @QtCore.Slot()
    def stop(self):
        self._threadpool.stop()


class WorkerSignals(QtCore.QObject):
    foundSolution = QtCore.Signal(object)


class Worker(QtCore.QRunnable):
    """Worker thread for running background tasks."""

    foundSolution = QtCore.Signal(object)

    def __init__(self, api):
        super(Worker, self).__init__()
        self._api = api
        self._config = csp4cg.tasks.Config.from_path(_CONFIG_PATH)
        self._solver = csp4cg.tasks.Solver(self._config)
        self._printer = CustomPrinter(self._solver, self)
        self._solver.printer = self._printer
        self.signals = WorkerSignals()

    def onSolutionFound(self, solution):
        self.signals.foundSolution.emit(solution)

    @QtCore.Slot()
    def run(self):
        self._solver.solve()


class CustomPrinter(cp_model.CpSolverSolutionCallback):
    """Print that compute the assignments."""

    def __init__(self, solver, api: Api):
        super().__init__()
        self._solver = solver
        self._api = api

    def on_solution_callback(self):
        """Called on each new solution."""
        solution = self._solver.get_assignments(getter=self.BooleanValue)
        self._api.onSolutionFound(solution)


def main():
    app = QApplication([])
    model_assignations = AssignmentsModel({})
    model_artist = ArtistsModel(_CONFIG.artists)
    model_shots = ShotListModel(_CONFIG.shots)
    api = Api(model_assignations, model_artist, model_shots)

    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("api", api)
    engine.rootContext().setContextProperty(
        "artistAssignationModel", model_assignations
    )
    engine.rootContext().setContextProperty("artistsModel", model_artist)
    engine.rootContext().setContextProperty("shotsModel", model_shots)

    engine.load(QtCore.QUrl(_QML))

    sys.exit(app.exec_())
