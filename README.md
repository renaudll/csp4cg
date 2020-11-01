Custom CSP solver for common CG/VFX problems.

# Installation

This project necessitate python-3.9.
If you don't have python-3.9 available you can obtain if with pyenv.

```bash
python3.9 -m venv venv  # Create a python virtualenv
source venv/bin/activate  # Enter the virtualenv
pip install poetry  # Install poetry
poetry install  # Initialize project
poetry run pytest  # Run tests
```

# Usage

There are multiples solver and dataset included with the project.

```
# Solve shot assignment for an animation department
python -m csp4cg tasks data/tasks.yml

# Solve an environment from package request
python -m csp4cg packages data/packages.yml  # TODO: Fix

# Show a GUI to manage task assignments (WIP)
python -m csp4cg gui
```