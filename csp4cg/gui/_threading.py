"""Worker thread for the solve process."""
import itertools
import multiprocessing
import time
import queue
from typing import Callable, Iterable, Tuple

from PySide2.QtCore import Signal, QThread
from ortools.sat.python import cp_model

from csp4cg.core import Solver, Context, Assignment

Score = Tuple[str, int]
Solution = Tuple[Tuple[Assignment, ...], Tuple[Score, ...]]
CallbackOnSolution = Callable[[Solution], None]


def _solve(context: Context, queue_: multiprocessing.Queue):
    # This function is voluntarily not a method of QThread as QThread
    # is not "pickable" on Windows.
    solver = Solver(context)
    printer = CustomPrinter(solver, queue_.put)
    solver.printer = printer
    solver.solve()


class WorkerThread(QThread):
    """Worker thread for running background tasks."""

    foundSolution = Signal(object)  # list of assignment
    foundBestSolution = Signal(object)

    def __init__(self, context=None, parent=None):
        super().__init__(parent)

        self._context = context
        self._process = None
        self._queue = None
        self._cancel = False

    def set_context(self, context: Context):
        """Set the current context"""
        self._context = context

    def _on_solution_found(self, solution: Solution):
        """Called when a new solution is found."""
        self.foundSolution.emit(solution)  # type: ignore

    def run(self):
        """Start the solve process."""
        self._cancel = False
        # We use multiprocessing to be able to kill the process.
        # https://stackoverflow.com/a/7752174
        # In ortools, there's no way to interrupt the solving immediately.
        # There is the CpSolverSolutionCallback.StopSearch but it's not immediate.
        # https://developers.google.com/optimization/cp/cp_tasks#solution-limit
        self._queue = multiprocessing.Queue()
        self._process = multiprocessing.Process(
            target=_solve,
            args=(
                self._context,
                self._queue,
            ),
        )
        self._process.start()

        while (
            self._process.is_alive() and not self._cancel
        ) or not self._queue.empty():
            try:
                solution = self._queue.get_nowait()
            except queue.Empty:
                pass
            else:
                self._on_solution_found(solution)
            time.sleep(0.1)

    def cancel(self):
        """Cancel the current solve process."""
        if self._process:
            self._process.terminate()
        self._cancel = True


class CustomPrinter(cp_model.CpSolverSolutionCallback):
    """Print that compute the assignments."""

    def __init__(self, solver: Solver, callback: CallbackOnSolution):
        super().__init__()
        self._solver = solver
        self._callback = callback

    def _iter_assignments(self) -> Iterable[Assignment]:
        """Get the assignments for the current solution."""
        for artist, task in itertools.product(self._solver.artists, self._solver.tasks):
            variable = self._solver.get_variable_assignment(task, artist)
            if self.BooleanValue(variable):
                yield Assignment(artist=artist, task=task)

    def on_solution_callback(self):
        """Called on each new solution."""
        solution = tuple(self._iter_assignments())
        scores = tuple(
            (variable.Name(), self.Value(variable) * score, score)
            for variable, score in self._solver.iter_variables_and_cost()
        )
        self._callback((solution, scores))
