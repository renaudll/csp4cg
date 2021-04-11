"""Internal types"""
import datetime
import functools
from dataclasses import dataclass, field
from typing import Dict, List, Literal, Union


@functools.total_ordering
@dataclass
class Artist:
    """A human artists that we can assign tasks to."""

    name: str
    availability: int = 100
    tags: Dict[str, int] = field(default_factory=dict)

    def __repr__(self):
        return f"Artist({self.name})"

    def __hash__(self):
        return hash(self.name)

    def __lt__(self, other):
        return other and self.name < other.name


@functools.total_ordering
@dataclass
class Task:
    """A task that can be performed by an artist."""

    name: str
    duration: Union[datetime.timedelta]
    tags: List[str] = field(default_factory=list)

    def __post_init__(self):
        assert self.duration
        # Conform duration from int to timedelta
        if isinstance(self.duration, str):
            self.duration = datetime.timedelta(
                hours=float(self.duration.replace(",", "."))
            )
        elif isinstance(self.duration, (float, int)):
            self.duration = datetime.timedelta(hours=self.duration)

    def __repr__(self):
        return f"<Task {self.name} ({self.duration} h)>"

    def __hash__(self):
        return hash(self.name)

    def __lt__(self, other):
        return other and self.name < other.name


@functools.total_ordering
@dataclass
class Assignment:
    """An artist assignment to a task."""

    artist: Artist
    task: Task

    def __hash__(self):
        return hash((self.artist, self.task))

    def __lt__(self, other):
        return other and self.task < other.task


@dataclass
class TaskGroup:
    """A sequence of tasks we'd like to have assigned to the same artist."""

    tasks: List[Task]
    weight: int = 1

    def __str__(self):
        return "assign_multiple_%s" % ("_and_".join(task.name for task in self.tasks))


@dataclass
class Settings:
    """Settings for solver heuristics."""

    weight_tags: Literal[10] = 100
    weight_equal_hours_by_artists: Literal[10] = 10
    weight_equal_tasks_count_by_artists: Literal[10] = 10


@dataclass()
class Context:
    """Hold the data to solve"""

    artists: List[Artist] = field(default_factory=list)
    tasks: List[Task] = field(default_factory=list)
    assignments: List[Assignment] = field(default_factory=list)
    settings: Settings = field(default_factory=Settings)
    combinations: List[TaskGroup] = field(default_factory=list)
    solution: List[Assignment] = field(default_factory=list)

    def assign(self, task: Task, artist: Artist):
        """Define a "hard" assignment."""
        self.unassign(task)
        self.assignments.append(Assignment(artist, task))

    def unassign(self, task: Task):
        """Remove a "hard" assignment."""
        self.assignments = [
            assignment for assignment in self.assignments if assignment.task != task
        ]

    def remove_artist(self, artist: Artist):
        """Remove an artist from the context."""
        self.artists.remove(artist)
        self.assignments = [
            assignment for assignment in self.assignments if assignment.artist != artist
        ]
        self.solution = [
            assignment for assignment in self.solution if assignment.artist != artist
        ]

    def remove_task(self, task: Task):
        """Remove a task from the context."""
        self.tasks.remove(task)
        self.assignments = [
            assignment for assignment in self.assignments if assignment.task != task
        ]
        self.solution = [
            assignment for assignment in self.solution if assignment.task != task
        ]

        new_combinations = []
        for combination in self.combinations:
            try:
                combination.tasks.remove(task)
            except ValueError:
                pass
            else:
                if not combination.tasks:  # became empty
                    continue
            new_combinations.append(combination)
        self.combinations = new_combinations
