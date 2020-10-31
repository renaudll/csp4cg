"""
- Heuristics:
  - Equal workload per artist
  - Minimize number of shots per artist
  - Artist prefer shots with the same tags (ex: close-up)
    - Some tags have more weights when consecutive on the same artist, ex: consecutive shots)
    - Some tags have more weights on certain users (preference, ex: combat)
    - In general, assigning the same tags on the same user is prefered.
  - Artists have seniority which make them better for hard tasks

- Constraint:
  - A shot can only be assigned once
  - An artist have a maximum of work hours
  - An artist cannot finish after the deadline

- CBB:
  - Different work hours per artist or vacation support
"""
from __future__ import print_function
from ortools.linear_solver import pywraplp

_SHOTS = [5,5,5,3,3,3,2,2,2]
_LIMIT = 16
_NUM_ARTISTS = 3

_TOTAL_WORK = 0
for shot in _SHOTS:
    _TOTAL_WORK += shot

print("Total work: %s" % _TOTAL_WORK)
assert float(_TOTAL_WORK)/_NUM_ARTISTS < _LIMIT


def create_data_model():
    """Create the data for the example."""
    data = {}
    weights = _SHOTS
    values = _SHOTS
    data['weights'] = weights
    data['values'] = values
    data['items'] = list(range(len(weights)))
    data['num_items'] = len(weights)
    data['bins'] = list(range(_NUM_ARTISTS))
    data['bin_capacities'] = [_LIMIT]* _NUM_ARTISTS
    return data


def main():
    data = create_data_model()

    # Create the mip solver with the SCIP backend.
    solver = pywraplp.Solver.CreateSolver('SCIP')

    # Variables
    # x[i, j] = 1 if item i is packed in bin j.
    x = {}
    for i in data['items']:
        for j in data['bins']:
            x[(i, j)] = solver.IntVar(0, 1, 'x_%i_%i' % (i, j))

    # Constraints
    # Each item can be in at most one bin.
    for i in data['items']:
        solver.Add(sum(x[i, j] for j in data['bins']) <= 1)
    # The amount packed in each bin cannot exceed its capacity.
    for j in data['bins']:
        solver.Add(
            sum(x[(i, j)] * data['weights'][i]
                for i in data['items']) <= data['bin_capacities'][j])

    # Objective
    objective = solver.Objective()

    for i in data['items']:
        for j in data['bins']:
            objective.SetCoefficient(x[(i, j)], data['values'][i])
    objective.SetMaximization()

    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        print('Total packed value:', objective.Value())
        total_weight = 0
        for j in data['bins']:
            bin_weight = 0
            bin_value = 0
            print('Bin ', j, '\n')
            for i in data['items']:
                if x[i, j].solution_value() > 0:
                    print('Item', i, '- weight:', data['weights'][i], ' value:',
                          data['values'][i])
                    bin_weight += data['weights'][i]
                    bin_value += data['values'][i]
            print('Packed bin weight:', bin_weight)
            print('Packed bin value:', bin_value)
            print()
            total_weight += bin_weight
        print('Total packed weight:', total_weight)
    else:
        print('The problem does not have an optimal solution.')


if __name__ == '__main__':
    main()
