"""Widget that display current solver settings."""
# pylint: disable=no-member
import os

from PySide2.QtCore import QObject, QUrl
from PySide2.QtWidgets import QDockWidget
from PySide2.QtQuickWidgets import QQuickWidget

from .._manager import Manager

_QML = os.path.join(os.path.dirname(__file__), "qml", "GanttView.qml")


class GanttWidget(QDockWidget):
    """Widget that display a gantt view of task assignments."""

    def __init__(
        self,
        parent: QObject,
        manager: Manager,
        artists_model,
        tasks_model,
        artist_selection_model,
        tasks_selection_model,
    ):
        super().__init__(parent)

        self.setWindowTitle("Assignments")

        self._manager = manager

        # Build widgets
        self.widget_gantt = QQuickWidget(self)
        self.widget_gantt.setResizeMode(QQuickWidget.SizeRootObjectToView)
        root_context = self.widget_gantt.rootContext()
        root_context.setContextProperty("manager", self._manager)
        root_context.setContextProperty("artists", artists_model)
        root_context.setContextProperty("tasks", tasks_model)
        root_context.setContextProperty("artistsSelectionModel", artist_selection_model)
        root_context.setContextProperty("tasksSelectionModel", tasks_selection_model)
        self.widget_gantt.setSource(QUrl.fromLocalFile(_QML))

        # Build layout
        self.setWidget(self.widget_gantt)
