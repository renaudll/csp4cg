"""CSP solvers"""
import datetime
import itertools
from typing import Generator, Hashable, Tuple, Iterable

from ortools.sat.python.cp_model import (
    CpModel,
    CpSolver,
    Constraint,
    IntVar,
    ObjectiveSolutionPrinter,
    BoundedLinearExpression,
    OPTIMAL,
    FEASIBLE,
)

from ._types import Task, Artist, Context, Assignment

_VARIABLE_ASSIGNMENT_TEMPLATE = "assign_task_{task}_to_{artist}"


class _Solver:
    """Generic solver class."""

    def __init__(self):
        self.model = CpModel()
        self.solver = CpSolver()
        # Ideal number of workers is 8, see https://or.stackexchange.com/a/4126
        self.solver.parameters.num_search_workers = 8
        self._known_names = set()
        self._vars_bool = {}
        self._vars_int = {}
        self._vars_weighted = []
        self._vars_weighted_cost = []
        self.printer = ObjectiveSolutionPrinter()

    def create_variable_bool(self, name: str = None) -> IntVar:
        """Create a boolean variable.

        :param name: The variable human readable name.
        :return: The new variable
        """
        assert name not in self._vars_bool
        assert name not in self._known_names

        var = self.model.NewBoolVar(name)
        self._vars_bool[name] = var
        return var

    def create_variable_int(
        self, key: str, minimum: int, maximum: int, name: str = None
    ) -> IntVar:
        """Create an integer variable.

        :param key: An hashable value to use as an identifier.
        :param minimum: The variable domain minimum value.
        :param maximum: The variable domain maximum value.
        :param name: The variable human readable name.
        :return: The new variable
        """
        name = name or "_".join(key)

        assert key not in self._vars_int
        assert name not in self._known_names

        var = self.model.NewIntVar(minimum, maximum, name)
        self._vars_int[key] = var
        return var

    def get_variable_bool(self, key: Hashable) -> IntVar:
        """Get an already defined boolean variable.

        :param key: A hashable key
        :return: A variable
        :raises KeyError: If no variable exist for the provided key.
        """
        return self._vars_bool[key]

    def add_hard_constraint(self, expr: BoundedLinearExpression) -> Constraint:
        """Add a "hard" constraint. T
        he solve will fail if even once hard constraint fail to be satisfied.

        :param expr: The constraint expression
        :return: A constraint
        """
        return self.model.Add(expr)

    def set_variable_bool_score(self, variable: Constraint, score: int) -> None:
        """Set the cost for a variable.

        :param variable: A variable
        :param score: The cost if the variant is ON
        """
        self._vars_weighted.append(variable)
        self._vars_weighted_cost.append(score)

    def create_soft_constraint_bool(self, name: str, score: int) -> Constraint:
        """Add a "soft" boolean variable with a score.
        The solver will try to maximize it's score.

        :param str name: The variable name
        :param int score: The variable score
        :return: A constraint
        """
        assert name not in self._known_names
        var = self.model.NewBoolVar(name)
        self.set_variable_bool_score(var, score)
        return var

    def create_soft_constraint_int(
        self, name: str, minimum: int, maximum: int, score: int
    ) -> IntVar:
        """Add a "soft" integer variable with a score.
        The solver will try to maximum it's score.

        :param name: The variable name
        :param minimum: The variable domain minimum value
        :param maximum: The variable domain maximum value
        :param score: The variable score
        :return: A constraint
        """
        assert name not in self._known_names
        var = self.model.NewIntVar(minimum, maximum, name)
        self._vars_weighted.append(var)
        self._vars_weighted_cost.append(score)
        return var

    def iter_variables_and_cost(self) -> Generator[Tuple[IntVar, int], None, None]:
        """Yield all variables and their score multipliers."""
        for variable, score in zip(self._vars_weighted, self._vars_weighted_cost):
            yield variable, score

    def solve(self):
        """Solve using provided constraints."""

        self.model.Maximize(
            sum(
                var * cost
                for var, cost in zip(
                    itertools.chain(
                        self._vars_weighted,
                        self._vars_weighted,
                    ),
                    itertools.chain(
                        self._vars_weighted_cost,
                        self._vars_weighted_cost,
                    ),
                )
            )
        )
        status = self.solver.SolveWithSolutionCallback(self.model, self.printer)

        if status not in (OPTIMAL, FEASIBLE):
            raise RuntimeError("No solution found! Status is %s" % status)
        return status


