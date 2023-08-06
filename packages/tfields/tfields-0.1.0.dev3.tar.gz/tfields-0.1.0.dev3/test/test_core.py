import tfields
import numpy as np
from sympy.abc import x, y
import unittest
from tempfile import NamedTemporaryFile


import sympy  # NOQA: F401

ATOL = 1e-8


class Base_Test(object):
    """
    Testing derivatives of Points3D
    """
    _inst = None

    def test_self_equality(self):
        """
        Test equality
        """
        self.assertTrue(self._inst.equal(self._inst))

    def test_cylinderTrafo(self):
        """
        Test coordinate transformations in circle
        """
        transformer = self._inst.copy()
        transformer.transform(tfields.bases.CYLINDER)
        self.assertTrue(self._inst.equal(transformer, atol=ATOL))
        if len(self._inst) > 0:
            self.assertFalse(np.array_equal(self._inst, transformer))

        transformer.transform(tfields.bases.CARTESIAN)
        self.assertTrue(self._inst.equal(transformer, atol=ATOL))

    def test_spericalTrafo(self):
        """
        Test coordinate transformations in circle
        """
        transformer = self._inst.copy()

        transformer.transform(tfields.bases.SPHERICAL)
        transformer.transform(tfields.bases.CARTESIAN)
        self.assertTrue(self._inst.equal(transformer, atol=ATOL))

    def test_basic_merge(self):
        merge_list = [self._inst.copy() for i in range(3)]
        merge_list[0].transform(tfields.bases.CARTESIAN)
        merge_list[1].transform(tfields.bases.CYLINDER)
        merge_list[2].transform(tfields.bases.SPHERICAL)
        obj = type(self._inst).merged(*merge_list)
        self.assertTrue(obj.coordSys == tfields.bases.CARTESIAN)
        for i in range(len(merge_list)):
            value = np.allclose(merge_list[0],
                                obj[i * len(self._inst): (i + 1) *
                                    len(self._inst)],
                                atol=ATOL)
            self.assertTrue(value)

        obj_cs = type(self._inst).merged(*merge_list, coordSys=tfields.bases.CYLINDER)
        for i in range(len(merge_list)):
            value = np.allclose(merge_list[1],
                                obj_cs[i * len(self._inst): (i + 1) *
                                       len(self._inst)],
                                atol=ATOL)
            self.assertTrue(value)

    def tearDown(self):
        del self._inst

"""
EMPTY TESTS
"""


class Tensors_Empty_Test(Base_Test, unittest.TestCase):
    def setUp(self):
        self._inst = tfields.Tensors([], dim=3)


class TensorFields_Empty_Test(Tensors_Empty_Test):
    def setUp(self):
        self._fields = []
        self._inst = tfields.TensorFields([], dim=3)

    def test_fields(self):
        # field is of type list
        self.assertTrue(isinstance(self._inst.fields, list))
        self.assertTrue(len(self._inst.fields) == len(self._fields))

        for field, target_field in zip(self._inst.fields, self._fields):
            self.assertTrue(np.array_equal(field, target_field))
            # fields are copied not reffered by a pointer
            self.assertFalse(field is target_field)
    

class TensorFields_Copy_Test(TensorFields_Empty_Test):
    def setUp(self):
        base = [(-5, 5, 11)] * 3
        self._fields = [tfields.Tensors.grid(*base, coordSys='cylinder'),
                        tfields.Tensors(range(11**3))]
        tensors = tfields.Tensors.grid(*base)
        self._inst = tfields.TensorFields(tensors, *self._fields)


class TensorMaps_Empty_Test(TensorFields_Empty_Test):
    def setUp(self):
        self._fields = []
        self._inst = tfields.TensorMaps([], dim=3)
        self._maps = []
        self._maps_fields = []

class TensorMaps_Copy_Test(TensorMaps_Empty_Test):
    def setUp(self):
        base = [(-1, 1, 3)] * 3
        tensors = tfields.Tensors.grid(*base)
        self._fields = [tfields.Tensors.grid(*base, coordSys='cylinder'),
                        tfields.Tensors(range(len(tensors)))]
        self._maps_tensors = [[[0, 0, 0],
                               [1, 2, 3],
                               [1, 5, 9]],
                              [[0, 4],
                               [1, 3]],
                              [[42]]]
        self._maps_fields = [[[42., 21., 11]],
                             [[3, 25]],
                             [[111]]]
        self._maps = [tfields.TensorFields(map_tensors,
                                           *map_fields) for map_tensors,
                      map_fields in zip(self._maps_tensors, self._maps_fields)]
        self._inst = tfields.TensorMaps(tensors, *self._fields,
                                        maps=self._maps)




if __name__ == '__main__':
    unittest.main()
