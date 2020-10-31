"""Tests for widgets"""
import pytest

from csp4cg.core import Context
from csp4cg.gui._manager import Manager
from csp4cg.gui.widgets.artists import ArtistsWidget
from csp4cg.gui.widgets.tasks import TasksWidget
from csp4cg.gui.widgets.taskgroups import TasksGroupsWidget
from csp4cg.gui.widgets.settings import SettingsWidget
from csp4cg.gui.widgets.gantt import GanttWidget
from csp4cg.gui.widgets.scores import ScoresWidget

from PySide2.QtWidgets import QWidget


@pytest.fixture(autouse=True)
def _init(qtbot):
    """Ensure qtbot is always initialized."""
    pass


@pytest.fixture
def parent():
    return QWidget()


@pytest.fixture
def manager():
    return Manager(Context())


def test_widget_artists_init(parent, manager):
    """Ensure we can initialize an ArtistsWidget."""
    ArtistsWidget(parent, manager)


def test_widget_tasks_init(parent, manager):
    """Ensure we can initialize a TasksWidget."""
    TasksWidget(parent, manager)


def test_widget_settings_init(parent, manager):
    """Ensure we can initialize a SettingsWidget."""
    SettingsWidget(parent, manager)


def test_widget_score_init(parent):
    """Ensure we can initialize a ScoresWidget."""
    ScoresWidget(parent)


def test_widget_taskgroups_init(parent, manager):
    """Ensure we can initialize a TasksWidget."""
    widget_tasks = TasksWidget(parent, manager)
    TasksGroupsWidget(parent, manager, widget_tasks)


def test_widget_gantt_init(parent, manager):
    """Ensure we can initialize a GanttWidget."""
    widget_artists = ArtistsWidget(parent, manager)
    widget_tasks = TasksWidget(parent, manager)
    # TODO: Simplify GanttWidget signature?
    GanttWidget(
        parent,
        manager,
        widget_artists.model,
        widget_tasks.model,
        widget_artists.table.selectionModel(),
        widget_tasks.table.selectionModel(),
    )
