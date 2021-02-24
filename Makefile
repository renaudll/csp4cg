# Simple Makefile to facilitate development
# https://github.com/python-poetry/poetry/issues/241#issuecomment-470200353
# TODO: Use tox instead?

pytest:
	pytest -v --cov=csp4cg --cov=tests --cov-branch

mypy:
	mypy csp4cg