class Solver(_Solver):
    """Solver that assign tasks to artists."""

    def __init__(self, context: Context):
        super().__init__()
        self.artists = context.artists
        self.tasks = context.tasks

        # Convert task durations to internal units
        duration_by_task = {
            task: _timedelta_to_unit(task.duration) for task in self.tasks
        }
        total_duration = sum(duration_by_task.values())
        num_tasks = len(self.tasks)
        num_users = len(self.artists)

        # Create one variable for each possible assignment
        for artist, task in itertools.product(self.artists, self.tasks):
            self.create_variable_assignment(task, artist)

        # A task need to be assigned to an artist and only once
        for task in self.tasks:
            variable = sum(
                self.get_variable_assignment(task, artist) for artist in self.artists
            )
            self.add_hard_constraint(variable == 1)

        # Apply already made assignments
        for assignment in context.assignments:
            expr = self.get_variable_assignment(assignment.task, assignment.artist) == 1
            self.add_hard_constraint(expr)

        # Compute individual artists preferences using tags.
        for artist, task in itertools.product(self.artists, self.tasks):
            for tag, weight in artist.tags.items():
                if tag == task.name or tag in task.tags:
                    variable = self.get_variable_assignment(task, artist)
                    self.set_variable_bool_score(variable, weight)

        # Apply combinations
        # This give points if a set of task are all assigned to the same artist.
        for combination in context.combinations:
            weight = combination.weight
            combination_task_count = len(combination.tasks)
            prefix = str(combination)

            var_transition = self.create_soft_constraint_bool(prefix, weight)
            variables = []
            for artist in self.artists:
                intermediate_var = self.model.NewBoolVar(prefix + "_to_" + artist.name)
                expr = (
                    sum(
                        self.get_variable_assignment(task, artist)
                        for task in combination.tasks
                    )
                    == combination_task_count
                )
                self.add_hard_constraint(expr).OnlyEnforceIf(intermediate_var)
                variables.append(intermediate_var)
            self.model.AddBoolOr(variables).OnlyEnforceIf(var_transition)

        # Ensure all artists work the same number of hours RELATIVE TO AVAILABILITY
        total_availability = sum(artist.availability for artist in self.artists)
        for artist in self.artists:
            expr = sum(
                self.get_variable_assignment(task, artist) * duration_by_task[task]
                for task in self.tasks
            )
            goal = int(total_duration * artist.availability / total_availability)
            self.create_soft_constraint_target_value(
                f"{artist.name}_hours_deviation_cost",
                expr,
                goal,
                total_duration,
                context.settings.weight_equal_hours_by_artists,
            )

        # Minimize deviation from average tasks per user ?
        for artist in self.artists:
            expr = sum(
                self.get_variable_assignment(task, artist) for task in self.tasks
            )
            self.create_soft_constraint_target_value(
                f"{artist.name}_number_of_tasks_deviation_cost",
                expr,
                int(num_tasks / num_users),
                num_tasks,
                context.settings.weight_equal_tasks_count_by_artists,
            )

    def solve(self) -> Tuple[Assignment, ...]:
        """Solve using provided constraints."""
        super().solve()
        return tuple(self._iter_assignments())

    def _iter_assignments(self) -> Iterable[Assignment]:
        """Iter current assignments"""
        for artist, task in itertools.product(self.artists, self.tasks):
            variable = self.get_variable_assignment(task, artist)
            if self.solver.BooleanValue(variable):
                yield Assignment(artist=artist, task=task)

    def create_soft_constraint_target_value(
        self, prefix: str, expr: IntVar, goal: int, domain: int, cost: int
    ):
        """
        Create a bias for a particular value.
        The cost for deviating from that value is exponential.

        :param prefix: A common prefix for the variables to create.
        :param expr: The affected variable.
        :param goal: The variable desired value.
        :param cost: A cost multiplier.
        """
        var_distance = _create_distance(self.model, domain, prefix, expr, goal)
        var_weight = self.create_variable_int(f"{prefix}_cost", 0, domain * domain)
        self.model.AddMultiplicationEquality(var_weight, [var_distance, var_distance])
        var_total = self.create_soft_constraint_int(
            f"{prefix}__total", 0, domain * domain * cost, -1
        )
        self.model.Add(var_total == var_weight * cost)

    def create_variable_assignment(self, task: Task, artist: Artist) -> IntVar:
        """Create a boolean variable defining a possible task to artist assignment.

        :param task: The assignment task
        :param artist: The assignment artist
        :return: A boolean variable
        """
        name = _VARIABLE_ASSIGNMENT_TEMPLATE.format(task=task.name, artist=artist.name)
        return self.create_variable_bool(name)

    def get_variable_assignment(self, task: Task, artist: Artist) -> IntVar:
        """Get a boolean variable representing a possible task to artist assignment.

        :param task: The assignment task
        :param artist: The assignment artist
        :return: A boolean variable
        """
        name = _VARIABLE_ASSIGNMENT_TEMPLATE.format(task=task.name, artist=artist.name)
        return self.get_variable_bool(name)


def _timedelta_to_unit(delta: datetime.timedelta) -> int:
    """Convert a datetime timedelta objects to internal units.
    The smallest unit of time we handle is minutes.

    :param delta: A timedelta object
    :return: An amount of minutes
    """
    return int(delta.total_seconds() / 60)


def _create_distance(model, domain, prefix, value1, value2):
    """Create a variable that will contain the distance between two expression/value."""
    delta = value1 - value2
    var_delta = model.NewIntVar(-domain, domain, f"{prefix}_delta")
    var_distance = model.NewIntVar(0, domain, f"{prefix}_distance")
    model.Add(var_delta == delta)
    model.AddAbsEquality(var_distance, var_delta)
    return var_distance
