"""Main Window"""
# pylint: disable=no-member
from PySide2.QtCore import Qt
from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import QMainWindow, QShortcut, QAction, QMenu, QMenuBar

from csp4cg.core import Context
from ._manager import Manager
from .widgets.artists import ArtistsWidget
from .widgets.settings import SettingsWidget
from .widgets.scores import ScoresWidget
from .widgets.tasks import TasksWidget
from .widgets.taskgroups import TasksGroupsWidget
from .widgets.gantt import GanttWidget
from .widgets.footer import FooterBarWidget
from ._utils import show_save_dialog, show_open_dialog


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self, context=None, parent=None):
        super().__init__(parent)
        context = context or Context()

        self._manager = Manager(context)

        # Build top menu
        self.action_new = QAction("New", self)
        self.action_save = QAction("Save", self)
        self.action_open = QAction("Open", self)
        self.action_save_as = QAction("Save As", self)
        self.action_quit = QAction("Quit", self)
        self.action_show_artists = QAction("Artists", self)
        self.action_show_artists.setCheckable(True)
        self.action_show_artists.setChecked(True)
        self.action_show_tasks = QAction("Tasks", self)
        self.action_show_tasks.setCheckable(True)
        self.action_show_tasks.setChecked(True)
        self.action_show_taskgroups = QAction("Task Groups", self)
        self.action_show_taskgroups.setCheckable(True)
        self.action_show_settings = QAction("Settings", self)
        self.action_show_settings.setCheckable(True)
        self.action_show_scores = QAction("Score", self)
        self.action_show_scores.setCheckable(True)

        self.menubar = QMenuBar(self)
        self.menu_file = QMenu("File", self.menubar)
        self.menu_view = QMenu("View", self.menubar)
        self.menubar.addAction(self.menu_file.menuAction())
        self.menubar.addAction(self.menu_view.menuAction())
        self.menu_file.addAction(self.action_new)
        self.menu_file.addAction(self.action_open)
        self.menu_file.addAction(self.action_save)
        self.menu_file.addAction(self.action_save_as)
        self.menu_file.addSeparator()
        self.menu_view.addAction(self.action_show_artists)
        self.menu_view.addAction(self.action_show_tasks)
        self.menu_view.addAction(self.action_show_taskgroups)
        self.menu_view.addAction(self.action_show_settings)
        self.menu_view.addAction(self.action_show_scores)
        self.setMenuBar(self.menubar)

        # Build dock widgets
        self.widget_artists = ArtistsWidget(self, self._manager)
        self.widget_tasks = TasksWidget(self, self._manager)
        self.widget_settings = SettingsWidget(self, self._manager)
        self.widget_scores = ScoresWidget(self)
        self.widget_tasksgroups = TasksGroupsWidget(
            self, self._manager, self.widget_tasks
        )
        self.widget_gantt = GanttWidget(
            self,
            self._manager,
            self.widget_artists.model,
            self.widget_tasks.model,
            self.widget_artists.table.selectionModel(),
            self.widget_tasks.table.selectionModel(),
        )
        self.widget_footer = FooterBarWidget(self, self._manager)

        self.addDockWidget(Qt.RightDockWidgetArea, self.widget_artists)
        self.addDockWidget(Qt.RightDockWidgetArea, self.widget_tasks)
        self.addDockWidget(Qt.RightDockWidgetArea, self.widget_settings)
        self.addDockWidget(Qt.RightDockWidgetArea, self.widget_scores)
        self.addDockWidget(Qt.RightDockWidgetArea, self.widget_tasksgroups)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.widget_gantt)
        self.addToolBar(Qt.BottomToolBarArea, self.widget_footer)

        # Connect events
        self.widget_footer.actionPlay.connect(self._manager.play)
        self.widget_footer.actionStop.connect(self._manager.stop)
        self.widget_footer.actionLiveModeToggle.connect(self.on_autosolve_changed)
        self._manager.onSolutionFound.connect(self.on_solution_found)
        self._manager.onContextChanged.connect(self.on_context_changed)
        self._manager.onDirty.connect(self.on_dirty)
        self.action_new.triggered.connect(self.file_new)
        self.action_open.triggered.connect(self.file_open)
        self.action_save.triggered.connect(self.file_save)
        self.action_save_as.triggered.connect(self.file_save_as)
        self.widget_artists.artistDeleted.connect(self._on_artist_deleted)
        self.widget_tasks.taskDeleted.connect(self._on_task_deleted)

        for action, widget in (
            (self.action_show_artists, self.widget_artists),
            (self.action_show_tasks, self.widget_tasks),
            (self.action_show_taskgroups, self.widget_tasksgroups),
            (self.action_show_settings, self.widget_settings),
            (self.action_show_scores, self.widget_scores),
        ):
            widget.setVisible(action.isChecked())
            action.toggled.connect(widget.setVisible)

        self.shortcut = QShortcut(QKeySequence("Space"), self)
        self.shortcut.activated.connect(self._manager.toogle)

        self._manager.restore_autosave()
        self._update_window_title()

    def _update_window_title(self):
        title = "csp4cg"
        if self._manager.path:
            title += f": {self._manager.path}"
        if self._manager.dirty:
            title += " *"
        self.setWindowTitle(title)

    def on_dirty(self, state):
        """Called when solver related data change."""
        self.widget_footer.set_dirty(state)
        self._update_window_title()

    def on_context_changed(self, context: Context):
        """Called when the current context change."""
        self.widget_artists.model.set_context(context)
        self.widget_tasks.model.set_context(context)
        self.widget_tasksgroups.model.set_context(context)
        self.widget_settings.model.set_settings(context.settings)

    def on_autosolve_changed(self, state):
        """Called when the "Live" checkbox state change."""
        self._manager.auto_solve = bool(state)

    def file_new(self):
        """Clear the current session."""
        self._manager.set_context(Context())
        self._update_window_title()

    def file_open(self):
        """Open a saved session."""
        path = show_open_dialog(self, "Load Session", "Session (*.yml)")
        if not path:
            return

        self._manager.open(path)
        self._update_window_title()

    def file_save(self):
        """Save the session to the current file."""
        if not self._manager.path:
            self.file_save_as()
        else:
            self._manager.save()
        self._update_window_title()

    def file_save_as(self):
        """Save the session to a new file."""
        path = show_save_dialog(self, "Save Session", "Session (*.yml)")
        if not path:
            return
        self._manager.save_as(path)
        self._update_window_title()

    def _on_artist_deleted(self):
        """Called when an artist is deleted. Reset related models."""
        for model in (self.widget_tasks.model, self.widget_tasksgroups.model):
            model.beginResetModel()
            model.resetInternalData()
            model.endResetModel()

    def _on_task_deleted(self):
        """Called when a task is deleted. Reset related models."""
        for model in (self.widget_tasksgroups.model,):
            model.beginResetModel()
            model.resetInternalData()
            model.endResetModel()

    def on_solution_found(self):
        """Called when the solver found a solution."""
        self.widget_tasks.model.beginResetModel()
        self.widget_tasks.model.resetInternalData()
        self.widget_tasks.model.endResetModel()
        self.widget_scores.model.set_scores(self._manager.statistics)
