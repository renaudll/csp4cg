"""Test csp4cg.core.Solver"""
import itertools
import operator
from datetime import timedelta
from typing import List, Sequence, Callable

import pytest

from csp4cg.core import context_from_dict
from csp4cg.core._solver import Solver
from csp4cg.core._types import Artist, Task, Context, Assignment


def test_more_artists_than_tasks():
    """Validate we handle the case where there's more artists than tasks."""
    context = context_from_dict(
        {
            "artists": [{"name": "1"}, {"name": "2"}],
            "tasks": [
                {"name": "0001", "duration": 1},
            ],
            "settings": {
                "EQUAL_TASKS_BY_USER": 1,
            },
        }
    )
    solver = Solver(context)
    result = solver.solve()
    assert result


def test_spread_workload_1():
    """Validate we can spread an equal number of tasks per artists."""
    context = context_from_dict(
        {
            "artists": [
                {"name": "1"},
                {"name": "2"},
            ],
            "tasks": [
                {"name": "0001", "duration": 1},
                {"name": "0002", "duration": 1},
                {"name": "0003", "duration": 1},
                {"name": "0004", "duration": 1},
            ],
            "settings": {
                "EQUAL_TASKS_BY_USER": 1,
            },
        }
    )

    artist1, artist2 = context.artists

    _test(
        context,
        {artist1: timedelta(hours=2), artist2: timedelta(hours=2)},
    )


def test_spread_workload_2():
    """Validate we assign equal work per artists."""
    context = context_from_dict(
        {
            "artists": [
                {"name": "1"},
                {"name": "2"},
            ],
            "tasks": [
                {"name": "0001", "duration": 2},
                {"name": "0002", "duration": 1},
                {"name": "0004", "duration": 1},
            ],
            "settings": {
                "EQUAL_TASKS_BY_USER": 1,
            },
        }
    )

    artist1, artist2 = context.artists

    _test(
        context,
        {artist1: timedelta(hours=2), artist2: timedelta(hours=2)},
    )


def test_spread_workload_complex_a():
    """Test a known hard problem."""
    context = context_from_dict(
        {
            "artists": [
                {"name": "1"},
                {"name": "2"},
                {"name": "3"},
                {"name": "4"},
                {"name": "5"},
                {"name": "6"},
                {"name": "7"},
            ],
            "tasks": [
                {"name": "0001", "duration": 10},
                {"name": "0002", "duration": 8},
                {"name": "0003", "duration": 12},
                {"name": "0004", "duration": 12},
                {"name": "0005", "duration": 4},
                {"name": "0006", "duration": 6},
                {"name": "0007", "duration": 8},
                {"name": "0008", "duration": 5},
            ],
            "settings": {
                "EQUAL_TASKS_BY_USER": 1,
            },
        }
    )

    solver = Solver(context)
    result = solver.solve()
    actual = sorted(_get_workload_by_artist(result).values())
    expected = [
        timedelta(hours=6),
        timedelta(hours=8),
        timedelta(hours=8),
        timedelta(hours=9),
        timedelta(hours=10),
        timedelta(hours=12),
        timedelta(hours=12),
    ]
    assert actual == expected


def test_spread_workload_complex_b():
    """Test another known hard problem."""
    context = context_from_dict(
        {
            "artists": [
                {"name": "1"},
                {"name": "2"},
                {"name": "3"},
                {"name": "4"},
                {"name": "5"},
                {"name": "6"},
                {"name": "7"},
            ],
            "tasks": [
                {"name": "0001", "duration": 10},
                {"name": "0002", "duration": 8},
                {"name": "0003", "duration": 12},
                {"name": "0004", "duration": 12},
                {"name": "0005", "duration": 4},
                {"name": "0006", "duration": 6},
                {"name": "0007", "duration": 8},
                {"name": "0008", "duration": 5},
                {"name": "0009", "duration": 2},
            ],
            "settings": {
                "EQUAL_TASKS_BY_USER": 1,
            },
        }
    )

    solver = Solver(context)
    result = solver.solve()
    actual = sorted(_get_workload_by_artist(result).values())
    expected = [
        timedelta(hours=8),
        timedelta(hours=8),
        timedelta(hours=8),
        timedelta(hours=9),
        timedelta(hours=10),
        timedelta(hours=12),
        timedelta(hours=12),
    ]
    assert actual == expected


def test_equal_tasks_count():
    """Ensure we prefer to assign the same number of tasks per user."""
    context = context_from_dict(
        {
            "artists": [
                {"name": "1"},
                {"name": "2"},
            ],
            "tasks": [
                {"name": "0001", "duration": 1},
                {"name": "0002", "duration": 1},
                {"name": "0003", "duration": 2},
                {"name": "0004", "duration": 4},
                {"name": "0005", "duration": 2},
                {"name": "0006", "duration": 2},
            ],
            "settings": {
                "EQUAL_TASKS_COUNT_BY_USER": 1,
            },
        }
    )

    solver = Solver(context)
    result = solver.solve()
    actual = [len(tasks) for tasks in _get_assignments_by_artist(result).values()]
    assert actual == [3, 3]


