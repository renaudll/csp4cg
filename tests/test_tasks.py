import datetime

from csp4cg import tasks


def _test(config, expected):
    solver = tasks.Solver(config)
    result = solver.solve()
    actual = {
        artist: sum((shot.duration for shot in shots), datetime.timedelta())
        for artist, shots in result.items()
    }
    assert actual == expected


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
    actual = sorted(
        sum((shot.duration for shot in shots), datetime.timedelta())
        for shots in result.values()
    )
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
    actual = sorted(
        sum((shot.duration for shot in shots), datetime.timedelta())
        for shots in result.values()
    )
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
    actual = [
        sorted(shot.duration for shot in shots) for artist, shots in result.items()
    ]
    actual = [len(value) for value in actual]
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
    solver = tasks.Solver(config)
    results = solver.solve()
    actual = {tuple(shot.name for shot in shots) for artist, shots in results.items()}
    expected = {("0001", "0002", "0003"), ("0004",)}
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
    actual = solver.solve()
    expected = {
        artist1: [shot2, shot3, shot4],
        artist2: [shot1],
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
    actual = solver.solve()
    expected = {
        artist1: [shot2, shot3, shot4],
        artist2: [shot1],
    }
    assert actual == expected
