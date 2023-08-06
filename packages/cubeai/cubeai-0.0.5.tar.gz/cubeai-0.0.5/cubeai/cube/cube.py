# imports
import numpy as np
from enum import Enum


# helper functions
def invert_permutation(p):
    """ invert a permutation given by the list `p' """
    inv = np.empty(len(p), dtype=int)
    for i, val in enumerate(p):
        inv[val] = i
    return inv


# constants
NUM_FACES = 6


class Face(Enum):
    """ Enumeration of the cube's faces """
    FRONT = 0
    UP = 1
    RIGHT = 2
    DOWN = 3
    LEFT = 4
    BACK = 5


# go from a string to a face and backwards
FACE_TO_STR = {
    Face.FRONT: 'F',
    Face.BACK: 'B',
    Face.RIGHT: 'R',
    Face.LEFT: 'L',
    Face.UP: 'U',
    Face.DOWN: 'D'
}
STR_TO_FACE = {FACE_TO_STR[k]: k for k in FACE_TO_STR.keys()}

# the permutations and rotations for the Cube.rotate method
PERMUTATION = {
    Face.FRONT: [0, 1, 2, 3, 4, 5],
    Face.UP: [1, 5, 2, 0, 4, 3],
    Face.RIGHT: [2, 1, 5, 3, 0, 4],
    Face.DOWN: [3, 0, 2, 5, 4, 1],
    Face.LEFT: [4, 1, 0, 3, 5, 2],
    Face.BACK: [5, 1, 4, 3, 2, 0]
}
INVERSE_PERM = {face: invert_permutation(PERMUTATION[face])
                for face in Face}
ROTATION = {
    Face.FRONT: [0, 0, 0, 0, 0, 0],
    Face.UP: [0, 0, 1, 0, -1, 2],
    Face.RIGHT: [0, -1, 0, 1, 0, 0],
    Face.DOWN: [0, 0, -1, 0, 1, 2],
    Face.LEFT: [0, 1, 0, -1, 0, 0],
    Face.BACK: [0, 2, 0, 2, 0, 0]
}


# class definitions
class Action:
    """ a class to nicely represent an action. """

    def __init__(self, face_or_str, k=1, layer=0):
        """
        can be initialized either with a standard string (e.g. "F'") or
        explicitly give a face, amount and layer.
        :param face_or_str: cubeai.cube.cube.Face or string
        :param k: int
        :param layer: non-negative int
        """
        if isinstance(face_or_str, str):
            self.__init_from_str__(face_or_str)
        else:
            self.face = face_or_str
            self.k = k
            self.layer = layer

    def __init_from_str__(self, string):
        """
        initializes the action from an action string
        :param string: F B L R U D for front, back, left, right, up, down
                       respectively. default is clockwise rotation.
                       add ' in the end (e.g. R') for counter-clockwise,
                       or 2 for 180 degrees rotation (e.g. R2)
        """
        assert 1 <= len(string) <= 2
        assert string[0].upper() in ['F', 'B', 'R', 'L', 'U', 'D']
        self.face = STR_TO_FACE[string[0].upper()]
        if string[0].isupper():
            self.layer = 0
        else:
            self.layer = 1

        if string[-1] == "'":
            self.k = 1
        elif string[-1] == "2":
            self.k = 2
        else:
            self.k = 3

    def inverse(self):
        face = self.face
        k = (-self.k) % 4
        layer = self.layer
        return Action(face, k, layer)

    def __eq__(self, other):
        if isinstance(other, str):
            return self.__eq__(Action(other))
        return self.face == other.face \
            and self.k == other.k \
            and self.layer == other.k

    def __str__(self):
        result = FACE_TO_STR[self.face]
        if self.layer == 1:
            result = result.lower()
        if self.k == 1:
            result += "'"
        elif self.k == 2:
            result += "2"
        return result

    def __repr__(self):
        return str(self)


