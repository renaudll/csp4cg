import itertools
import logging
from abc import ABCMeta
from dataclasses import dataclass

from tabulate import tabulate
from ortools.sat.python import cp_model
import yaml

logging.basicConfig()

_LOG = logging.getLogger("main")


@dataclass()
class Config(metaclass=ABCMeta):  # TODO: Convert to abstract
    """Hold the solver data."""

    @classmethod
    def from_path(cls, path):
        with open(path) as stream:
            config = yaml.load(stream, Loader=yaml.SafeLoader)
        return cls.from_data(config)

    @classmethod
    def from_data(cls, config: dict):
        """Class constructor from JSON-compatible dict."""
        raise NotImplementedError


class Solver:
    """Manager class to facilitate constraint creation."""

    def __init__(self, model=None, printer=None):
        self.model = model or cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        self.solver.parameters.num_search_workers = 8  # TODO: necessary?
        self._known_names = set()
        self.variables = {}
        self._vars_bool = []
        self._vars_bool_cost = []
        self._vars_int = []
        self._vars_int_cost = []
        self._vars_weights = []
        self.printer = printer or cp_model.ObjectiveSolutionPrinter()

    def create_variable_bool(self, key, name=None):
        """Create a variable.

        :param object key: An hashable key to fetch the variable if needed.
        :param str name: The variable name
        :return: A variable
        :rtype: ortools.sat.python.cp_model.IntVar
        """
        name = name or "_".join(key)

        assert key not in self.variables
        assert name not in self._known_names

        var = self.model.NewBoolVar(name)
        self.variables[key] = var
        return var

    def get_variable(self, key):
        """Get a registered variable

        :param object key: A hashable key
        :return: A variable
        :rtype: ortools.sat.python.cp_model.IntVar
        :raises KeyError: If no variable exist for the provided key.
        """
        return self.variables[key]

    def add_hard_constraint(self, expr):
        """Add a "hard" constraint. T
        he solve will fail if even once hard constraint fail to be satisfied.

        :param expr: The constraint expression
        :type expr: ortools.sat.python.cp_model.BoundedLinearExpression
        :return: A constraint
        :rtype: ortools.sat.python.cp_model.Constraint
        """
        return self.model.Add(expr)

    def set_variable_bool_score(self, variable, score):
        """Set the cost for a variable.

        :param variable: A variable
        :type variable: ortools.sat.python.cp_model.Constraint
        :param score: The cost if the variant is ON
        """
        self._vars_bool.append(variable)
        self._vars_bool_cost.append(score)

    def create_soft_constraint_bool(self, name, score):  # TODO: dead code?
        """Add a "soft" boolean variable with a score.
        The solver will try to maximize it's score.

        :param str name: The variable name
        :param int score: The variable score
        :return: A constraint
        :rtype: ortools.sat.python.cp_model.Constraint
        """
        assert name not in self._known_names
        var = self.model.NewBoolVar(name)
        self.set_variable_bool_score(var, score)
        return var

    def create_soft_constraint_int(
        self, name: str, minimum: int, maximum: int, score: int
    ):
        """Add a "soft" integer variable with a score.
        The solver will try to maximum it's score.

        :param name: The variable name
        :param minimum: The variable domain minimum value
        :param maximum: The variable domain maximum value
        :param score: The variable score
        :return: A constraint
        :rtype: ortools.sat.python.cp_model.Constraint
        """
        assert name not in self._known_names
        var = self.model.NewIntVar(minimum, maximum, name)
        self._vars_int.append(var)
        self._vars_int_cost.append(score)
        return var

    def create_weighted_variable_int(self, name: str, minimum: int, maximum: int):
        """Create a variable which value is added to the score.

        :param name: The variable name
        :param minimum: The variable score domain minimum value
        :param maximum: The variable score domain maximum value
        :return: The created variable
        :rtype: ortools.sat.python.cp_model.IntVar
        """
        assert name not in self._known_names
        var = self.model.NewIntVar(minimum, maximum, name)
        self._vars_weights.append(var)
        return var

    def solve(self):
        """Solve using provided constraints."""
        self.model.Maximize(
            sum(
                itertools.chain(
                    (
                        var * cost
                        for var, cost in zip(self._vars_bool, self._vars_bool_cost)
                    ),
                    (
                        var * cost
                        for var, cost in zip(self._vars_int, self._vars_int_cost)
                    ),
                    self._vars_weights,
                )
            )
        )
        status = self.solver.SolveWithSolutionCallback(self.model, self.printer)
        if status != cp_model.OPTIMAL and status != cp_model.FEASIBLE:
            raise Exception("No solution found! Status is %s" % status)
        return status

    def _iter_variable_and_values(self):
        for variable, score in zip(self._vars_bool, self._vars_bool_cost):
            yield variable.Name(), int(self.solver.BooleanValue(variable)), score
        for variable, score in zip(self._vars_int, self._vars_int_cost):
            yield variable.Name(), self.solver.Value(variable), score

    def print_score_tracking(self):
        """Print an explanation of the decisions taken."""
        print("Opportunities taken:")
        print()

        def _fn_sort(data):
            name, value, score = data
            return (name, -value * score)

        data = tuple(
            (name, value, score)
            for name, value, score in self._iter_variable_and_values()
            if value > 0
        )
        data = sorted(data, key=_fn_sort)
        print(tabulate(data, headers=["Constraint", "Value", "Multiplier"]))

        print()
        print("Opportunities missed:")
        print()
        data = tuple(
            (name, value, score)
            for name, value, score in self._iter_variable_and_values()
            if value <= 0
        )
        data = sorted(data, key=_fn_sort)
        print(tabulate(data, headers=["Constraint", "Value", "Multiplier"]))

    def get_variable_result(self, key):
        """Get the value of a variable after a solve.
        :param key: A hashable key to fetch the variable.
        :return: A boolean value
        :rtype: bool
        """
        var = self.variables[key]
        return self.solver.BooleanValue(var)

    def print_variables(self):
        print("Variables:")
        data = [
            [key, self.solver.BooleanValue(var)] for key, var in self.variables.items()
        ]
        print(tabulate(data))
