"""Handle interaction between a solver thread and a context object."""
import csv
import datetime
import itertools
import logging
import os
import tempfile
from typing import List, Tuple

from PySide2.QtCore import QObject, Signal, Slot, Qt

from csp4cg.core import (
    Artist,
    Task,
    Assignment,
    TaskGroup,
    Context,
    import_context_from_yml,
    export_context_to_yml,
)
from csp4cg.core._io import (
    export_artists_to_csv,
    export_tasks_to_csv,
    import_artists_from_csv,
    import_tasks_from_csv,
    export_assignments_to_csv,
    import_assignments_from_csv,
)
from csp4cg.gui._threading import WorkerThread, Score

_LOG = logging.getLogger(__name__)


class Manager(QObject):
    """
    Handle interaction between a solver thread and a context object.
    Made so that the actual logic is decoupled from the UI.
    """

    onDirty = Signal(bool)
    onContextChanged = Signal(object)
    onSolvingStarted = Signal()
    onSolvingEnded = Signal()
    onSolutionFound = Signal()

    def __init__(self, context: Context, auto_solve=False):
        super().__init__()
        self.context = context  # type: Context
        self.assignments = ()  # type: Tuple[Assignment, ...]
        self.statistics = ()  # type: Tuple[Score, ...]
        self.solution_count = 0
        self.current_score = 0
        self.auto_solve = auto_solve
        self.dirty = False
        self.path = ""
        self._path_autosave = os.path.join(tempfile.gettempdir(), "tmp.yml")

        self._thread = WorkerThread()
        self._thread.started.connect(self.onSolvingStarted.emit, Qt.DirectConnection)  # type: ignore
        self._thread.finished.connect(self.onSolvingEnded.emit, Qt.DirectConnection)  # type: ignore
        self._thread.foundSolution.connect(self._on_solution_found, Qt.DirectConnection)  # type: ignore
        self.set_context(context or Context())

        if self.auto_solve and self.can_play():
            self.play()

    def perform_autosave(self):
        """Save the current context to a temporary file."""
        if not self.path:
            self.save(self._path_autosave)

    def restore_autosave(self):
        """Restore an auto-saved context from a temporary file."""
        if os.path.exists(self._path_autosave):
            try:
                self.open(self._path_autosave, update_path=False)
            except ValueError as error:
                _LOG.warning("Could not open %s: %s", self._path_autosave, error)

    def set_context(self, context: Context):
        """Set the current context."""
        self.context = context
        self._thread.set_context(context)
        self.assignments = self._get_default_assignments()
        self.onContextChanged.emit(context)  # type: ignore

    def _get_artist_assigned_to_task(self, task: Task):
        return next(
            (
                assignment.artist
                for assignment in self.context.solution
                if assignment.task == task
            )
        )

    @Slot(int, int)  # type: ignore
    def onTaskDroppedOnArtist(  # pylint: disable=invalid-name
        self, task_index, artist_index
    ):
        """Called when a task is dragged on an artist row."""
        task = self.context.tasks[task_index]
        old_artist = self._get_artist_assigned_to_task(task)
        new_artist = self.context.artists[artist_index]
        if old_artist == new_artist:
            return

        self.context.assign(task=task, artist=new_artist)

        # Compute new assignments
        assignments = [
            assignment
            for assignment in self.context.solution
            if assignment.task != task
        ]
        assignments.append(Assignment(new_artist, task))
        self.assignments = assignments
        self.onSolutionFound.emit()

        self.set_dirty()

    def _get_default_assignments(self):
        if not self.context.artists:
            return []
        assignments = []
        default_artist = self.context.artists[0]
        for task in self.context.tasks:
            artist = next(
                (
                    combination.artist
                    for combination in self.context.assignments
                    if combination.task == task
                ),
                default_artist,
            )
            assignments.append(Assignment(artist, task))
        return assignments

    def _on_solution_found(self, data):
        """Called when the solver found a solution."""
        self.solution_count += 1
        self.context.solution, self.statistics = data
        self.current_score = sum(score for _, score, _ in self.statistics)
        self.perform_autosave()
        self.onSolutionFound.emit()

    def set_dirty(self, state: bool = True):
        """Notify the manager that the data changed and we need to rerun the solver."""
        self.dirty = state
        self.onDirty.emit(state)  # type: ignore

        if not state:
            return

        self.perform_autosave()
        if self.auto_solve and self.can_play():
            self.stop()
            self.play()

    def can_play(self):
        """Determine if we have data to solve."""
        return self.context.artists and self.context.tasks

    def play(self, join=False):
        """Start the solve process."""
        self.set_dirty(False)
        self.solution_count = 0
        self._thread.start()
        if join:
            self._thread.wait()

    def stop(self):
        """Stop the solve process."""
        if self._thread.isRunning():
            self._thread.cancel()
            self._thread.wait()

    def toogle(self):
        """Play or stop the solve processing depending on it's current state."""
        if self._thread.isRunning():
            self.stop()
        else:
            self.play()

    def add_artist(self):
        """Add a new artist to the current context."""
        names = {artist.name for artist in self.context.artists}
        name = _get_unique_name(names, "Artist")
        artist = Artist(name=name, availability=100, tags={})
        self.context.artists.append(artist)
        self.set_dirty()

    def remove_artists(self, artists):
        """Remove artists from the current context.

        :param artists: The artist to remove
        """
        for artist in artists:
            self.context.remove_artist(artist)
        self.set_dirty()

    def add_task(self):
        """Add a new task to the current context."""
        names = {task.name for task in self.context.tasks}
        name = _get_unique_name(names, "Task")
        task = Task(name, datetime.timedelta(hours=1), [])
        self.context.tasks.append(task)
        self.set_dirty()

    def remove_tasks(self, tasks: List[Task]):
        """Remove tasks from the current context.

        :param tasks: The tasks to remove
        """
        for task in tasks:
            self.context.remove_task(task)
        self.set_dirty()

    def add_tasks_group(self, tasks: List[Task]):
        """Give bonus points if a group of tasks are given to the same artist."""
        new_group = TaskGroup(tasks, 1)

        # Remove any groups that already use these tasks
        groups_to_remove = [
            group
            for group in self.context.combinations
            if any(task in group.tasks for task in tasks)
        ]
        for group_to_remove in groups_to_remove:
            self.context.combinations.remove(group_to_remove)

        self.context.combinations.append(new_group)
        self.set_dirty()
        return new_group

    def remove_task_groups(self, task_groups: List[TaskGroup]):
        """Remove bonus points if a group of tasks are given to the same artist."""
        for task_group in task_groups:
            self.context.combinations.remove(task_group)
        self.set_dirty()

    def export_artists(self, path: str):
        """Export the list of artists to a .csv file."""
        export_artists_to_csv(self.context.artists, path)

    def import_artists(self, path: str):
        """Import the list of artists from a .csv file."""
        self.context.artists = import_artists_from_csv(path)

    def import_tasks(self, path: str):
        """Import the list of tasks from a .csv file."""
        self.context.tasks = import_tasks_from_csv(path)

    def export_tasks(self, path: str):
        """Export the list of tasks to a .csv file."""
        export_tasks_to_csv(self.context.tasks, path)

    def import_assignments(self, path: str):
        """Import a list of assignments from a .csv file."""
        self.context.solution = import_assignments_from_csv(self.context, path)

    def export_assignments(self, path: str):
        """Export the current assignments to a .csv file."""
        export_assignments_to_csv(self.context.solution, path)

    def save(self, path: str = None):
        """Expose the current session to a .yml file."""
        export_context_to_yml(self.context, path or self.path)

    def save_as(self, path: str):
        """Export the current session to a .yml file."""
        self.path = path
        self.save()

    def open(self, path: str, update_path: bool = True):
        """Open a saved session .yml file."""
        context = import_context_from_yml(path)
        self.set_context(context)
        if update_path:
            self.path = path
        self.set_dirty(False)


def _get_unique_name(known, prefix):
    suffix = itertools.count(start=1)
    while True:
        name = f"{prefix}{next(suffix)}"
        if name not in known:
            return name
