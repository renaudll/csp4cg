"""Tests for data types serialization."""
import os
import yaml

from csp4cg.core import Context, Artist, Task, Assignment, TaskGroup
from csp4cg.core import _io


def test_serialization(tmp_path):
    """Validate we can serialize/deserialize a context. """
    path = tmp_path / "context.yml"
    artist1 = Artist("Artist1", tags={"0010": 1})
    artist2 = Artist("Artist1", tags={"0010": 1})
    task1 = Task("0010", 1, tags=["acting"])
    task2 = Task("0020", 1)
    context = Context(
        artists=[artist1],
        tasks=[task1, task2],
        assignments=[Assignment(artist1, task1), Assignment(artist2, task2)],
        combinations=[TaskGroup([task1], 1)],
    )

    # Test serialization
    _io.export_context_to_yml(context, path)
    actual = yaml.load(path.read_text())
    expected = {
        "artists": [
            {
                "name": "Artist1",
                "availability": 100,
                "tags": [{"name": "0010", "weight": 1}],
            }
        ],
        "tasks": [
            {"name": "0010", "duration": 1.0, "tags": ["acting"]},
            {"name": "0020", "duration": 1.0},
        ],
        "settings": {"EQUAL_TASKS_BY_USER": 100, "EQUAL_TASKS_COUNT_BY_USER": 100},
        "assignments": [
            {"artist": "Artist1", "task": "0010"},
            {"artist": "Artist1", "task": "0020"},
        ],
        "combinations": [{"tasks": ["0010"], "weight": 1}],
    }
    assert actual == expected

    # Test deserialization round-trip
    deserialized = _io.import_context_from_yml(path)
    assert context == deserialized


def test_import_artists_csv_1_columns(tmpdir):
    """Ensure we can import csv containing artists with two columns."""
    path = os.path.join(tmpdir, "artists.csv")
    with open(path, "w") as stream:
        stream.write("Artist1\nArtist2")

    actual = _io.import_artists_from_csv(path)
    assert actual == [
        Artist("Artist1"),
        Artist("Artist2"),
    ]


def test_export_artists_to_csv(tmpdir):
    """Ensure we can export a list of artists to a .csv file."""
    path = os.path.join(tmpdir, "artists.csv")
    artists = [Artist("Artist1"), Artist("Artist2")]
    _io.export_artists_to_csv(artists, path)

    with open(path) as stream:
        actual = stream.read()

    assert actual == "Artist1,100,{}\nArtist2,100,{}\n"


def test_import_tasks_csv_2_columns(tmpdir):
    """Ensure we can import csv containing tasks with two columns."""
    path = os.path.join(tmpdir, "shots.csv")
    with open(path, "w") as stream:
        stream.write("Task1,1\nTask2,2")

    actual = _io.import_tasks_from_csv(path)
    assert actual == [
        Task("Task1", 1),
        Task("Task2", 2),
    ]


def test_export_tasks_to_csv(tmpdir):
    """Ensure we can export a list of tasks to a .csv file."""
    path = os.path.join(tmpdir, "artists.csv")
    tasks = [Task("Task1", 1), Task("Task2", 2)]
    _io.export_tasks_to_csv(tasks, path)

    with open(path) as stream:
        actual = stream.read()

    assert actual == "Task1,1:00:00,[]\nTask2,2:00:00,[]\n"


def test_export_assignments_to_csv(tmpdir):
    """Ensure we can export a list of assignments to a .csv file."""
    path = os.path.join(tmpdir, "artists.csv")
    artist1 = Artist("Artist1")
    artist2 = Artist("Artist2")
    task1 = Task("0010", 1)
    task2 = Task("0020", 2)
    context = Context(
        artists=[artist1, artist2],
        tasks=[task1, task2],
        assignments=[Assignment(artist1, task1), Assignment(artist2, task2)],
    )

    _io.export_assignments_to_csv(context.assignments, path)

    with open(path) as stream:
        actual = stream.read()

    assert actual == "0010,Artist1\n0020,Artist2\n"


def test_import_assignments_to_csv(tmpdir):
    """Ensure we can import a list of assignments to a .csv file."""
    path = os.path.join(tmpdir, "artists.csv")
    with open(path, "w") as stream:
        stream.write("0010,Artist1\n0020,Artist2\n")

    artist1 = Artist("Artist1")
    artist2 = Artist("Artist2")
    task1 = Task("0010", 1)
    task2 = Task("0020", 2)
    context = Context(
        artists=[artist1, artist2],
        tasks=[task1, task2],
    )

    actual = _io.import_assignments_from_csv(context, path)
    assert actual == [Assignment(artist1, task1), Assignment(artist2, task2)]