class Cube:
    """ A simple representation of a NxNxN cube (3x3x3 by default) """

    def __init__(self, layers=3):
        """
        Creates a new instance of a NxNxN cube, where N is the `layers' param
        :param layers: the number of layers in the cube (3 by default)
        """
        assert layers >= 2
        self.layers = layers
        self._array = np.zeros((layers, layers, NUM_FACES),
                               dtype=np.uint8)
        for face in Face:
            self._array[:, :, face.value] = face.value

    def copy(self):
        new_cube = Cube(self.layers)
        new_cube._array = self._array.copy()
        return new_cube

    @staticmethod
    def _rotate_front(arr, amount, layer):
        """
        Rotates the `layer'th layer in the front face of the cube represented
        by the array `arr'.
        :param arr: NxNx6 array representing a cube
        :param amount: the number of 90 deg. rotations clockwise
        :param layer: which layer to rotate (int between 0 and the number
                      of layers in the cube divided by 2)
        :return: a rotated array
        """
        arr_copy = arr.copy()
        if layer == 0:
            arr_copy[:, :, 0] = np.rot90(arr[:, :, 0], amount)
        for _ in range(amount):
            arr_copy[-(1+layer), :, 1] = arr[:, layer, 2]
            arr_copy[:, layer, 2] = arr[layer, :, 3][::-1]
            arr_copy[layer, :, 3] = arr[:, -(1+layer), 4]
            arr_copy[:, -(1+layer), 4] = arr[-(1+layer), :, 1][::-1]
            arr = arr_copy.copy()
        return arr_copy

    def to_array(self, flat=True):
        """
        :param flat: True for a flat array (1d), False for NxNx6 array
        :return: the array representing this cube
        """
        if flat:
            return self._array.flatten()
        else:
            return self._array.copy()

    def rotate(self, face, amount, layer=0):
        """
        Rotates a given layer parallel to a face of the cube
        :param face: must be a `Face' instance
        :param amount: number of counterclockwise rotations
        :param layer: which layer to rotate (int in the range [0,m/2) where
                      m is the number of layers in the cube)
        """
        # make sure the input is valid
        assert isinstance(face, Face)
        assert 0 <= layer < (self.layers // 2)

        amount %= 4
        if amount == 0:
            return self
        # get the relevant permutations and rotations
        perm = PERMUTATION[face]
        rotation = ROTATION[face]
        inverse = INVERSE_PERM[face]
        rotated = self._array.copy()
        # change the cube's orientation such that the input face is
        # the front face
        for i in range(NUM_FACES):
            rotated[:, :, i] = np.rot90(rotated[:, :, i], rotation[i])
        rotated = rotated[:, :, perm]
        # rotate the front (which is now the correct face to rotate)
        rotated = Cube._rotate_front(rotated, amount, layer)
        # change the cube back to the original orientation
        rotated = rotated[:, :, inverse]
        for i in range(NUM_FACES):
            rotated[:, :, i] = np.rot90(rotated[:, :, i], -rotation[i])
        # save the result in the inner array
        self._array = rotated
        return self

    def apply(self, sequence):
        # if the sequence is empty, do nothing
        if not sequence:
            return self
        # handle a string (e.g. "U D' R2 B")
        elif isinstance(sequence, str):
            return self.apply(list(Action(a) for a in sequence.split()))
        # handle a list of strings (e.g. ["U", "D'", "R2", "B"])
        elif isinstance(sequence[0], str):
            return self.apply(list(Action(a) for a in sequence))
        # handle a list of actions
        else:
            for action in sequence:
                self.rotate(action.face, action.k, action.layer)
            return self

    def is_solved(self):
        """
        :return: True if the cube is solved, False otherwise
        """
        return all(np.all(self._array[:, :, i] == self._array[0, 0, i])
                   for i in range(NUM_FACES))

    def get_face(self, face):
        """
        Get a 2d array of the chosen face
        :param face: a Face instance
        :return: NxN array of colors of the chosen face
        """
        assert isinstance(face, Face)
        return self._array[:, :, face.value].copy()

    def __str__(self):
        result = ''
        n = self.layers

        def row(arr):
            return ''.join(str(arr[i]) + ' ' for i in range(n))

        for i in range(n):
            result += ' '*(2*n + 1) + row(self._array[i, :, 1]) + '\n'
        result += '\n'
        for i in range(n):
            result += row(self._array[i, :, 4]) + ' ' + \
                row(self._array[i, :, 0]) + ' ' + \
                row(self._array[i, :, 2]) + ' ' + \
                row(self._array[i, :, 5]) + '\n'
        result += '\n'
        for i in range(n):
            result += ' '*(2*n + 1) + row(self._array[i, :, 3]) + '\n'
        return result

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return np.array_equal(self._array, other._array)
