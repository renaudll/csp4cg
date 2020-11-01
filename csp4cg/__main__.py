"""Main entry point. Invoke with "python -m csp4cg". """
import argparse

import csp4cg


def _solver_tasks(args):
    config = csp4cg.tasks.Config.from_path(args.data)
    solver = csp4cg.tasks.Solver(config)
    solver.solve()


def _solver_packages(args):
    config = csp4cg.packages.Config.from_path(args.data)
    solver = csp4cg.packages.Solver(config, args.request)
    solver.solve()


def _gui(args):
    from . import gui

    gui.main()


parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="solver")

parser_tasks = subparsers.add_parser("tasks")
parser_tasks.set_defaults(func=_solver_tasks)
parser_tasks.add_argument("data")

parser_pkgs = subparsers.add_parser("packages")
parser_pkgs.set_defaults(func=_solver_packages)
parser_pkgs.add_argument("data")
parser_pkgs.add_argument("request")

parser_gui = subparsers.add_parser("gui")
parser_gui.set_defaults(func=_gui)


def main(args):
    """Entry point"""
    # TODO: Use a real plugin system
    args.func(args)


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
