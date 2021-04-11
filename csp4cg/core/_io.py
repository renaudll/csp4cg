"""Logic for serializing/deserializing a session."""
import csv
import dataclasses
import datetime
from typing import Dict, Type, List, Sequence, Any

import yaml

from csp4cg.core._types import (
    Artist,
    Task,
    Context,
    TaskGroup,
    Settings,
    Assignment,
)


def context_to_dict(context: Context) -> Dict:
    """Serialize a context object to a JSON compatible data type.

    :param context: A context object
    :return: A dict
    """
    data = {
        "artists": [_artist_to_dict(artist) for artist in context.artists],
        "tasks": [_task_to_dict(task) for task in context.tasks],
        "settings": _settings_to_dict(context.settings),
    }
    if context.assignments:
        data["assignments"] = [
            {"artist": assignment.artist.name, "task": assignment.task.name}
            for assignment in sorted(context.assignments)
        ]
    if context.solution:
        data["solution"] = [
            {"artist": assignment.artist.name, "task": assignment.task.name}
            for assignment in sorted(context.solution)
        ]
    if context.combinations:
        data["combinations"] = [
            {
                "tasks": [task.name for task in combination.tasks],
                "weight": combination.weight,
            }
            for combination in context.combinations
        ]
    return data


def context_from_dict(data: Dict) -> Context:
    """Deserialize a context from a JSON compatible data type.

    :param data: A dict
    :return: A context object
    """
    context = Context(
        artists=[
            _artist_from_dict(artist_data) for artist_data in data.get("artists", ())
        ],
        tasks=[_task_from_dict(task_data) for task_data in data.get("tasks", ())],
        settings=_settings_from_dict(data.get("settings", {})),
    )

    artists_by_name = {artist.name: artist for artist in context.artists}
    tasks_by_name = {task.name: task for task in context.tasks}

    # Load assignments
    for assignment_data in data.get("assignments", []):
        assignment = Assignment(
            artists_by_name[assignment_data["artist"]],
            tasks_by_name[assignment_data["task"]],
        )
        context.assignments.append(assignment)

    # Load solutions
    for assignment_data in data.get("solution", []):
        assignment = Assignment(
            artists_by_name[assignment_data["artist"]],
            tasks_by_name[assignment_data["task"]],
        )
        context.solution.append(assignment)

    # Load combinations
    for combination_data in data.get("combinations", []):
        tasks = [tasks_by_name[task_name] for task_name in combination_data["tasks"]]
        combination = TaskGroup(tasks, combination_data["weight"])
        context.combinations.append(combination)

    return context


def import_context_from_yml(path: str) -> Context:
    """Deserialize a context from a JSON/YAML file.

    :param path: Path to load from
    :return: A context object
    :raises ValueError: The the file cannot be serialized.
    """
    with open(path) as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as error:
            raise ValueError(error) from error
    if not data:
        raise ValueError("File is empty.")
    return context_from_dict(data)


def export_context_to_yml(context: Context, path: str):
    """Serialize a context to a YAML file.

    :param context: Context to serialize
    :param path: Destination path to a .yml file
    """
    data = context_to_dict(context)
    with open(path, "w") as stream:
        yaml.safe_dump(data, stream)


def _artist_to_dict(artist: Artist) -> Dict:
    """Serialize an artist object to a JSON compatible data type.

    :param artist: An artist object
    :return: A dict
    """
    data = {
        "name": artist.name,
        "availability": artist.availability,
    }
    if artist.tags:
        data["tags"] = [
            {"name": name, "weight": weight} for name, weight in artist.tags.items()
        ]
    return data


def _artist_from_dict(data: Dict) -> Artist:
    """Deserialize an artist from a JSON compatible data type.

    :param data: A dict
    :return: An artist object
    """
    return Artist(
        name=data["name"],
        availability=data.get("availability", 100),
        tags={
            tag_data["name"]: tag_data.get("weight", 1)
            for tag_data in data.get("tags", [])
        },
    )


