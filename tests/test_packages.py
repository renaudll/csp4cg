from csp4cg import packages
import pytest


@pytest.fixture
def config():
    return packages.Config.from_data(
        {
            "core_context": [
                {"version": "1.1", "requires": "python"},
                {"version": "1.2", "requires": "python"},
                {"version": "2.0", "requires": "python"},
            ],
            "core_publish": [
                {"version": "1.1", "requires": "core_context<2"},
            ],
            "python": [
                {"version": "2.7"},
                {"version": "3.7"},
                {"version": "3.8"},
            ],
        }
    )


@pytest.fixture
def registry(config):
    return packages.PackageRegistry(config.packages)


@pytest.mark.parametrize(
    "request_,expected",
    [
        [
            "core_publish",
            {
                "python-3.8",
                "core_context-1.2",
                "core_publish-1.1",
            },
        ],
        [
            "core_context",
            {
                "core_context-2.0",
                "python-3.8",
            },
        ],
        ["python", {"python-3.8"}],
    ],
)
def test_something(registry, request_, expected, config):
    solver = packages.Solver(config, packages=registry, request=request_)
    actual = {str(version) for version in solver.solve()}
    assert actual == expected