def test_combinations():
    """Ensure we try to assign a sequence to the same artist."""

    context = context_from_dict(
        {
            "artists": [{"name": "1"}, {"name": "2"}],
            "tasks": [
                {"name": "0001", "duration": 1},
                {"name": "0002", "duration": 1},
                {"name": "0003", "duration": 1},
                {"name": "0004", "duration": 1},
            ],
            "combinations": [
                {"tasks": ["0001", "0002", "0003"], "weight": 10},
            ],
            "settings": {
                "EQUAL_TASKS_COUNT_BY_USER": 1,
            },
        }
    )
    task1, task2, task3, task4 = context.tasks
    solver = Solver(context)
    assignments = solver.solve()
    actual = set(_get_tasks_by_artist(assignments).values())
    expected = {(task1, task2, task3), (task4,)}
    assert actual == expected


def test_preferences():
    """Validate we satisfy artists preferences toward certain tasks."""
    context = context_from_dict(
        {
            "artists": [
                {
                    "name": "1",
                    "tags": [{"name": "0002"}, {"name": "0003"}, {"name": "0004"}],
                },
                {"name": "2", "tags": [{"name": "0001"}]},
            ],
            "tasks": [
                {"name": "0001", "duration": 1},
                {"name": "0002", "duration": 1},
                {"name": "0003", "duration": 1},
                {"name": "0004", "duration": 1},
            ],
        }
    )
    artist1, artist2 = context.artists
    task1, task2, task3, task4 = context.tasks
    solver = Solver(context)
    assignments = solver.solve()
    actual = _get_tasks_by_artist(assignments)
    expected = {
        artist1: (task2, task3, task4),
        artist2: (task1,),
    }
    assert actual == expected


def test_preferences_2():
    """Validate we don't give more point to an artist preference
    if it match multiple tags."""
    context = context_from_dict(
        {
            "artists": [
                {
                    "name": "1",
                    "tags": [
                        {"name": "1"},
                        {"name": "0002"},
                        {"name": "0003"},
                        {"name": "0004"},
                    ],
                },
                {
                    "name": "2",
                    "tags": [
                        {"name": "0001"},
                    ],
                },
            ],
            "tasks": [
                {"name": "0001", "duration": 1},
                {"name": "0002", "duration": 1},
                {"name": "0003", "duration": 1},
                {"name": "0004", "duration": 1},
            ],
        }
    )
    artist1, artist2 = context.artists
    task1, task2, task3, task4 = context.tasks
    solver = Solver(context)
    assignments = solver.solve()
    actual = _get_tasks_by_artist(assignments)
    expected = {
        artist1: (
            task2,
            task3,
            task4,
        ),
        artist2: (task1,),
    }
    assert actual == expected


def test_solve_hard_assignments():
    """Validate we satisfy an already made assignment whatever the cost."""
    artist1 = Artist("Artist 1")
    artist2 = Artist("Artist 2")
    task1 = Task("0001", 1)
    task2 = Task("0002", 1)
    task3 = Task("0003", 2)
    context = Context(
        artists=[artist1, artist2],
        tasks=[task1, task2, task3],
        assignments=[
            Assignment(artist1, task2),
            Assignment(artist1, task3),
        ],
    )
    solver = Solver(context)
    assignments = solver.solve()
    actual = _get_tasks_by_artist(assignments)
    expected = {
        artist1: (task2, task3),
        artist2: (task1,),
    }
    assert actual == expected


def test_no_solutions():
    """Validate we raise if we don't find a solution."""
    artist1 = Artist("Artist 1")
    artist2 = Artist("Artist 2")
    task1 = Task("0001", 1)
    task2 = Task("0002", 1)
    context = Context(
        artists=[artist1, artist2],
        tasks=[task1, task2],
        assignments=[
            Assignment(artist1, task1),
            Assignment(artist2, task1),  # Can't assigne same task to another artist
        ],
    )
    solver = Solver(context)
    with pytest.raises(RuntimeError):
        solver.solve()


def _test(config, expected):
    solver = Solver(config)
    result = solver.solve()
    actual = _get_workload_by_artist(result)
    assert actual == expected


def _groupby_sort(key: Callable, iterable: Sequence):
    return {
        key: tuple(val)
        for key, val in itertools.groupby(sorted(iterable, key=key), key)
    }


def _get_assignments_by_artist(assignment: List[Assignment]):
    return _groupby_sort(operator.attrgetter("artist"), assignment)


def _get_tasks_by_artist(assignments: List[Assignment]):
    return {
        artist: tuple(assignment.task for assignment in assignments_)
        for artist, assignments_ in _get_assignments_by_artist(assignments).items()
    }


def _get_workload_by_artist(assignments: List[Assignment]):
    actual = {}
    for assignment in assignments:
        actual.setdefault(assignment.artist, timedelta())
        actual[assignment.artist] += assignment.task.duration
    return actual
