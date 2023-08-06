import tfields
import numpy as np
from sympy.abc import x, y

import unittest
from tempfile import NamedTemporaryFile


import sympy  # NOQA: F401


pi = np.pi
sqrt2 = np.sqrt(2)
sqrt3 = np.sqrt(3)


class Cylinder_Test(unittest.TestCase):
    def setUp(self):
        self.array = np.array([[0, 0, 0],
                               [1, 0, 0],
                               [1, 1, 0],
                               [0, 1, 0],
                               [-1, 1, 0],
                               [-1, 0, 0],
                               [-1, -1, 0],
                               [0, -1, 0],
                               [1, -1, 0],
                               [1, -1, -1]],
                              dtype=float)
        self.array_transformed = np.array([[0, 0, 0],
                                           [1, 0, 0],
                                           [sqrt2, pi * 1 / 4, 0],
                                           [1, pi * 1 / 2, 0],
                                           [sqrt2, pi * 3 / 4, 0],
                                           [1, pi * 2 / 2, 0],
                                           [sqrt2, -pi * 3 / 4, 0],
                                           [1, -np.pi * 1 / 2, 0],
                                           [sqrt2, -pi * 1 / 4, 0],
                                           [sqrt2, -pi * 1 / 4, -1]],
                                          dtype=float)

    def test_cylinderTrafo(self):
        """
        Test coordinate transformations in circle
        """
        transformed = np.copy(self.array)
        tfields.bases.transform(transformed,
                                tfields.bases.CARTESIAN,
                                tfields.bases.CYLINDER)
        self.assertTrue(np.allclose(self.array_transformed,
                                    transformed,
                                    atol=1e-8))
        tfields.bases.transform(transformed,
                                tfields.bases.CYLINDER,
                                tfields.bases.CARTESIAN)
        self.assertTrue(np.allclose(self.array,
                                    transformed,
                                    atol=1e-8))


class Spherical_Test(unittest.TestCase):
    def setUp(self):
        self.array = np.array([[0, 0, 0],
                               [0, 0, 1],
                               [0, 0, -1],

                               [1, 0, 1],
                               [1, 1, 1],
                               [0, 1, 1],
                               [-1, 1, 1],
                               [-1, 0, 1],
                               [-1, -1, 1],
                               [0, -1, 1],
                               [1, -1, 1],

                               [1, 0, 0],
                               [1, 1, 0],
                               [0, 1, 0],
                               [-1, 1, 0],
                               [-1, 0, 0],
                               [-1, -1, 0],
                               [0, -1, 0],
                               [1, -1, 0],

                               [1, 0, -1],
                               [1, 1, -1],
                               [0, 1, -1],
                               [-1, 1, -1],
                               [-1, 0, -1],
                               [-1, -1, -1],
                               [0, -1, -1],
                               [1, -1, -1]],
                              
                              dtype=float)
        self.array_transformed = np.array([[0, 0, 0],
                                           [1, 0, pi / 2],
                                           [1, 0, -pi / 2],

                                           [sqrt2, 0, pi / 4],
                                           [sqrt3, pi * 1 / 4,
                                            np.arcsin(1 / sqrt3)],
                                           [sqrt2, pi * 1 / 2, pi / 4],
                                           [sqrt3, pi * 3 / 4,
                                            np.arcsin(1 / sqrt3)],
                                           [sqrt2, pi * 2 / 2, pi / 4],
                                           [sqrt3, -pi * 3 / 4,
                                            np.arcsin(1 / sqrt3)],
                                           [sqrt2, -pi * 1 / 2, pi / 4],
                                           [sqrt3, -pi * 1 / 4,
                                            np.arcsin(1 / sqrt3)],

                                           [1, 0, 0],
                                           [sqrt2, pi * 1 / 4, 0],
                                           [1, pi * 1 / 2, 0],
                                           [sqrt2, pi * 3 / 4, 0],
                                           [1, pi * 2 / 2, 0],
                                           [sqrt2, -pi * 3 / 4, 0],
                                           [1, -pi * 1 / 2, 0],
                                           [sqrt2, -pi * 1 / 4, 0],

                                           [sqrt2, 0, -pi / 4],
                                           [sqrt3, pi * 1 / 4,
                                            np.arcsin(-1 / sqrt3)],
                                           [sqrt2, pi * 1 / 2, -pi / 4],
                                           [sqrt3, pi * 3 / 4,
                                            np.arcsin(-1 / sqrt3)],
                                           [sqrt2, pi * 2 / 2, -pi / 4],
                                           [sqrt3, -pi * 3 / 4,
                                            np.arcsin(-1 / sqrt3)],
                                           [sqrt2, -pi * 1 / 2, -pi / 4],
                                           [sqrt3, -pi * 1 / 4,
                                            np.arcsin(-1 / sqrt3)],
                                          ],
                                          
                                          dtype=float)

    def test_sphericalTrafo(self):
        """
        Test coordinate transformations in circle
        """
        transformed = np.copy(self.array)
        tfields.bases.transform(transformed,
                                tfields.bases.CARTESIAN,
                                tfields.bases.SPHERICAL)
        self.assertTrue(np.allclose(self.array_transformed, transformed,
                                    atol=1e-8))
        tfields.bases.transform(transformed,
                                tfields.bases.SPHERICAL,
                                tfields.bases.CARTESIAN)
        self.assertTrue(np.allclose(self.array,
                                    transformed,
                                    atol=1e-8))


if __name__ == '__main__':
    unittest.main()
