"""Tests for Qt models."""
import datetime
from typing import List, Any

from PySide2 import QtCore

from csp4cg.core._types import Artist, Task, Assignment, Context
from csp4cg.gui.widgets.tasks import (
    RoleTaskXCoord,
    RoleTaskYCoord,
    RoleTaskWidth,
    RoleTaskArtist,
    RoleTaskLocked,
    RoleTaskDuration,
    RoleTaskTags,
    TasksListModel,
    TasksListToTableProxyModel,
)
from csp4cg.gui.widgets.artists import ArtistsListModel, ArtistListToTableProxyModel


def test_ArtistsModel(mocker):  # pylint: disable=invalid-name
    """Test the ArtistsListModel and ArtistListToTableProxyModel"""
    artists = [
        Artist(name="artist1"),
        Artist(name="artist2"),
    ]
    context = Context(artists=artists)
    source_model = ArtistsListModel(None, context)
    source_model.set_context(context)  # for coverage
    model = ArtistListToTableProxyModel()
    model.setSourceModel(source_model)

    _assert_horizontal_header_equal(model, ["Name", "Availability", "Tags"])
    _assert_model_data_equal(model, [["artist1", "100", ""], ["artist2", "100", ""]])
    _assert_model_rows_equal(model, artists, QtCore.Qt.UserRole)

    # Spy dataChanged calls
    spy = mocker.Mock()
    model.dataChanged.connect(spy)

    # Set name (unchanged)
    index = model.index(0, 0)
    assert not model.setData(index, "artist1", QtCore.Qt.EditRole)
    assert context.artists[0].name == "artist1"
    assert model.data(index, QtCore.Qt.DisplayRole) == "artist1"
    assert not spy.called

    # Set name (changed)
    assert model.setData(index, "artist1NewName", QtCore.Qt.EditRole)
    assert context.artists[0].name == "artist1NewName"
    assert model.data(index, QtCore.Qt.DisplayRole) == "artist1NewName"
    assert spy.called

    spy.reset_mock()

    # Set availability (unchanged)
    index = model.index(0, 1)
    assert not model.setData(index, "100", QtCore.Qt.EditRole)
    assert context.artists[0].availability == 100
    assert model.data(index, QtCore.Qt.DisplayRole) == "100"
    assert not spy.called

    # Set availability (changed)
    assert model.setData(index, "99", QtCore.Qt.EditRole)
    assert context.artists[0].availability == 99
    assert model.data(index, QtCore.Qt.DisplayRole) == "99"
    assert spy.called

    spy.reset_mock()

    # Set tags (unchanged)
    index = model.index(0, 2)
    assert not model.setData(index, "", QtCore.Qt.EditRole)
    assert context.artists[0].tags == {}
    assert model.data(index, QtCore.Qt.DisplayRole) == ""
    assert not spy.called

    # Set tags (changed)
    assert model.setData(index, "foo:10", QtCore.Qt.EditRole)
    assert context.artists[0].tags == {"foo": 10}
    assert model.data(index, QtCore.Qt.DisplayRole) == "foo:10"
    assert spy.calld


