"""
- Heuristics:
  - [x] Equal workload per artist
  - [x] Equal shots count per artist

  - Artist prefer shots with the same tags (ex: close-up)
    - In general, assigning the same tags on the same user is preferred.
  - Artists have seniority which make them better for hard tasks
- Constraint:
  - [x] A shot can only be assigned once

- TODO: Points for consecutive shots on the same user.
- TODO: Ensure we give equal treatment to artists preferences.
"""
import datetime
import itertools
import statistics
from dataclasses import dataclass
from typing import Dict, List, Literal
import operator

import humanize
from tabulate import tabulate

from csp4cg import core, utils


@dataclass
class Artist:
    id: int
    name: str
    tags: Dict[str, str]
    availability: int

    def __repr__(self):
        return f"Artist({self.id}, {self.name})"

    def __hash__(self):
        return hash(repr(self))


@dataclass
class Shot:
    id: int
    name: str
    duration: datetime.timedelta
    tags: List[str]

    def __repr__(self):
        return f"<Shot {self.name} ({self.duration} h)>"

    def __hash__(self):
        return hash(repr(self))


@dataclass
class ArtistAssignment:
    """An artist assignment to a shot."""

    artist: Artist
    shot: Shot


@dataclass
class ArtistShotPreference:
    """An artist preference toward a shot."""

    artist: Artist
    shot: Shot
    score: int


@dataclass
class ShotCombination:
    """A sequence of shots we'd like to have assigned to the same artist."""

    shots: List[Shot]
    weight: int

    def __str__(self):
        return "assign_multiple_%s" % ("_and_".join(shot.name for shot in self.shots))


@dataclass
class Settings:
    """Settings for solver heuristics."""

    weight_equal_hours_by_artists: Literal[0]
    weight_equal_shot_count_by_artists: Literal[0]


@dataclass()
class Config(core.Config):
    """Hold the data to solve"""

    artists: List[Artist]
    shots: List[Shot]
    assignments: List[ArtistAssignment]
    preferences: List[ArtistShotPreference]
    settings: Settings
    combinations: List[ShotCombination]

    @classmethod
    def from_data(cls, config):
        # Create artists
        artists = [
            Artist(
                id_,
                data["name"],
                {tag["name"]: tag["weight"] for tag in data.get("tags", {})},
                data.get("availability", 100),
            )
            for id_, data in enumerate(config["artists"])
        ]
        artists_by_name = {artist.name: artist for artist in artists}

        # Create shots
        # TODO: Do we handle time not representable in minutes?
        shots = [
            Shot(
                id_,
                data["name"],
                datetime.timedelta(hours=data["duration"]),
                data.get("tags", []),
            )
            for id_, data in enumerate(config["shots"])
        ]
        shots_by_name = {shot.name: shot for shot in shots}

        # Load solver settings
        settings = Settings(
            config.get("settings", {}).get("EQUAL_HOURS_BY_USER", 0),
            config.get("settings", {}).get("EQUAL_SHOT_COUNT_BY_USER", 0),
        )

        # Load predefined assignments
        assignments = [
            ArtistAssignment(
                artists_by_name[entry["artist"]], shots_by_name[entry["shot"]]
            )
            for entry in config.get("assignments", [])
        ]

        # Load preferences
        preferences = []
        for entry in config.get("preferences", ()):
            preferences.append(
                ArtistShotPreference(
                    artists_by_name[entry["artist"]],
                    shots_by_name[entry["shot"]],
                    entry.get("weight", 1),
                )
            )

        # Load additional preferences from artists/shot tags
        for artist, shot in itertools.product(artists, shots):
            for tag, weight in artist.tags.items():
                if tag in shot.tags:
                    preferences.append(ArtistShotPreference(artist, shot, weight))

        # Load preferred shot sequenced
        combinations = [
            ShotCombination(
                [shots_by_name[shot_name] for shot_name in entry["shots"]],
                int(entry["weight"]),
            )
            for entry in config.get("preferred_combinations", ())
        ]
        return cls(artists, shots, assignments, preferences, settings, combinations)


