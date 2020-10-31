"""Unit tests for GUI manager."""
# pylint: disable=redefined-outer-name
import pytest

from csp4cg.core import Context, Artist, Task, TaskGroup
from csp4cg.gui import Manager


@pytest.fixture()
def context():
    """A context instance."""
    return Context(
        artists=[
            Artist("artist1"),
            Artist("artist2"),
        ],
        tasks=[
            Task("0010", 1),
            Task("0020", 2),
            Task("0030", 3),
        ],
    )


@pytest.fixture
def manager(context):
    """A manager instance."""
    return Manager(context)


def test_add_task_group(manager):
    """Ensure we can add a new task group."""
    task1, task2, task3 = manager.context.tasks
    manager.add_tasks_group([task1, task2])

    assert manager.context.combinations == [TaskGroup([task1, task2])]

    # Ensure we break any conflicting group when creating a new one.
    manager.add_tasks_group([task2, task3])
    assert manager.context.combinations == [TaskGroup([task2, task3])]


def test_remove_task_group(manager):
    """Ensure we can remove a task group."""
    task1, task2, _ = manager.context.tasks
    new_group = manager.add_tasks_group([task1, task2])
    manager.remove_task_groups([new_group])
    assert manager.context.combinations == []