def test_taskModel():  # pylint: disable=invalid-name
    """Test the TasksListModel and TasksListToTableProxyModel."""
    artists = [
        Artist(name="artist1"),
        Artist(name="artist2"),
    ]
    tasks = [
        Task(name="task1", duration=datetime.timedelta(hours=2)),
        Task(name="task2", duration=datetime.timedelta(hours=1)),
        Task(name="task3", duration=datetime.timedelta(hours=1), tags=["foo"]),
    ]
    hard_assignments = [
        Assignment(artists[0], tasks[0]),
    ]
    all_assignments = [
        Assignment(artists[0], tasks[0]),
        Assignment(artists[1], tasks[1]),
        Assignment(artists[1], tasks[2]),
    ]
    context = Context(artists=artists, tasks=tasks, assignments=hard_assignments)
    source_model = TasksListModel(None, context)
    source_model.set_context(context)  # for coverage
    model = TasksListToTableProxyModel()
    model.setSourceModel(source_model)

    # Validate values, we only have one (hard) assignment.
    _assert_model_rows_equal(model, ["task1", "task2", "task3"])
    _assert_model_rows_equal(model, ["artist1", None, None], role=RoleTaskArtist)
    _assert_model_rows_equal(model, [2.0, 1.0, 1.0], role=RoleTaskWidth)
    _assert_model_rows_equal(model, [0.0, 0.0, 0.0], role=RoleTaskXCoord)
    _assert_model_rows_equal(model, [0.0, 0.0, 0.0], role=RoleTaskYCoord)
    _assert_model_rows_equal(model, [True, False, False], role=RoleTaskLocked)
    _assert_model_rows_equal(model, tasks, role=QtCore.Qt.UserRole)

    # Set assignments
    context.solution = all_assignments
    source_model.resetInternalData()

    # Validate values now that we assigned everything.
    _assert_model_rows_equal(model, ["task1", "task2", "task3"])
    _assert_model_rows_equal(model, ["2.0", "1.0", "1.0"], role=RoleTaskDuration)
    _assert_model_rows_equal(model, ["", "", "foo"], role=RoleTaskTags)
    _assert_model_rows_equal(
        model, ["artist1", "artist2", "artist2"], role=RoleTaskArtist
    )
    _assert_model_rows_equal(model, [2.0, 1.0, 1.0], role=RoleTaskWidth)
    _assert_model_rows_equal(model, [0.0, 0.0, 1.0], role=RoleTaskXCoord)
    _assert_model_rows_equal(model, [0.0, 1.0, 1.0], role=RoleTaskYCoord)
    _assert_model_rows_equal(model, [True, False, False], role=RoleTaskLocked)

    # Set name (unchanged)
    index = model.index(0, 0)
    assert not model.setData(index, "task1")
    assert model.data(index) == "task1"
    assert context.tasks[0].name == "task1"

    # Set name (changed)
    assert model.setData(index, "task1NewName")
    assert model.data(index) == "task1NewName"
    assert context.tasks[0].name == "task1NewName"

    # Set duration (unchanged)
    index = model.index(0, 1)
    assert not model.setData(index, "2")
    assert model.data(index) == "2.0"
    assert context.tasks[0].duration == datetime.timedelta(hours=2)

    # Set duration (changed)
    assert model.setData(model.index(0, 1), "3.5")
    assert model.data(index) == "3.5"
    assert context.tasks[0].duration == datetime.timedelta(hours=3.5)

    # Set tags (unchanged)
    index = model.index(0, 4)
    assert not model.setData(index, "")
    assert model.data(index) == ""
    assert context.tasks[0].tags == []

    # Set tags (changed)
    assert model.setData(index, "foo,bar")
    assert model.data(index) == "foo,bar"
    assert context.tasks[0].tags == ["foo", "bar"]


# Helpers


def _assert_model_rows_equal(
    model: QtCore.QAbstractItemModel,
    expected: List[Any],
    role: int = QtCore.Qt.DisplayRole,
):
    num_rows = model.rowCount()
    actual = [model.data(model.index(row, 0), role) for row in range(num_rows)]
    assert actual == expected


def _assert_model_data_equal(
    model: QtCore.QAbstractItemModel,
    expected: List[List[Any]],
    role: int = QtCore.Qt.DisplayRole,
):
    num_rows = model.rowCount()
    num_cols = model.columnCount()
    actual = [
        [model.data(model.index(row, column), role) for column in range(num_cols)]
        for row in range(num_rows)
    ]
    assert actual == expected


def _assert_horizontal_header_equal(
    model: QtCore.QAbstractItemModel,
    expected: List[Any],
    role: int = QtCore.Qt.DisplayRole,
):
    num_cols = model.columnCount()
    actual = [
        model.headerData(column, QtCore.Qt.Horizontal, role)
        for column in range(num_cols)
    ]
    assert actual == expected
