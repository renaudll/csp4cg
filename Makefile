# Simple Makefile to facilitate development
# https://github.com/python-poetry/poetry/issues/241#issuecomment-470200353
# TODO: Use tox instead?

pytest:
	pytest -v --cov=csp4cg --cov=tests --cov-branch

mypy:
	mypy csp4cg

pylint:
	pylint csp4cg tests --output-format=colorized --rcfile=./pyproject.toml

flake8:
	flake8 --exclude=ui csp4cg tests

black:
	black --check csp4cg csp4cg/gui tests --exclude="/ui/"

black-reformat:
	black csp4cg csp4cg/gui tests --exclude="/ui/"