class Solver(core.Solver):
    def __init__(self, config: Config, printer=None):
        super(Solver, self).__init__(printer=printer)
        self.artists = config.artists
        self.shots = config.shots
        # Convert shot durations to internal units
        duration_by_shot = {
            shot: _timedelta_to_unit(shot.duration) for shot in self.shots
        }
        total_duration = sum(duration_by_shot.values())
        num_tasks = len(self.shots)
        num_users = len(self.artists)

        # Create variables
        for artist, shot in itertools.product(self.artists, self.shots):
            self.create_variable_bool(
                (shot.id, artist.id), "assign_shot_%s_to_%s" % (shot.name, artist.name)
            )

        # A shot need to be assigned to an artist and only once
        for shot in self.shots:
            expr = (
                sum(self.get_variable((shot.id, artist.id)) for artist in self.artists)
                == 1
            )
            self.add_hard_constraint(expr)

        # Apply already made assignments
        for assignment in config.assignments:
            expr = self.get_variable((assignment.shot.id, assignment.artist.id)) == 1
            self.add_hard_constraint(expr)

        # Apply preferences
        for preference in config.preferences:
            variable = self.get_variable((preference.shot.id, preference.artist.id))
            self.set_variable_bool_score(variable, preference.score)

        # Apply transitions
        for combination in config.combinations:
            weight = combination.weight
            num_shots = len(combination.shots)
            prefix = str(combination)

            var_transition = self.create_soft_constraint_bool(prefix, weight)
            variables = []
            for artist in self.artists:
                intermediate_var = self.model.NewBoolVar(prefix + "_to_" + artist.name)
                expr = (
                    sum(
                        self.get_variable((shot.id, artist.id))
                        for shot in combination.shots
                    )
                    == num_shots
                )
                self.add_hard_constraint(expr).OnlyEnforceIf(intermediate_var)
                variables.append(intermediate_var)
            self.model.AddBoolOr(variables).OnlyEnforceIf(var_transition)

        # Ensure all artists work the same number of hours RELATIVE TO AVAILABILITY
        exprs = (
            sum(
                self.get_variable((shot.id, artist.id)) * duration_by_shot[shot]
                for shot in self.shots
            )
            for artist in self.artists
        )
        total_availability = sum(artist.availability for artist in self.artists)
        goals = [
            int(total_duration * artist.availability / total_availability)
            for artist in self.artists
        ]
        self.create_total_distance_soft_constraint(
            "hours_diff",
            exprs,
            goals,
            total_duration,
            config.settings.weight_equal_hours_by_artists,
        )

        # Minimize deviation from average tasks per user ?
        exprs = (
            sum(self.get_variable((shot.id, artist.id)) for shot in self.shots)
            for artist in self.artists
        )
        goal = int(num_tasks / num_users)
        goals = [goal] * num_users
        self.create_total_distance_soft_constraint(
            "task_count",
            exprs,
            goals,
            num_tasks,
            config.settings.weight_equal_shot_count_by_artists,
        )

    def solve(self):
        super(Solver, self).solve()

        self.print_assignments()
        self.print_total_hours()
        self.print_statistics(self.artists, self.shots)
        self.print_score_tracking()

        return self.get_assignments()

    def get_assignments(self, getter=None):
        getter = getter or self.solver.BooleanValue
        # Return assignations as a mapping of shots per artist
        shots_by_artists = {artist: [] for artist in self.artists}
        for artist, shot in itertools.product(self.artists, self.shots):
            variable = self.get_variable((shot.id, artist.id))
            if getter(variable):
                shots_by_artists[artist].append(shot)
        return shots_by_artists

    def create_total_distance_soft_constraint(
        self, prefix, expressions, goals, domain, multiplier
    ):
        """
        :param prefix: The prefix to use for intermediate variables.
        :param expressions: Expressions computing the values
        :param goal: The desired value for all expressions
        :param domain: The domain
        :param multiplier: A cost multiplier
        """
        # Create one variable for each distances from the goal
        vars_distances = [
            utils.create_distance(self.model, domain, prefix, expr_workload, goal)
            for i, (expr_workload, goal) in enumerate(zip(expressions, goals))
        ]

        # We'll want the penalty to be relative to the domain.
        # Since we use integer arithmetics we need to scale our computations in percentage.
        new_domain = domain * multiplier * 100
        expr_total_penalty = -sum(vars_distances) * multiplier * 100
        var_penalty = self.model.NewIntVar(-new_domain, 0, f"{prefix}_sadads")
        var_penalty_adjusted = self.model.NewIntVar(-new_domain, 0, f"{prefix}_sadads")
        self.model.Add(var_penalty == expr_total_penalty)
        self.model.AddDivisionEquality(var_penalty_adjusted, var_penalty, domain)
        var = self.create_weighted_variable_int(f"{prefix}_cost", -domain, 0)
        self.model.Add(var <= var_penalty_adjusted)

    def print_statistics(self, artists, shots):
        total_duration = sum((shot.duration for shot in shots), datetime.timedelta())
        num_shots = len(shots)
        num_users = len(artists)
        mean_shot_per_user = num_shots / num_users

        # Print average deviation
        hoursByUser = {artist: datetime.timedelta() for artist in artists}
        for artist, shot in itertools.product(artists, shots):
            if self.solver.BooleanValue(self.get_variable((shot.id, artist.id))):
                hoursByUser[artist] += shot.duration
        values = hoursByUser.values()

        mean = total_duration / num_users
        deviation = statistics.stdev([timedelta.seconds for timedelta in values])
        shots_by_users_mean = mean_shot_per_user

        print("Statistics:")
        print()
        print(f"Total Duration: {total_duration}")
        print()
        print("  Hours by Users:")
        print(f"    Mean: {mean}")
        print(f"    Deviation: {deviation}")
        print("")
        print("  Shots by Users:")
        print(f"    Num Shots: {num_shots}")
        print(f"    Num Users: {num_users}")
        print(f"    Mean: {shots_by_users_mean}")

    def print_total_hours(self):
        """Print a table of the total number of hours assigned to each animators."""
        print()
        print("Total hours by users:")
        data = []
        for artist in self.artists:
            total = sum(
                (
                    self.solver.BooleanValue(self.variables[shot.id, artist.id])
                    * shot.duration
                    for shot in self.shots
                ),
                datetime.timedelta(),
            )
            data.append([artist.name, "%s hours" % (total.total_seconds() / 60 / 60)])
        data = sorted(data, key=operator.itemgetter(1), reverse=True)
        print(tabulate(data))

    def print_assignments(self):
        """Print the solved shot to artist assignments."""
        print()
        print("User assignments:")
        headers = ["Shot", "Tags"] + [f"{artist.name}" for artist in self.artists]
        data = []
        for shot in self.shots:
            row = [
                "x"
                if self.solver.BooleanValue(self.variables[shot.id, artist.id])
                else ""
                for artist in self.artists
            ]
            shot_duration = humanize.naturaldelta(shot.duration)
            data.append([f"{shot.name} ({shot_duration})", shot.tags] + row)
        print(tabulate(data, headers=headers))


def _timedelta_to_unit(delta: datetime.timedelta):
    """Convert a datetime timedelta objects to internal units.
    The smallest unit of time we handle is minutes.

    :param delta: A timedelta object
    :return: An amount of minutes
    :rtype: int
    """
    return int(delta.total_seconds() / 60)
