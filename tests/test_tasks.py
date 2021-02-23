import datetime
import itertools
import operator

from typing import List, Sequence, Callable

from csp4cg import tasks


def _test(config, expected):
    solver = tasks.Solver(config)
    result = solver.solve()
    actual = _get_workload_by_artist(result)
    assert actual == expected


def _groupby_sort(key: Callable, iterable: Sequence):
    return {
        key: tuple(val)
        for key, val in itertools.groupby(sorted(iterable, key=key), key)
    }


def _get_assignments_by_artist(assignment: List[tasks.ShotAssignment]):
    return _groupby_sort(operator.attrgetter("artist"), assignment)


def _get_shots_by_artist(assignments: List[tasks.ShotAssignment]):
    return {
        artist: tuple(assignment.shot for assignment in assignments_)
        for artist, assignments_ in _get_assignments_by_artist(assignments).items()
    }


def _get_workload_by_artist(assignments : List[tasks.ShotAssignment]):
    actual = {}
    for assignment in assignments:
        actual.setdefault(assignment.artist, datetime.timedelta())
        actual[assignment.artist] += assignment.shot.duration
    return actual


def test_spread_workload_1():
    config = tasks.Config.from_data(
        {
            "artists": [
                {"name": "1"},
                {"name": "2"},
            ],
            "shots": [
                {"name": "0001", "duration": 1},
                {"name": "0002", "duration": 1},
                {"name": "0003", "duration": 1},
                {"name": "0004", "duration": 1},
            ],
            "settings": {
                "EQUAL_HOURS_BY_USER": 1,
            },
        }
    )

    artist1, artist2 = config.artists

    _test(
        config,
        {artist1: datetime.timedelta(hours=2), artist2: datetime.timedelta(hours=2)},
    )


def test_spread_workload_2():
    """Validate we assign equal work per artists."""
    config = tasks.Config.from_data(
        {
            "artists": [
                {"name": "1"},
                {"name": "2"},
            ],
            "shots": [
                {"name": "0001", "duration": 2},
                {"name": "0002", "duration": 1},
                {"name": "0004", "duration": 1},
            ],
            "settings": {
                "EQUAL_HOURS_BY_USER": 1,
            },
        }
    )

    artist1, artist2 = config.artists

    _test(
        config,
        {artist1: datetime.timedelta(hours=2), artist2: datetime.timedelta(hours=2)},
    )


def test_spread_workload_complex_a():
    config = tasks.Config.from_data(
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
            "shots": [
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
                "EQUAL_HOURS_BY_USER": 1,
            },
        }
    )

    solver = tasks.Solver(config)
    result = solver.solve()
    actual = sorted(_get_workload_by_artist(result).values())
    expected = [
        datetime.timedelta(hours=6),
        datetime.timedelta(hours=8),
        datetime.timedelta(hours=8),
        datetime.timedelta(hours=9),
        datetime.timedelta(hours=10),
        datetime.timedelta(hours=12),
        datetime.timedelta(hours=12),
    ]
    assert actual == expected


def test_spread_workload_complex_b():
    config = tasks.Config.from_data(
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
            "shots": [
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
                "EQUAL_HOURS_BY_USER": 1,
            },
        }
    )

    solver = tasks.Solver(config)
    result = solver.solve()
    actual = sorted(_get_workload_by_artist(result).values())
    expected = [
        datetime.timedelta(hours=8),
        datetime.timedelta(hours=8),
        datetime.timedelta(hours=8),
        datetime.timedelta(hours=9),
        datetime.timedelta(hours=10),
        datetime.timedelta(hours=12),
        datetime.timedelta(hours=12),
    ]
    assert actual == expected


def test_5():
    """Ensure we prefer to assign the same number of tasks per user."""
    config = tasks.Config.from_data(
        {
            "artists": [
                {"name": "1"},
                {"name": "2"},
            ],
            "shots": [
                {"name": "0003", "duration": 1},
                {"name": "0004", "duration": 1},
                {"name": "0005", "duration": 2},
                {"name": "0005", "duration": 4},
                {"name": "0005", "duration": 2},
                {"name": "0006", "duration": 2},
            ],
            "settings": {
                "EQUAL_SHOT_COUNT_BY_USER": 1,
            },
        }
    )

    solver = tasks.Solver(config)
    result = solver.solve()
    actual = [len(shots) for shots in _get_assignments_by_artist(result).values()]
    assert actual == [3, 3]


def test_preferred_combinations():
    """Ensure we try to assign a sequence to the same artist."""

    config = tasks.Config.from_data(
        {
            "artists": [{"name": "1"}, {"name": "2"}],
            "shots": [
                {"name": "0001", "duration": 1},
                {"name": "0002", "duration": 1},
                {"name": "0003", "duration": 1},
                {"name": "0004", "duration": 1},
            ],
            "preferred_combinations": [
                {"shots": ["0001", "0002", "0003"], "weight": 10},
            ],
        }
    )
    shot1, shot2, shot3, shot4 = config.shots
    solver = tasks.Solver(config)
    assignments = solver.solve()
    actual = set(_get_shots_by_artist(assignments).values())
    expected = {(shot1, shot2, shot3), (shot4,)}
    assert actual == expected


def test_preferences():
    """Validate we satisfy artists preferences toward certain shots."""
    config = tasks.Config.from_data(
        {
            "artists": [{"name": "1"}, {"name": "2"}],
            "shots": [
                {"name": "0001", "duration": 1},
                {"name": "0002", "duration": 1},
                {"name": "0003", "duration": 1},
                {"name": "0004", "duration": 1},
            ],
            "preferences": [
                {"artist": "2", "shot": "0001"},
                {"artist": "1", "shot": "0002"},
                {"artist": "1", "shot": "0003"},
                {"artist": "1", "shot": "0004"},
            ],
        }
    )
    artist1, artist2 = config.artists
    shot1, shot2, shot3, shot4 = config.shots
    solver = tasks.Solver(config)
    assignments = solver.solve()
    actual = _get_shots_by_artist(assignments)
    expected = {
        artist1: (shot2, shot3, shot4),
        artist2: (shot1,),
    }
    assert actual == expected


def test_preferences_2():
    """Validate we don't give more point to an artist preference if it match multiple tags."""
    config = tasks.Config.from_data(
        {
            "artists": [
                {"name": "1", "tags": [{"name": "1", "weight": 1}]},
                {"name": "2"},
            ],
            "shots": [
                {"name": "0001", "duration": 1},
                {"name": "0002", "duration": 1},
                {"name": "0003", "duration": 1},
                {"name": "0004", "duration": 1},
            ],
            "preferences": [
                {"artist": "2", "shot": "0001"},
                {"artist": "1", "shot": "0002"},
                {"artist": "1", "shot": "0003"},
                {"artist": "1", "shot": "0004"},
            ],
        }
    )
    artist1, artist2 = config.artists
    shot1, shot2, shot3, shot4 = config.shots
    solver = tasks.Solver(config)
    assignments = solver.solve()
    actual = _get_shots_by_artist(assignments)
    expected = {
        artist1: (
            shot2,
            shot3,
            shot4,
        ),
        artist2: (shot1,),
    }
    assert actual == expected
