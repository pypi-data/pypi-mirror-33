# Magic Cube AI Solver

The common solutions to the magic cube (a.k.a Rubik's Cube) involve
one of the two:
1. Unreasonable amount of resources - CPU, memory, etc. or,
2. A very large number of steps

It has been shown that any _3x3x3_ cube can be solved
using no more than 26 quarter turns (90 degrees rotations of the cube's faces),
yet the efficient solvers tend to yield solutions with dozens of turns.

The usual AI methods don't work well with this problem due to the complex
nature of the [group](https://en.wikipedia.org/wiki/Rubik%27s_Cube_group)
which is induced by the cube.
Namely, the _A*_ search algorithm needs a good heuristic to be able to
efficiently cover its search space, and those are hard to come up with.

We propose the following approach:
* Use Machine Learning to learn a heuristic
* Perform _A*_ search with the learned heuristic
