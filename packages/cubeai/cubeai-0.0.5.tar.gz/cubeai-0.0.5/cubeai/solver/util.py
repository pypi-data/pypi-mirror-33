# util.py
# -------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

import heapq

"""
 Data structures useful for implementing SearchAgents
"""


class Stack:
    """"A container with a last-in-first-out (LIFO) queuing policy."""
    def __init__(self):
        self.list = []

    def push(self, item):
        """"Push 'item' onto the stack"""
        self.list.append(item)

    def pop(self):
        """"Pop the most recently pushed item from the stack"""
        return self.list.pop()

    def is_empty(self):
        """"Returns true if the stack is empty"""
        return len(self.list) == 0


class Queue:
    """"A container with a first-in-first-out (FIFO) queuing policy."""
    def __init__(self):
        self.list = []

    def push(self, item):
        """"Enqueue the 'item' into the queue"""
        self.list.insert(0, item)

    def pop(self):
        """
          Dequeue the earliest enqueued item still in the queue. This
          operation removes the item from the queue.
        """
        return self.list.pop()

    def is_empty(self):
        """"Returns true if the queue is empty"""
        return len(self.list) == 0


class PriorityQueue:
    """
      Implements a priority queue data structure. Each inserted item
      has a priority associated with it and the client is usually interested
      in quick retrieval of the lowest-priority item in the queue. This
      data structure allows O(1) access to the lowest-priority item.

      Note that this PriorityQueue does not allow you to change the priority
      of an item.  However, you may insert the same item multiple times with
      different priorities.
    """
    def __init__(self):
        self.heap = []
        self.init = False

    def push(self, item, priority):
        if not self.init:
            self.init = True
            try:
                item < item
            except:
                item.__class__.__lt__ = lambda x, y: True
        pair = (priority, item)
        heapq.heappush(self.heap, pair)

    def pop(self):
        (priority, item) = heapq.heappop(self.heap)
        return item

    def is_empty(self):
        return len(self.heap) == 0


class PriorityQueueWithFunction(PriorityQueue):
    """
    Implements a priority queue with the same push/pop signature of the
    Queue and the Stack classes. This is designed for drop-in replacement for
    those two classes. The caller has to provide a priority function, which
    extracts each item's priority.
    """
    def __init__(self, priority_function):
        """"priority_function (item) -> priority"""
        self.priority_function = priority_function  # store the priority function
        super().__init__()  # super-class initializer

    def push(self, item):
        """"Adds an item to the queue with priority from the priority function"""
        PriorityQueue.push(self, item, self.priority_function(item))


def manhattan_distance(xy1, xy2):
    """"Returns the Manhattan distance between points xy1 and xy2 in R^2"""
    return abs(xy1[0] - xy2[0]) + abs(xy1[1] - xy2[1])
