"""Unit tests for the Task data type."""
import datetime

import pytest

from csp4cg.core._types import Task

_DATA = {
    "int": (3, datetime.timedelta(hours=3)),
    "float": (3.5, datetime.timedelta(hours=3.5)),
    "string_with_dot": ("3.5", datetime.timedelta(hours=3.5)),
    "string_with_comma": ("3,5", datetime.timedelta(hours=3.5)),
}


@pytest.mark.parametrize("value,expected", _DATA.values(), ids=_DATA.keys())
def test_time_notation(value, expected):
    """Validate we can create a task using different input for the duration. """
    task = Task("test", value)
    actual = task.duration
    assert actual == expected
