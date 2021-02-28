"""Rez-like package manager re-implementation using CSP"""
import logging
import functools
from dataclasses import dataclass
from typing import List

from packaging.requirements import Requirement
from csp4cg import core

logging.basicConfig()
_LOG = logging.getLogger(__name__)
_LOG.setLevel(logging.INFO)


@dataclass
@functools.total_ordering
class PackageVersion:
    """A registered package version, ex: python-3.7"""

    name: str
    version: Requirement
    requirements: List[Requirement]

    def __str__(self):
        return f"{self.name}-{self.version}"

    def __hash__(self):
        return hash(repr(self))

    def __lt__(self, other):
        return self.name > other.name and self.version > other.version

    def __eq__(self, other):
        return self.name == other.name and self.version == other.version


@dataclass
class Package:
    """A registered package, ex: python"""

    name: str
    versions: List[PackageVersion]

    def __post_init__(self):
        self._version_by_version = {
            version.version: version for version in self.versions
        }

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(repr(self))

    def __iter__(self):
        return iter(self.versions)

    def __getitem__(self, version):
        return self._version_by_version[version]


@dataclass
class Config(core.Config):
    """A package configuration"""

    packages: List[Package]

    @classmethod
    def from_data(cls, config):
        packages = []
        for package_name, package_data in config.items():
            versions = []
            for version_data in package_data:
                # UX: We cast version to string in case user wrote a YAML float
                version_number = str(version_data["version"])
                requires = version_data.get("requires", [])
                requires = [requires] if not isinstance(requires, list) else requires
                requirements = [Requirement(require) for require in requires]
                version = PackageVersion(package_name, version_number, requirements)
                versions.append(version)
            package = Package(package_name, versions)
            packages.append(package)
        return cls(packages)


@dataclass
class PackageRegistry:
    """A collection of packages"""

    packages: List[Package]

    def __post_init__(self):
        self._package_by_name = {package.name: package for package in self.packages}

    def __iter__(self):
        return iter(self.packages)

    def __len__(self):
        return len(self.packages)

    def __getitem__(self, name):
        return self._package_by_name[name]


class Solver(core.Solver):
    def __init__(self, config, packages=None, request="core_publish"):
        super(Solver, self).__init__()
        packages = packages or PackageRegistry(config.packages)
        request = request.split(" ") if request else []

        # Create a boolean for each
        # We don't want the solver to "want" to add package.
        # Because of this, package have negative weight.
        # And older package have more negative weight.

        for package in packages:
            for version, score in zip(
                sorted(package.versions), reversed(range(len(packages)))
            ):
                var = self.create_variable_bool(
                    version, name=f"{package.name}_{version.version}"
                )
                self.set_variable_bool_score(var, -score)

        # Hard constraint: We can only have one version of a package at a time.
        for package in packages:
            variables = (self.get_variable(version) for version in package)
            expr = 0 <= sum(variables) <= 1
            self.add_hard_constraint(expr)

        # Hard constraint: We want requested packages
        for package_name in request:
            package = packages[package_name]
            variables = (self.get_variable(version) for version in package)
            expr = sum(variables) == 1
            self.add_hard_constraint(expr)

        # Hard constraint: Apply requires
        for package in packages:
            for version in package.versions:
                for requirement in version.requirements:
                    dependency = packages[
                        requirement.name
                    ]  # TODO: .requirements should already have the proper datatype
                    matchs = [
                        version_
                        for version_ in dependency.versions
                        if requirement.specifier.contains(version_.version)
                    ]
                    for match in matchs:
                        _LOG.debug("%s is a requirement of %s", match, version)

                    expr = sum(self.get_variable(match) for match in matchs) == 1
                    var_package = self.get_variable(version)
                    self.add_hard_constraint(expr).OnlyEnforceIf(var_package)

    def solve(self):
        super(Solver, self).solve()

        self.print_variables()

        return {
            key for key, var in self.variables.items() if self.get_variable_result(key)
        }