def _task_to_dict(task: Task) -> Dict:
    """Serialize a task object to a JSON compatible data type.

    :param task: A task object
    :return: A dict
    """
    result = {
        "name": task.name,
        "duration": task.duration.total_seconds() / 60 / 60,  # in hours
    }
    if task.tags:
        result["tags"] = task.tags
    return result


def _task_from_dict(data: Dict) -> Task:
    """Deserialize a task from a JSON dict.

    :param data: A dict
    :return: A task object
    """
    return Task(
        name=data["name"],
        duration=datetime.timedelta(hours=float(data["duration"])),
        tags=data.get("tags", []),
    )


def _settings_from_dict(data: Dict) -> Settings:
    return Settings(
        weight_tags=data.get("TAGS", 1),
        weight_equal_hours_by_artists=data.get("EQUAL_TASKS_BY_USER", 0),
        weight_equal_tasks_count_by_artists=data.get("EQUAL_TASKS_COUNT_BY_USER", 0),
    )


def _settings_to_dict(settings: Settings) -> dict:
    return {
        "TAGS": settings.weight_tags,
        "EQUAL_TASKS_BY_USER": settings.weight_equal_hours_by_artists,
        "EQUAL_TASKS_COUNT_BY_USER": settings.weight_equal_tasks_count_by_artists,
    }


def export_artists_to_csv(artists: Sequence[Artist], path: str):
    """Export a list of artists to a .csv file."""
    _export_to_csv(Artist, path, artists)


def export_tasks_to_csv(tasks: Sequence[Task], path: str):
    """Export a list of tasks to a .csv file."""
    _export_to_csv(Task, path, tasks)


def export_assignments_to_csv(assignments: Sequence[Assignment], path: str):
    """Export a list of assignments to a .csv file."""
    with open(path, "w") as stream:
        writer = csv.writer(stream)
        for assignment in assignments:
            writer.writerow([assignment.task.name, assignment.artist.name])


def import_assignments_from_csv(context: Context, path: str):
    """Import a list of assignments from a .csv file."""
    assignments = []
    artist_by_name = {artist.name: artist for artist in context.artists}
    task_by_name = {task.name: task for task in context.tasks}
    with open(path) as stream:
        reader = csv.reader(stream)
        for row in reader:
            task_name, artist_name = row
            assignment = Assignment(
                artist_by_name[artist_name], task_by_name[task_name]
            )
            assignments.append(assignment)
    return assignments


def _export_to_csv(cls: Type, path: str, data: Sequence[Any]):
    """Export data to a .csv file.

    :param cls: The data class to export.
    :param path: Path to the .csv file.
    :param data: Registry of existing data to export.
    """
    fields = dataclasses.fields(cls)
    with open(path, "w") as stream:
        writer = csv.writer(stream)
        for entry in data:
            writer.writerow([str(getattr(entry, field.name)) for field in fields])


def import_artists_from_csv(path: str) -> List[Artist]:
    """Import a list of artists from a .csv file."""
    artists = []  # type: List[Artist]
    _import_from_csv(Artist, path, artists)
    return artists


def import_tasks_from_csv(path: str) -> List[Task]:
    """Import a list of tasks from a .csv file."""
    tasks = []  # type: List[Task]
    _import_from_csv(Task, path, tasks)
    return tasks


def _import_from_csv(cls: Type, path: str, data: List):
    """Import data from a .csv file.

    :param cls: The data class to instantiate.
    :param path: Path to the .csv file.
    :param data: Registry of existing data
    """
    fields = dataclasses.fields(cls)
    del data[:]
    with open(path) as stream:
        reader = csv.reader(stream)
        for row in reader:
            dict_ = {field.name: row for field, row in zip(fields, row)}
            entry = cls(**dict_)
            data.append(entry)
