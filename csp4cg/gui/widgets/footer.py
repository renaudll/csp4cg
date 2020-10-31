"""Bottom tool bar"""
# pylint: disable=no-member
from PySide2.QtCore import Signal, QObject
from PySide2.QtWidgets import (
    QPushButton,
    QLabel,
    QProgressBar,
    QSizePolicy,
    QCheckBox,
    QWidget,
    QToolBar,
)

from .._manager import Manager
from .._utils import show_save_dialog

_CSS_CLEAN = ""
_CSS_DIRTY = "background-color: #CC0; color: black"


class FooterBarWidget(QToolBar):
    """Bottom tool bar"""

    actionPlay = Signal()
    actionStop = Signal()
    actionLiveModeToggle = Signal(bool)

    def __init__(self, parent: QObject, manager: Manager):
        super().__init__(parent)

        self._manager = manager

        # Used to control the progress bar and spacer visibility
        # https://stackoverflow.com/a/1695779
        self._action_progress = None
        self._action_spacer = None

        # Build widgets
        self.button_play = QPushButton("Play", self)
        self.button_stop = QPushButton("Stop", self)
        self.button_export = QPushButton("Export", self)
        self.label_progress = QLabel(self)
        self.checkbox_live = QCheckBox("Live", self)
        self.checkbox_live.setChecked(self._manager.auto_solve)
        self.progressbar = QProgressBar(self)
        self.progressbar.setMaximum(0)
        self.progressbar.setValue(-1)
        self.progressbar.setHidden(True)
        self.spacer = QWidget()
        self.spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Build layout
        self.addWidget(self.button_play)
        self.addWidget(self.button_stop)
        self.addWidget(self.label_progress)
        self._action_progress = self.addWidget(self.progressbar)
        self._action_spacer = self.addWidget(self.spacer)
        self.addWidget(self.button_export)
        self.addWidget(self.checkbox_live)

        # # Connect events
        self.button_play.pressed.connect(self.actionPlay.emit)  # type: ignore
        self.button_stop.pressed.connect(self.actionStop.emit)  # type: ignore
        self.button_export.pressed.connect(self.on_export_pressed)  # type: ignore
        self.checkbox_live.stateChanged.connect(self.actionLiveModeToggle.emit)  # type: ignore
        self._manager.onSolvingStarted.connect(self.on_solve_start)  # type: ignore
        self._manager.onSolvingEnded.connect(self.on_solve_end)  # type: ignore
        self._manager.onSolutionFound.connect(self.on_solution_found)  # type: ignore

    def set_dirty(self, state: bool):
        """Called when a change that invalidate the current solution was made."""
        self.button_play.setStyleSheet(_CSS_DIRTY if state else _CSS_CLEAN)

    def on_export_pressed(self):
        """Export the current assignments to a .csv file."""
        path = show_save_dialog(self, "Export Assignations", "CSV (*.csv)")
        if not path:
            return
        self._manager.export_assignments(path)

    def on_solve_start(self):
        """Called when the solve start."""
        self._action_progress.setVisible(True)
        self._action_spacer.setVisible(False)

        self.button_play.setEnabled(False)
        self.button_stop.setEnabled(True)
        self.on_solution_found()

    def on_solution_found(self):
        """Called when the solver found a solution."""
        self.label_progress.setText(
            f"Number of iterations: {self._manager.solution_count}. "
            f"Total score: {self._manager.current_score}"
        )

    def on_solve_end(self):
        """Called when the solve end."""
        self._action_progress.setVisible(False)
        self._action_spacer.setVisible(True)

        self.button_play.setEnabled(True)
        self.button_stop.setEnabled(False)
