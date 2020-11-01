"""Utility methods"""


def create_distance(model, domain, prefix, value1, value2):
    """Create a variable that will contain the distance between two expression/value."""
    delta = value1 - value2
    var_delta = model.NewIntVar(-domain, domain, f"{prefix}_delta")
    var_distance = model.NewIntVar(0, domain, f"{prefix}_distance")
    model.Add(var_delta == delta)
    model.AddAbsEquality(var_distance, var_delta)
    return var_distance
