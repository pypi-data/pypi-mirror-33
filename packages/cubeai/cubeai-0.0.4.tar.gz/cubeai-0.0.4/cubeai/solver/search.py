from cubeai.solver import util


class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def get_start_state(self):
        """
        Returns the start state for the search problem
        """
        util.raiseNotDefined()

    def is_goal_state(self, state):
        """
        state: Search state

        Returns True if and only if the state is a valid goal state
        """
        util.raiseNotDefined()

    def get_successors(self, state):
        """
        state: Search state

        For a given state, this should return a list of triples,
        (successor, action, stepCost), where 'successor' is a
        successor to the current state, 'action' is the action
        required to get there, and 'stepCost' is the incremental
        cost of expanding to that successor
        """
        util.raiseNotDefined()

    def get_cost_of_actions(self, actions):
        """
        actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.  The sequence must
        be composed of legal moves
        """
        util.raiseNotDefined()


class Node:
    """
    A simple node class which saves arbitrary data and a pointer to a parent.
    """

    def __init__(self, data, parent=None):
        """
        Initializes a new node
        :param data: data to save
        :param parent: node's parent (Node object)
        """
        self.data = data
        self.parent = parent

    def is_root(self):
        """
        :return: True if this node has a parent, False otherwise
        """
        return True if self.parent is None else False

    def path_from_root(self):
        """
        :return: a list of nodes which corresponds to a path from the root
                 to this node
        """
        path = []
        current = self
        while current is not None:
            path.append(current)
            current = current.parent
        # the above path is reversed. return the correct order:
        return path[::-1]


class SearchNode(Node):
    """ a node where the data saved is the (state,action,cost) triplet """
    def __init__(self, state, action, cost, parent=None):
        super().__init__(None, parent)
        self.state = state
        self.action = action
        self.cost = cost


def _cost_so_far(node):
    """ also referred to as `g' in the class notation """
    prev_cost = 0 if node.is_root() else node.parent.incremental_cost
    node.incremental_cost = prev_cost + node.cost
    return node.incremental_cost


def generic_search(problem, data_structure, **kwargs):
    """
    Implements a generic search algorithm which. I.e. this algorithm
    can be used with different data structures as fringe.

    :param problem: The search problem instance
    :param data_structure: A data structure for the fringe (e.g. Stack)
    :param kwargs: Additional keyword arguments for the data structure init
    :return: A list of actions if a goal state is found, None otherwise
    """

    fringe = data_structure(**kwargs)
    visited = set()
    start_state = problem.get_start_state()
    fringe.push(SearchNode(state=start_state, action=None, cost=0))
    visited.add(start_state)
    while not fringe.is_empty():
        node = fringe.pop()
        if problem.is_goal_state(node.state):
            # omit the root node (doesn't have any action)
            path_from_root = node.path_from_root()[1:]
            return [p.action for p in path_from_root]
        else:
            visited.add(node.state)
            for successor, action, cost in problem.get_successors(node.state):
                if successor not in visited:
                    fringe.push(SearchNode(successor, action,
                                           cost, parent=node))
    # This means that the fringe is empty and no goal state was reached
    return []


def depth_first_search(problem):
    """
    Search the deepest nodes in the search tree first.
    """
    return generic_search(problem, util.Stack)


def breadth_first_search(problem):
    """
    Search the shallowest nodes in the search tree first.
    """
    return generic_search(problem, util.Queue)


def uniform_cost_search(problem):
    """
    Search the node of least total cost first.
    """
    return generic_search(problem, util.PriorityQueueWithFunction,
                          priority_function=_cost_so_far)


def null_heuristic(*_):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0


def a_star_search(problem, heuristic=null_heuristic):
    """
    Search the node that has the lowest combined cost and heuristic first.
    """
    def f(n):
        return heuristic(n.state, problem) + _cost_so_far(n)

    return generic_search(problem, util.PriorityQueueWithFunction,
                          priority_function=f)


# Abbreviations
bfs = breadth_first_search
dfs = depth_first_search
a_star = a_star_search
ucs = uniform_cost_search
