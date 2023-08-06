from cubeai.solver import search
from cubeai.cube.cube import Face, Action
import numpy as np


class CubeProblem(search.SearchProblem):
    """ a Problem class to be used with the search module """

    def __init__(self, cube, quarter_metric=True):
        """
        :param cube: a cubeai.cube.cube.Cube instance
        :param quarter_metric: if True, use 90 degrees rotations only.
                               otherwise use also 180 degrees.
        """
        self.cube = cube
        self.expanded = 0
        self.actions = []
        if quarter_metric:
            k_values = (-1, 1)
        else:
            k_values = (-1, 1, 2)
        for layer in range(self.cube.layers // 2):
            for k in k_values:
                self.actions += [Action(face, k, layer) for face in Face]

    def get_start_state(self):
        return self.cube.copy()

    def is_goal_state(self, cube):
        return cube.is_solved()

    def get_successors(self, cube):
        self.expanded += 1
        successors = []
        for action in self.actions:
            successor = cube.copy().rotate(
                action.face, action.k, action.layer)
            successors.append((successor, action, 1))
        return successors

    def get_cost_of_actions(self, actions):
        return len(actions)


def solve(cube, heuristic=lambda *args: 0, verbose=False):
    """
    solves a given cube instance
    :param cube: cubeai.cube.cube.Cube instance
    :param heuristic: a heuristic function for A* search.
                      takes a cube and problem instances as input and returns
                      a number.
                      by default, uses the null heuristic (0 for every state)
    :param verbose: if True, prints some information about the search
    :return: a list of actions that solves the cube
    """
    cube_problem = CubeProblem(cube)
    solution = search.a_star(cube_problem, heuristic)
    if verbose:
        solution_str = ' '.join([str(s) for s in solution])
        print('Length %d solution found:\n%s' %
              (len(solution), solution_str))
        print('Expanded %d nodes.' % cube_problem.expanded)
    return solution


def random_actions(cube, num_actions, quarter_metric=True):
    """
    returns a sequence of random actions on the given cube
    (does not apply the actions to the cube)
    :param cube: Cube object
    :param num_actions: an integer >= 1
    :param quarter_metric: whether to use the quarter-turn metric or not
    :return: a sequence of `num_actions' actions
    """
    assert num_actions >= 1
    cube_problem = CubeProblem(cube, quarter_metric)
    last_cube = cube.copy()
    visited = {last_cube.copy()}
    possible_actions = cube_problem.actions
    actions = [None] * num_actions
    actions[0] = np.random.choice(possible_actions)
    for i in range(1, num_actions):
        rand_action = np.random.choice(possible_actions)
        while last_cube.copy().apply([rand_action]) in visited:
            rand_action = np.random.choice(possible_actions)
        actions[i] = rand_action
        last_cube.apply([rand_action])
        visited.add(last_cube.copy())
    return actions
