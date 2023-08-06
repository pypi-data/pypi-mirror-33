#!/usr/bin/env
# encoding: utf-8
"""
Author:     Daniel Boeckenhoff
Mail:       daniel.boeckenhoff@ipp.mpg.de

core of tfields library
contains numpy ndarray derived bases of the tfields package
"""
import warnings
import os
import pathlib
from six import string_types
from contextlib import contextmanager
from collections import Counter

import numpy as np
import sympy
import scipy as sp
import tfields.bases
np.seterr(all='warn', over='raise')


def rank(tensor):
    """
    Tensor rank
    """
    return len(tensor.shape) - 1


def dim(tensor):
    """
    Manifold dimension
    """
    if rank(tensor) == 0:
        return 1
    return tensor.shape[1]


class AbstractNdarray(np.ndarray):
    """
    All tensors and subclasses should derive from AbstractNdarray.
    AbstractNdarray implements all the inheritance specifics for np.ndarray
    Whene inheriting, three attributes are of interest:
        __slots__ (list of str): If you want to add attributes to
            your AbstractNdarray subclass, add the attribute name to __slots__
        __slot_defaults__ (list): if __slot_defaults__ is None, the
            defaults for the attributes in __slots__ will be None
            other values will be treaded as defaults to the corresponding
            arg at the same position in the __slots__ list.
        __slotDtype__ (list of types): for the conversion of the
            args in __slots__ to numpy arrays. None values mean no
            conversion.

    Args:
        array (array-like): input array
        **kwargs: arguments corresponding to __slots__
    TODO:
        equality check
    """
    __slots__ = []
    __slot_defaults__ = []
    __slotDtypes__ = []
    __slot_setters__ = []

    def __new__(cls, array, **kwargs):  # pragma: no cover
        raise NotImplementedError("{clsType} type must implement '__new__'"
                                  .format(clsType=type(cls)))

    def __array_finalize__(self, obj):
        if obj is None:
            return
        for attr in self._iter_slots():
            setattr(self, attr, getattr(obj, attr, None))

    def __array_wrap__(self, out_arr, context=None):
        return np.ndarray.__array_wrap__(self, out_arr, context)

    @classmethod
    def _iter_slots(cls):
        return [att for att in cls.__slots__ if att != '_cache']

    @classmethod
    def _update_slot_kwargs(cls, kwargs):
        """
        set the defaults in kwargs according to __slot_defaults__
        and convert the kwargs according to __slotDtypes__
        """
        slotDefaults = cls.__slot_defaults__ + \
            [None] * (len(cls.__slots__) - len(cls.__slot_defaults__))
        slotDtypes = cls.__slotDtypes__ + \
            [None] * (len(cls.__slots__) - len(cls.__slotDtypes__))
        for attr, default, dtype in zip(cls.__slots__, slotDefaults, slotDtypes):
            if attr == '_cache':
                continue
            if attr not in kwargs:
                kwargs[attr] = default
            if dtype is not None:
                try:
                    kwargs[attr] = np.array(kwargs[attr], dtype=dtype)
                except Exception as err:
                    raise ValueError(str(attr) + str(dtype) + str(kwargs[attr]) + str(err))

    def __setattr__(self, name, value):
        if name in self.__slots__:
            index = self.__slots__.index(name)
            try:
                setter = self.__slot_setters__[index]
            except IndexError:
                setter = None
            if setter is not None:
                value = setter(value)
        super(AbstractNdarray, self).__setattr__(name, value)

    def __reduce__(self):
        """
        important for pickling
        Examples:
            >>> from tempfile import NamedTemporaryFile
            >>> import pickle
            >>> import tfields

            Build a dummy scalar field
            >>> from tfields import Tensors, TensorFields
            >>> scalars = Tensors([0, 1, 2])
            >>> vectors = Tensors([[0, 0, 0], [0, 0, 1], [0, -1, 0]])
            >>> scalarField = TensorFields(vectors, scalars, coordSys='cylinder')

            Save it and restore it
            >>> outFile = NamedTemporaryFile(suffix='.pickle')

            >>> pickle.dump(scalarField,
            ...             outFile)
            >>> _ = outFile.seek(0)

            >>> sf = pickle.load(outFile)
            >>> sf.coordSys == 'cylinder'
            True
            >>> sf.fields[0][2] == 2.
            True

        """
        # Get the parent's __reduce__ tuple
        pickled_state = super(AbstractNdarray, self).__reduce__()

        # Create our own tuple to pass to __setstate__
        new_state = pickled_state[2] + tuple([getattr(self, slot) for slot in
                                              self._iter_slots()])

        # Return a tuple that replaces the parent's __setstate__ tuple with our own
        return (pickled_state[0], pickled_state[1], new_state)

    def __setstate__(self, state):
        """
        important for unpickling
        """
        # Call the parent's __setstate__ with the other tuple elements.
        super(AbstractNdarray, self).__setstate__(state[0:-len(self._iter_slots())])

        # set the __slot__ attributes
        for i, slot in enumerate(reversed(self._iter_slots())):
            index = -(i + 1)
            setattr(self, slot, state[index])

    def copy(self, *args, **kwargs):
        """
        The standard ndarray copy does not copy slots. Correct for this.
        Examples:
            >>> import tfields
            >>> m = tfields.TensorMaps([[1,2,3], [3,3,3], [0,0,0], [5,6,7]],
            ...                        maps=[tfields.TensorFields([[0, 1, 2], [1, 2, 3]],
            ...                                                   [1, 2])])
            >>> mc = m.copy()
            >>> mc is m
            False
            >>> mc.maps[0].fields[0] is m.maps[0].fields[0]
            False

        TODO: This function implementation could be more general or maybe redirect to deepcopy?
        """
        inst = super(AbstractNdarray, self).copy(*args, **kwargs)
        for attr in self._iter_slots():
            value = getattr(self, attr)
            if hasattr(value, 'copy'):
                setattr(inst, attr, value.copy(*args, **kwargs))
            elif isinstance(value, list):
                list_copy = []
                for item in value:
                    if hasattr(item, 'copy'):
                        list_copy.append(item.copy(*args, **kwargs))
                    else:
                        list_copy.append(item)
                setattr(inst, attr, list_copy)

        return inst

    def save(self, path, *args, **kwargs):
        """
        Saving a tensors object by redirecting to the correct save method depending on path
        Args:
            path (str or buffer)
            *args:
                forwarded to extension specific method
            **kwargs:
                extension (str): only needed if path is buffer
                ... remaining:forwarded to extension specific method
        """
        # get the extension
        if isinstance(path, string_types):
            extension = pathlib.Path(path).suffix.lstrip('.')

        # get the save method
        try:
            save_method = getattr(self,
                                  '_save_{extension}'.format(**locals()))
        except:
            raise NotImplementedError("Can not find save method for extension: "
                                      "{extension}.".format(**locals()))

        # resolve:     relative paths,  symlinks and    ~
        path = os.path.realpath(os.path.abspath(os.path.expanduser(path)))
        return save_method(path, **kwargs)

    @classmethod
    def load(cls, path, *args, **kwargs):
        """
        load a file as a tensors object.
        Args:
            path (str or buffer)
            *args:
                forwarded to extension specific method
            **kwargs:
                extension (str): only needed if path is buffer
                ... remaining:forwarded to extension specific method
        """
        extension = kwargs.pop('extension', 'npz')
        if isinstance(path, string_types):
            path = os.path.realpath(os.path.abspath(os.path.expanduser(path)))
            extension = pathlib.Path(path).suffix.lstrip('.')

        try:
            load_method = getattr(cls, '_load_{e}'.format(e=extension))
        except:
            raise NotImplementedError("Can not find load method for extension: "
                                      "{extension}.".format(**locals()))
        return load_method(path, *args, **kwargs)

    def _save_npz(self, path, **kwargs):
        """
        Args:
            path (open file or str/unicode): destination to save file to.
        Examples:
            >>> import tfields
            >>> from tempfile import NamedTemporaryFile
            >>> outFile = NamedTemporaryFile(suffix='.npz')
            >>> p = tfields.Points3D([[1., 2., 3.], [4., 5., 6.], [1, 2, -6]])
            >>> p.save(outFile.name)
            >>> _ = outFile.seek(0)
            >>> p1 = tfields.Points3D.load(outFile.name)
            >>> assert p.equal(p1)

        """
        kwargs = {}
        for attr in self._iter_slots():
            if not hasattr(self, attr):
                # attribute in __slots__ not found.
                warnings.warn("When saving instance of class {0} Attribute {1} not set."
                              "This Attribute is not saved.".format(self.__class__, attr), Warning)
            else:
                kwargs[attr] = getattr(self, attr)

        np.savez(path, self, **kwargs)

    @classmethod
    def _load_npz(cls, path, **load_kwargs):
        """
        Factory method
        Given a path to a npz file, construct the object
        """
        np_file = np.load(path, **load_kwargs)
        keys = np_file.keys()
        bulk = np_file['arr_0']
        data_kwargs = {key: np_file[key] for key in keys if key not in ['arr_0']}
        return cls.__new__(cls, bulk, **data_kwargs)


class Tensors(AbstractNdarray):
    """
    Set of tensors with the same basis.
    TODO:
        all slot args should be protected -> _base
    Args:
        tensors: np.ndarray or AbstractNdarray subclass
    Examples:
        >>> import numpy as np

        Initialize a scalar range
        >>> scalars = tfields.Tensors([0, 1, 2])
        >>> scalars.rank == 0
        True

        Initialize vectors
        >>> vectors = tfields.Tensors([[0, 0, 0], [0, 0, 1], [0, -1, 0]])
        >>> vectors.rank == 1
        True
        >>> vectors.dim == 3
        True
        >>> assert vectors.coordSys == 'cartesian'

        Initialize the Levi-Zivita Tensor
        >>> matrices = tfields.Tensors([[[0, 0, 0], [0, 0, 1], [0, -1, 0]],
        ...                     [[0, 0, -1], [0, 0, 0], [1, 0, 0]],
        ...                     [[0, 1, 0], [-1, 0, 0], [0, 0, 0]]])
        >>> matrices.shape == (3, 3, 3)
        True
        >>> matrices.rank == 2
        True
        >>> matrices.dim == 3
        True

        Initializing in different start coordinate system
        >>> cyl = tfields.Tensors([[5, np.arctan(4. / 3.), 42]], coordSys='cylinder')
        >>> assert cyl.coordSys == 'cylinder'
        >>> cyl.transform('cartesian')
        >>> assert cyl.coordSys == 'cartesian'
        >>> cart = cyl
        >>> assert round(cart[0, 0], 10) == 3.
        >>> assert round(cart[0, 1], 10) == 4.
        >>> assert cart[0, 2] == 42

        Initialize with copy constructor keeps the coordinate system
        >>> with vectors.tmp_transform('cylinder'):
        ...     vect_cyl = tfields.Tensors(vectors)
        ...     assert vect_cyl.coordSys == vectors.coordSys
        >>> assert vect_cyl.coordSys == 'cylinder'

        You can demand a special dimension.
        >>> _ = tfields.Tensors([[1, 2, 3]], dim=3)
        >>> _ = tfields.Tensors([[1, 2, 3]], dim=2)  # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        ValueError: Incorrect dimension: 3 given, 2 demanded.

        The dimension argument (dim) becomes necessary if you want to initialize
        an empty array
        >>> _ = tfields.Tensors([])  # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        ValueError: Empty tensors need dimension parameter 'dim'.
        >>> tfields.Tensors([], dim=7)
        Tensors([], shape=(0, 7), dtype=float64)

    """
    __slots__ = ['coordSys']
    __slot_defaults__ = ['cartesian']
    __slot_setters__ = [tfields.bases.get_coord_system_name]

    def __new__(cls, tensors, **kwargs):
        dtype = kwargs.pop('dtype', None)
        order = kwargs.pop('order', None)
        dim = kwargs.pop('dim', None)

        ''' copy constructor extracts the kwargs from tensors'''
        if issubclass(type(tensors), Tensors):
            if dim is not None:
                dim = tensors.dim
            coordSys = kwargs.pop('coordSys', tensors.coordSys)
            tensors = tensors.copy()
            tensors.transform(coordSys)
            kwargs['coordSys'] = coordSys
            if dtype is None:
                dtype = tensors.dtype
        else:
            if dtype is None:
                dtype = np.float64

        ''' demand iterable structure '''
        try:
            len(tensors)
        except TypeError as err:
            raise TypeError("Iterable structure necessary."
                            " Got {tensors}"
                            .format(**locals()))

        ''' process empty inputs '''
        if len(tensors) == 0:
            if issubclass(type(tensors), tfields.Tensors):
                tensors = np.empty(tensors.shape, dtype=tensors.dtype)
            elif dim is not None:
                tensors = np.empty((0, dim))
            if issubclass(type(tensors), np.ndarray):
                # np.empty
                pass
            else:
                raise ValueError("Empty tensors need dimension "
                                 "parameter 'dim'.")

        tensors = np.asarray(tensors, dtype=dtype, order=order)
        obj = tensors.view(cls)

        ''' check dimension(s) '''
        for d in obj.shape[1:]:
            if not d == obj.dim:
                raise ValueError("Dimensions are inconstistent. "
                                 "Manifold dimension is {obj.dim}, "
                                 "Found dimensions {found} in {obj}."
                                 .format(found=obj.shape[1:], **locals()))
        if dim is not None:
            if dim != obj.dim:
                raise ValueError("Incorrect dimension: {obj.dim} given,"
                                 " {dim} demanded."
                                 .format(**locals()))

        ''' update kwargs with defaults from slots '''
        cls._update_slot_kwargs(kwargs)

        ''' set kwargs to slots attributes '''
        for attr in kwargs:
            if attr not in cls._iter_slots():
                raise AttributeError("Keyword argument {attr} not accepted "
                                     "for class {cls}".format(**locals()))
            setattr(obj, attr, kwargs[attr])

        return obj

    @classmethod
    def merged(cls, *objects, **kwargs):
        """
        Factory method
        Merges all tensor inputs to one tensor

        Examples:
            >>> import numpy as np
            >>> import tfields
            >>> import tfields.bases

            Use of most frequent coordinate system
            >>> vec_a = tfields.Tensors([[0, 0, 0], [0, 0, 1], [0, -1, 0]])
            >>> vec_b = tfields.Tensors([[5, 4, 1]], coordSys=tfields.bases.cylinder)
            >>> vec_c = tfields.Tensors([[4, 2, 3]], coordSys=tfields.bases.cylinder)
            >>> merge = tfields.Tensors.merged(vec_a, vec_b, vec_c, [[2, 0, 1]])
            >>> assert merge.coordSys == 'cylinder'
            >>> assert merge.equal([[0, 0, 0],
            ...                     [0, 0, 1],
            ...                     [1, -np.pi / 2, 0],
            ...                     [5, 4, 1],
            ...                     [4, 2, 3],
            ...                     [2, 0, 1]])

            Merge also shifts the maps to still refer to the same tensors
            >>> tm_a = tfields.TensorMaps(merge, maps=[[[0, 1, 2]]])
            >>> tm_b = tm_a.copy()
            >>> assert tm_a.coordSys == 'cylinder'
            >>> tm_merge = tfields.TensorMaps.merged(tm_a, tm_b)
            >>> assert tm_merge.coordSys == 'cylinder'
            >>> assert tm_merge.maps[0].equal([[0, 1, 2],
            ...                               list(range(len(merge),
            ...                                          len(merge) + 3,
            ...                                          1))])
            
            >>> obj_list = [tfields.Tensors([[1, 2, 3]], coordSys=tfields.bases.CYLINDER),
            ...             tfields.Tensors([[3] * 3]),
            ...             tfields.Tensors([[5, 1, 3]])]
            >>> merge2 = tfields.Tensors.merged(*obj_list, coordSys=tfields.bases.CARTESIAN)
            >>> assert merge2.equal([[-0.41614684, 0.90929743, 3.],
            ...                      [3, 3, 3], [5, 1, 3]], atol=1e-8)

        """

        ''' get most frequent coordSys or predefined coordSys '''
        coordSys = kwargs.get('coordSys', None)
        dimension = kwargs.get('dim', None)
        if coordSys is None:
            bases = []
            for t in objects:
                try:
                    bases.append(t.coordSys)
                except AttributeError:
                    pass
            if bases:
                # get most frequent coordSys
                coordSys = sorted(bases, key=Counter(bases).get, reverse=True)[0]
                kwargs['coordSys'] = coordSys
            else:
                default = cls.__slot_defaults__[cls.__slots__.index('coordSys')]
                kwargs['coordSys'] = default

        ''' transform all raw inputs to cls type with correct coordSys. Also
        automatically make a copy of those instances that are of the correct
        type already.'''
        objects = [cls(t, **kwargs) for t in objects]

        ''' check rank and dimension equality '''
        if not len(set([t.rank for t in objects])) == 1:
            raise TypeError("Tensors must have the same rank for merging.")
        if not len(set([t.dim for t in objects])) == 1:
            raise TypeError("Tensors must have the same dimension for merging.")

        ''' merge all objects '''
        remainingObjects = objects[1:] or []
        tensors = objects[0]

        for i, obj in enumerate(remainingObjects):
            tensors = np.append(tensors, obj, axis=0)

        if len(tensors) == 0 and dimension is None:
            for obj in objects:
                kwargs['dim'] = dim(obj)

        return cls.__new__(cls, tensors, **kwargs)

    @classmethod
    def grid(cls, *base_vectors, **kwargs):
        """
        Args:
            baseVector 0 (list/np.array of base coordinates)
            baseVector 1 (list/np.array of base coordinates)
            baseVector 2 (list/np.array of base coordinates)
        Kwargs:
            iter_order (list): order in which the iteration will be done.
                Frequency rises with position in list. default is [0, 1, 2]
                iteration will be done like::
                      
                for v0 in base_vectors[iter_order[0]]:
                    for v1 in base_vectors[iter_order[1]]:
                        for v2 in base_vectors[iter_order[2]]:
                            coords0.append(locals()['v%i' % iter_order[0]])
                            coords1.append(locals()['v%i' % iter_order[1]])
                            coords2.append(locals()['v%i' % iter_order[2]])

        Examples:
            Initilaize using the mgrid notation
            >>> import tfields
            >>> mgrid = tfields.Tensors.grid((0, 1, 2j), (3, 4, 2j), (6, 7, 2j))
            >>> mgrid.equal([[0, 3, 6],
            ...              [0, 3, 7],
            ...              [0, 4, 6],
            ...              [0, 4, 7],
            ...              [1, 3, 6],
            ...              [1, 3, 7],
            ...              [1, 4, 6],
            ...              [1, 4, 7]])
            True
            >>> lins = tfields.Tensors.grid(np.linspace(3, 4, 2), np.linspace(0, 1, 2),
            ...                             np.linspace(6, 7, 2), iter_order=[1, 0, 2])
            >>> lins.equal([[3, 0, 6],
            ...             [3, 0, 7],
            ...             [4, 0, 6],
            ...             [4, 0, 7],
            ...             [3, 1, 6],
            ...             [3, 1, 7],
            ...             [4, 1, 6],
            ...             [4, 1, 7]])
            True
            >>> lins2 = tfields.Tensors.grid(np.linspace(0, 1, 2),
            ...                              np.linspace(3, 4, 2),
            ...                              np.linspace(6, 7, 2),
            ...                              iter_order=[2, 0, 1])
            >>> lins2.equal([[0, 3, 6],
            ...              [0, 4, 6],
            ...              [1, 3, 6],
            ...              [1, 4, 6],
            ...              [0, 3, 7],
            ...              [0, 4, 7],
            ...              [1, 3, 7],
            ...              [1, 4, 7]])
            True

        """
        inst = cls.__new__(cls, tfields.lib.grid.igrid(*base_vectors, **kwargs))
        return inst

    @property
    def rank(self):
        """
        Tensor rank
        """
        return rank(self)

    @property
    def dim(self):
        """
        Manifold dimension
        """
        return dim(self)

    def transform(self, coordSys):
        """
        Args:
            coordSys (str)

        Examples:
            >>> import numpy as np
            >>> import tfields

            CARTESIAN to SPHERICAL
            >>> t = tfields.Tensors([[1, 2, 2], [1, 0, 0], [0, 0, -1], [0, 0, 1], [0, 0, 0]])
            >>> t.transform('spherical')

            r
            >>> assert t[0, 0] == 3

            phi
            >>> assert t[1, 1] == 0.
            >>> assert t[2, 1] == 0.

            theta is 0 at (0, 0, 1) and pi / 2 at (0, 0, -1)
            >>> assert round(t[1, 2], 10) == round(0, 10)
            >>> assert t[2, 2] == -np.pi / 2
            >>> assert t[3, 2] == np.pi / 2

            theta is defined 0 for R == 0
            >>> assert t[4, 0] == 0.
            >>> assert t[4, 2] == 0.


            CARTESIAN to CYLINDER
            >>> tCart = tfields.Tensors([[3, 4, 42], [1, 0, 0], [0, 1, -1], [-1, 0, 1], [0, 0, 0]])
            >>> t_cyl = tCart.copy()
            >>> t_cyl.transform('cylinder')
            >>> assert t_cyl.coordSys == 'cylinder'

            R
            >>> assert t_cyl[0, 0] == 5
            >>> assert t_cyl[1, 0] == 1
            >>> assert t_cyl[2, 0] == 1
            >>> assert t_cyl[4, 0] == 0

            Phi
            >>> assert round(t_cyl[0, 1], 10) == round(np.arctan(4. / 3), 10)
            >>> assert t_cyl[1, 1] == 0
            >>> assert round(t_cyl[2, 1], 10) == round(np.pi / 2, 10)
            >>> assert t_cyl[1, 1] == 0

            Z
            >>> assert t_cyl[0, 2] == 42
            >>> assert t_cyl[2, 2] == -1

            >>> t_cyl.transform('cartesian')
            >>> assert t_cyl.coordSys == 'cartesian'
            >>> assert t_cyl[0, 0] == 3

        """
        #           scalars                 empty             already there
        if self.rank == 0 or self.shape[0] == 0 or self.coordSys == coordSys:
            self.coordSys = coordSys
            return

        tfields.bases.transform(self, self.coordSys, coordSys)
        # self[:] = tfields.bases.transform(self, self.coordSys, coordSys)
        self.coordSys = coordSys

    @contextmanager
    def tmp_transform(self, coordSys):
        """
        Temporarily change the coordSys to another coordSys and change it back at exit
        This method is for cleaner code only.
        No speed improvements go with this.
        Args:
            see transform
        Examples:
            >>> import tfields
            >>> p = tfields.Tensors([[1,2,3]], coordSys=tfields.bases.SPHERICAL)
            >>> with p.tmp_transform(tfields.bases.CYLINDER):
            ...     assert p.coordSys == tfields.bases.CYLINDER
            >>> assert p.coordSys == tfields.bases.SPHERICAL

        """
        baseBefore = self.coordSys
        if baseBefore == coordSys:
            yield
        else:
            self.transform(coordSys)

            yield

            self.transform(baseBefore)

    def mirror(self, coordinate, condition=None):
        """
        Reflect/Mirror the entries meeting <condition> at <coordinate> = 0
        Args:
            coordinate (int): coordinate index
        Examples:
            >>> import tfields
            >>> p = tfields.Tensors([[1., 2., 3.], [4., 5., 6.], [1, 2, -6]])
            >>> p.mirror(1)
            >>> assert p.equal([[1, -2, 3], [4, -5,  6], [1, -2, -6]])

            multiple coordinates can be mirrored. Eg. a point mirrorion would be
            >>> p = tfields.Tensors([[1., 2., 3.], [4., 5., 6.], [1, 2, -6]])
            >>> p.mirror([0,2])
            >>> assert p.equal([[-1, 2, -3], [-4, 5, -6], [-1, 2., 6.]])

            You can give a condition as mask or as str.
            The mirroring will only be applied to the points meeting the condition.
            >>> import sympy
            >>> x, y, z = sympy.symbols('x y z')
            >>> p.mirror([0,2], y > 3)
            >>> p.equal([[-1, 2, -3], [4, 5, 6], [-1, 2, 6]])
            True

        """
        if condition is None:
            condition = np.array([True for i in range(len(self))])
        elif isinstance(condition, sympy.Basic):
            condition = self.evalf(condition)
        if isinstance(coordinate, list) or isinstance(coordinate, tuple):
            for c in coordinate:
                self.mirror(c, condition)
        elif isinstance(coordinate, int):
            self[:, coordinate][condition] *= -1
        else:
            raise TypeError()

    def to_segment(self, segment, num_segments, coordinate,
                   periodicity=2 * np.pi, offset=0,
                   coordSys=None):
        """
        For circular (close into themself after
        <periodicity>) coordinates at index <coordinate> assume
        <num_segments> segments and transform all values to
        segment number <segment>
        Examples:
            >>> import tfields
            >>> import numpy as np
            >>> pStart = tfields.Points3D([[6, 2 * np.pi, 1],
            ...                            [6, 2 * np.pi / 5 * 3, 1]],
            ...                           coordSys='cylinder')
            >>> p = tfields.Points3D(pStart)
            >>> p.to_segment(0, 5, 1, offset=-2 * np.pi / 10)
            >>> assert np.array_equal(p[:, 1], [0, 0])

            >>> p2 = tfields.Points3D(pStart)
            >>> p2.to_segment(1, 5, 1, offset=-2 * np.pi / 10)
            >>> assert np.array_equal(np.round(p2[:, 1], 4), [1.2566] * 2)

        """
        if segment > num_segments - 1:
            raise ValueError("Segment {0} not existent.".format(segment))

        if coordSys is None:
            coordSys = self.coordSys
        with self.tmp_transform(coordSys):
            # map all values to first segment
            self[:, coordinate] = \
                (self[:, coordinate] - offset) % (periodicity / num_segments) + \
                offset + segment * periodicity / num_segments

    def equal(self, other,
              rtol=None, atol=None, equal_nan=False,
              return_bool=True):
        """
        Evaluate, whether the instance has the same content as other.
        Args:
            optional:
                rtol (float)
                atol (float)
                equal_nan (bool)
            see numpy.isclose
        """
        if issubclass(type(other), Tensors) and self.coordSys != other.coordSys:
            other = other.copy()
            other.transform(self.coordSys)
        x, y = np.asarray(self), np.asarray(other)
        if rtol is None and atol is None:
            mask = (x == y)
            if equal_nan:
                both_nan = np.isnan(x) & np.isnan(y)
                mask[both_nan] = both_nan[both_nan]
        else:
            if rtol is None:
                rtol = 0.
            if atol is None:
                atol = 0.
            mask = np.isclose(x, y, rtol=rtol, atol=atol, equal_nan=equal_nan)
        if return_bool:
            return bool(np.all(mask))
        return mask

    def contains(self, other, **kwargs):
        """
        Inspired by a speed argument @
        stackoverflow.com/questions/14766194/testing-whether-a-numpy-array-contains-a-given-row
        Examples:
            >>> import tfields
            >>> p = tfields.Tensors([[1,2,3], [4,5,6], [6,7,8]])
            >>> p.contains([4,5,6])
            True

        """
        return any(self.equal(other, return_bool=False).all(1))

    def indices(self, tensor):
        """
        Returns:
            list of int: indices of tensor occuring
        """
        indices = []
        for i, p in enumerate(self):
            if all(p == tensor):
                indices.append(i)
        return indices

    def index(self, tensor):
        """
        Args:
            tensor
        Returns:
            int: index of tensor occuring
        """
        indices = self.indices(tensor)
        if not indices:
            return None
        if len(indices) == 1:
            return indices[0]
        raise ValueError("Multiple occurences of value {}"
                         .format(tensor))

    def moments(self, moment):
        """
        Returns:
            Moments of the distribution.
        Note:
            The first moment is given as the mean,
            second as variance etc. Not 0 as it is mathematicaly correct.
        Args:
            moment (int): n-th moment
        """
        return tfields.lib.stats.moments(self, moment)

    def closest(self, other, **kwargs):
        """
        Args:
            other (Tensors): closest points to what? -> other
            **kwargs: forwarded to scipy.spatial.cKDTree.query
        Returns:
            array shape(len(self)): Indices of other points that are closest to own points
        Examples:
            >>> import tfields
            >>> m = tfields.Tensors([[1,0,0], [0,1,0], [1,1,0], [0,0,1],
            ...                      [1,0,1]])
            >>> p = tfields.Tensors([[1.1,1,0], [0,0.1,1], [1,0,1.1]])
            >>> p.closest(m)
            array([2, 3, 4])

        """
        with other.tmp_transform(self.coordSys):
            # balanced_tree option gives huge speedup!
            kd_tree = sp.spatial.cKDTree(other, 1000,
                                         balanced_tree=False)
            res = kd_tree.query(self, **kwargs)
            array = res[1]

        return array

    def evalf(self, expression=None, coordSys=None):
        """
        Args:
            expression (sympy logical expression)
            coordSys (str): coordSys to evalfuate the expression in.
        Returns:
            np.ndarray: mask of dtype bool with lenght of number of points in self.
                 This array is True, where expression evalfuates True.
        Examples:
            >>> import tfields
            >>> import numpy
            >>> import sympy
            >>> x, y, z = sympy.symbols('x y z')
            >>> p = tfields.Tensors([[1., 2., 3.], [4., 5., 6.], [1, 2, -6],
            ...                      [-5, -5, -5], [1,0,-1], [0,1,-1]])
            >>> np.array_equal(p.evalf(x > 0),
            ...                [True, True, True, False, True, False])
            True
            >>> np.array_equal(p.evalf(x >= 0),
            ...                [True, True, True, False, True, True])
            True

            And combination
            >>> np.array_equal(p.evalf((x > 0) & (y < 3)),
            ...                [True, False, True, False, True, False])
            True

            Or combination
            >>> np.array_equal(p.evalf((x > 0) | (y > 3)),
            ...                [True, True, True, False, True, False])
            True

        """
        coords = sympy.symbols('x y z')
        with self.tmp_transform(coordSys or self.coordSys):
            mask = tfields.evalf(self, expression, coords=coords)
        return mask

    def cut(self, expression, coordSys=None):
        """
        Default cut method for Points3D. Works on a copy.
        Args:
            expression (sympy logical expression): logical expression which will be evalfuated.
                             use symbols x, y and z
            coordSys (str): coordSys to evalfuate the expression in.
        Examples:
            >>> import tfields
            >>> import sympy
            >>> x, y, z = sympy.symbols('x y z')
            >>> p = tfields.Tensors([[1., 2., 3.], [4., 5., 6.], [1, 2, -6],
            ...                      [-5, -5, -5], [1,0,-1], [0,1,-1]])
            >>> p.cut(x > 0).equal([[1, 2, 3],
            ...                     [4, 5, 6],
            ...                     [1, 2, -6],
            ...                     [1, 0, -1]])
            True

            combinations of cuts
            >>> p.cut((x > 0) & (z < 0)).equal([[1, 2, -6], [1, 0, -1]])
            True

        Returns:
            copy of self with cut applied

        """
        if len(self) == 0:
            return self.copy()
        mask = self.evalf(expression, coordSys=coordSys or self.coordSys)
        mask.astype(bool)
        inst = self[mask].copy()
        return inst

    def distances(self, other, **kwargs):
        """
        Args:
            other(array)
            **kwargs:
                ... is forwarded to sp.spatial.distance.cdist
        Examples:
            >>> import tfields
            >>> p = tfields.Tensors.grid((0, 2, 3j),
            ...                          (0, 2, 3j),
            ...                          (0, 0, 1j))
            >>> p[4,2] = 1
            >>> p.distances(p)[0,0]
            0.0
            >>> p.distances(p)[5,1]
            1.4142135623730951
            >>> p.distances([[0,1,2]])[-1][0] == 3
            True

        """
        if issubclass(type(other), Tensors) and self.coordSys != other.coordSys:
            other = other.copy()
            other.transform(self.coordSys)
        return sp.spatial.distance.cdist(self, other, **kwargs)

    def min_dists(self, other=None, **kwargs):
        """
        Args:
            other(array | None): if None: closest distance to self
            **kwargs:
                memory_saving (bool): for very large array comparisons
                    default False
                ... rest is forwarded to sp.spatial.distance.cdist

        Returns:
            np.array: minimal distances of self to other


        Examples:
            >>> import tfields
            >>> import numpy as np
            >>> p = tfields.Tensors.grid((0, 2, 3),
            ...                          (0, 2, 3),
            ...                          (0, 0, 1))
            >>> p[4,2] = 1
            >>> dMin = p.min_dists()
            >>> expected = [1] * 9
            >>> expected[4] = np.sqrt(2)
            >>> np.array_equal(dMin, expected)
            True

            >>> dMin2 = p.min_dists(memory_saving=True)
            >>> bool((dMin2 == dMin).all())
            True

        """
        memory_saving = kwargs.pop('memory_saving', False)

        if other is None:
            other = self
        else:
            raise NotImplementedError("Should be easy but make shure not to remove diagonal")

        try:
            if memory_saving:
                raise MemoryError()
            d = self.distances(other, **kwargs)
            return d[d > 0].reshape(d.shape[0], - 1).min(axis=1)
        except MemoryError:
            min_dists = np.empty(self.shape[0])
            for i, point in enumerate(other):
                d = self.distances([point], **kwargs)
                min_dists[i] = d[d > 0].reshape(-1).min()
            return min_dists

    def epsilon_neighbourhood(self, epsilon):
        """
        Returns:
            indices for those sets of points that lie within epsilon around the other
        Examples:
            Create mesh grid with one extra point that will have 8 neighbours
            within epsilon
            >>> import tfields
            >>> p = tfields.Tensors.grid((0, 1, 2j),
            ...                          (0, 1, 2j),
            ...                          (0, 1, 2j))
            >>> p = tfields.Tensors.merged(p, [[0.5, 0.5, 0.5]])
            >>> [len(en) for en in p.epsilon_neighbourhood(0.9)]
            [2, 2, 2, 2, 2, 2, 2, 2, 9]

        """
        indices = np.arange(self.shape[0])
        dists = self.distances(self)
        distsInEpsilon = dists <= epsilon
        return [indices[die] for die in distsInEpsilon]

    def _weights(self, weights, rigid=True):
        """
        transformer method for weights inputs.
        Args:
            weights (np.ndarray | None):
                If weights is None, use np.ones
                Otherwise just pass the weights.
            rigid (bool): demand equal weights and tensor length
        Returns:
            weight array
        """
        # set weights to 1.0 if weights is None
        if weights is None:
            weights = np.ones(len(self))
        if rigid:
            if not len(weights) == len(self):
                raise ValueError("Equal number of weights as tensors demanded.")
        return weights

    def cov_eig(self, weights=None):
        """
        Calculate the covariance eigenvectors with lenghts of eigenvalues
        Args:
            weights (np.array | int | None): index to scalars to weight with
        """
        # weights = self.getNormedWeightedAreas(weights=weights)
        weights = self._weights(weights)
        cov = np.cov(self.T,
                     ddof=0,
                     aweights=weights)
        # calculate eigenvalues and eigenvectors of covariance
        evalfs, evecs = np.linalg.eigh(cov)
        idx = evalfs.argsort()[::-1]
        evalfs = evalfs[idx]
        evecs = evecs[:, idx]
        e = np.concatenate((evecs, evalfs.reshape(1, 3)))
        return e.T.reshape(12, )

    def main_axes(self, weights=None):
        """
        Returns:
            Main Axes eigen-vectors
        """
        # weights = self.getNormedWeightedAreas(weights=weights)
        weights = self._weights(weights)
        mean = self.moments(1)
        relative_coords = self - mean
        cov = np.cov(relative_coords.T,
                     ddof=0,
                     aweights=weights)
        # calculate eigenvalues and eigenvectors of covariance
        evalfs, evecs = np.linalg.eigh(cov)
        return (evecs * evalfs.T).T


class TensorFields(Tensors):
    """
    Discrete Tensor Field

    Args:
        tensors (array): base tensors
        *fields (array): multiple fields assigned to one base tensor. Fields
            themself are also of type tensor
        **kwargs:
            rigid (bool): demand equal field and tensor lenght
            ... : see tfields.Tensors

    Examples:
        >>> from tfields import Tensors, TensorFields
        >>> scalars = Tensors([0, 1, 2])
        >>> vectors = Tensors([[0, 0, 0], [0, 0, 1], [0, -1, 0]])
        >>> scalarField = TensorFields(vectors, scalars)
        >>> scalarField.rank
        1
        >>> scalarField.fields[0].rank
        0
        >>> vectorField = TensorFields(vectors, vectors)
        >>> vectorField.fields[0].rank
        1
        >>> vectorField.fields[0].dim
        3
        >>> multiField = TensorFields(vectors, scalars, vectors)
        >>> multiField.fields[0].dim
        1
        >>> multiField.fields[1].dim
        3

        Empty initialization
        >>> empty_field = TensorFields([], dim=3)
        >>> assert empty_field.shape == (0, 3)
        >>> assert empty_field.fields == []

        Directly initializing with lists or arrays
        >>> vec_field_raw = tfields.TensorFields([[0, 1, 2], [3, 4, 5]],
        ...                                       [1, 6], [2, 7])
        >>> assert len(vec_field_raw.fields) == 2

        Copying
        >>> cp = TensorFields(vectorField)
        >>> assert vectorField.equal(cp)

        Copying takes care of coordSys
        >>> cp.transform(tfields.bases.CYLINDER)
        >>> cp_cyl = TensorFields(cp)
        >>> assert cp_cyl.coordSys == tfields.bases.CYLINDER

        Copying with changing type
        >>> tcp = TensorFields(vectorField, dtype=int)
        >>> assert vectorField.equal(tcp)
        >>> assert tcp.dtype == int

    Raises:
        TypeError:
        >>> import tfields
        >>> tfields.TensorFields([1, 2, 3], [3])  # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        ValueError: Length of base (3) should be the same as the length of all fields ([1]).

        This error can be suppressed by setting rigid=False
        >>> loose = tfields.TensorFields([1, 2, 3], [3], rigid=False)
        >>> assert len(loose) != 1

    """
    __slots__ = ['coordSys', 'fields']

    def __new__(cls, tensors, *fields, **kwargs):
        rigid = kwargs.pop('rigid', True)

        obj = super(TensorFields, cls).__new__(cls, tensors, **kwargs)
        if issubclass(type(tensors), TensorFields):
            if tensors.fields is None:
                raise ValueError("Tensor fields were None")
            obj.fields = [Tensors(field) for field in tensors.fields]
        elif not fields:
            obj.fields = []
        if fields:
            # (over)write fields
            obj.fields = [Tensors(field) for field in fields]

        if rigid:
            olen = len(obj)
            field_lengths = [len(f) for f in obj.fields]
            if not all([flen == olen for flen in field_lengths]):
                raise ValueError("Length of base ({olen}) should be the same as"
                                 " the length of all fields ({field_lengths})."
                                 .format(**locals()))
        return obj

    def __getitem__(self, index):
        """
        In addition to the usual, also slice fields
        Examples:
            >>> import tfields
            >>> import numpy as np
            >>> vectors = tfields.Tensors([[0, 0, 0], [0, 0, 1], [0, -1, 0]])
            >>> scalarField = tfields.TensorFields(vectors, [42, 21, 10.5], [1, 2, 3])

            Slicing
            >>> sliced = scalarField[2:]
            >>> assert isinstance(sliced, tfields.TensorFields)
            >>> assert isinstance(sliced.fields[0], tfields.Tensors)
            >>> assert sliced.fields[0].equal([10.5])

            Picking
            >>> picked = scalarField[1]
            >>> assert np.array_equal(picked, [0, 0, 1])

            Masking
            >>> masked = scalarField[[True, False, True]]
            >>> assert masked.equal([[0, 0, 0], [0, -1, 0]])
            >>> assert masked.fields[0].equal([42, 10.5])
            >>> assert masked.fields[1].equal([1, 3])

            Iteration
            >>> _ = [point for point in scalarField]

        """
        item = super(TensorFields, self).__getitem__(index)
        try:
            if issubclass(type(item), TensorFields):
                if isinstance(index, tuple):
                    index = index[0]
                if item.fields:
                    item.fields = [field.__getitem__(index) for field in item.fields]
        except IndexError as err:
            warnings.warn("Index error occured for field.__getitem__. Error "
                          "message: {err}".format(**locals()))

        return item

    def __setitem__(self, index, item):
        """
        In addition to the usual, also slice fields
        Examples:
            >>> import tfields
            >>> import numpy as np
            >>> original = tfields.TensorFields([[0, 0, 0], [0, 0, 1], [0, -1, 0]],
            ...                                  [42, 21, 10.5], [1, 2, 3])
            >>> obj = tfields.TensorFields([[0, 0, 0], [0, 0, np.nan], [0, -1, 0]],
            ...                             [42, 22, 10.5], [1, -1, 3])
            >>> slice_obj = obj.copy()
            >>> assert not obj.equal(original)
            >>> obj[1] = original[1]
            >>> assert obj[:2].equal(original[:2])

            >>> assert not slice_obj.equal(original)
            >>> slice_obj[:] = original[:]
            >>> assert slice_obj.equal(original)

        """
        super(TensorFields, self).__setitem__(index, item)
        if issubclass(type(item), TensorFields):
            if isinstance(index, slice):
                for i, field in enumerate(item.fields):
                    self.fields[i].__setitem__(index, field)
            elif isinstance(index, tuple):
                for i, field in enumerate(item.fields):
                    self.fields[i].__setitem__(index[0], field)
            else:
                for i, field in enumerate(item.fields):
                    self.fields[i].__setitem__(index, field)

    @classmethod
    def merged(cls, *objects, **kwargs):
        if not all([isinstance(o, cls) for o in objects]):
            # TODO: could allow if all faceScalars are none
            raise TypeError("Merge constructor only accepts {cls} instances."
                            .format(**locals()))

        inst = super(TensorFields, cls).merged(*objects, **kwargs)
        
        fields = []
        if all([len(obj.fields) == len(objects[0].fields)
                for obj in objects]):
            for fld_idx in range(len(objects[0].fields)):
                field = tfields.Tensors.merged(*[obj.fields[fld_idx]
                                                 for obj in objects])
                fields.append(field)
        inst = cls.__new__(cls, inst, *fields)
        return inst

    def transform(self, coordSys):
        super(TensorFields, self).transform(coordSys)
        for field in self.fields:
            field.transform(coordSys)

    def equal(self, other, **kwargs):
        """
        Test, whether the instance has the same content as other.
        Args:
            other (iterable)
            optional:
                see Tensors.equal
        """
        if not issubclass(type(other), Tensors):
            return super(TensorFields, self).equal(other, **kwargs)
        else:
            with other.tmp_transform(self.coordSys):
                mask = super(TensorFields, self).equal(other, **kwargs)
                if issubclass(type(other), TensorFields):
                    if len(self.fields) != len(other.fields):
                        mask &= False
                    else:
                        for i, field in enumerate(self.fields):
                            mask &= field.equal(other.fields[i], **kwargs)
                return mask

    def _weights(self, weights, rigid=True):
        """
        Expansion of Tensors._weights with integer inputs
        Args:
            weights (np.ndarray | int | None):
                if weights is int: use field at index <weights>
                else: see Tensors._weights
        """
        if isinstance(weights, int):
            weights = self.fields[weights]
        return super(TensorFields, self)._weights(weights, rigid=rigid)


class TensorMaps(TensorFields):
    """
    Args:
        tensors: see Tensors class
        *fields (Tensors): see TensorFields class
        **kwargs:
            coordSys ('str'): see Tensors class
            maps (array-like): indices indicating a connection between the
                tensors at the respective index positions
    Examples:
        >>> import tfields
        >>> import numpy as np
        >>> scalars = tfields.Tensors([0, 1, 2])
        >>> vectors = tfields.Tensors([[0, 0, 0], [0, 0, 1], [0, -1, 0]])
        >>> maps = [tfields.TensorFields([[0, 1, 2], [0, 1, 2]], [42, 21]),
        ...         tfields.TensorFields([[1], [2]], [-42, -21])]
        >>> mesh = tfields.TensorMaps(vectors, scalars,
        ...                           maps=maps)
        >>> assert isinstance(mesh.maps, list)
        >>> assert len(mesh.maps) == 2

        >>> assert mesh.equal(tfields.TensorFields(vectors, scalars))
        >>> assert mesh.maps[0].fields[0].equal(maps[0].fields[0])

        Copy constructor
        >>> mesh_copy = tfields.TensorMaps(mesh)

        Copying takes care of coordSys
        >>> mesh_copy.transform(tfields.bases.CYLINDER)
        >>> mesh_cp_cyl = tfields.TensorMaps(mesh_copy)
        >>> assert mesh_cp_cyl.coordSys == tfields.bases.CYLINDER

    Raises:
        >>> import tfields
        >>> tfields.TensorMaps([1] * 4, dim=3, maps=[[1, 2, 3]])  # +doctest: ELLIPSIS
        Traceback (most recent call last):
        ...
        ValueError: Incorrect map rank 0

    """
    __slots__ = ['coordSys', 'fields', 'maps']

    def __new__(cls, tensors, *fields, **kwargs):
        maps = kwargs.pop('maps', [])
        maps_cp = []
        for mp in maps:
            mp = TensorFields(mp, dtype=int)
            if not mp.rank == 1:
                raise ValueError("Incorrect map rank {mp.rank}"
                                 .format(**locals()))
            maps_cp.append(mp)
        maps = maps_cp
        obj = super(TensorMaps, cls).__new__(cls, tensors, *fields, **kwargs)
        obj.maps = maps
        return obj

    def __getitem__(self, index):
        """
        In addition to the usual, also slice fields

        Examples:
            >>> import tfields
            >>> import numpy as np
            >>> vectors = tfields.Tensors([[0, 0, 0], [0, 0, 1], [0, -1, 0],
            ...                            [1, 1, 1], [-1, -1, -1]])
            >>> maps=[tfields.TensorFields([[0, 1, 2], [0, 1, 3], [2, 3, 4]],
            ...                            [[1, 2], [3, 4], [5, 6]]),
            ...       tfields.TensorFields([[0], [1], [2], [3], [4]])]
            >>> mesh = tfields.TensorMaps(vectors,
            ...                           [42, 21, 10.5, 1, 1],
            ...                           [1, 2, 3, 3, 3],
            ...                           maps=maps)

            Slicing
            >>> sliced = mesh[2:]
            >>> assert isinstance(sliced, tfields.TensorMaps)
            >>> assert isinstance(sliced.fields[0], tfields.Tensors)
            >>> assert isinstance(sliced.maps[0], tfields.TensorFields)
            >>> assert sliced.fields[0].equal([10.5, 1, 1])
            >>> assert sliced.maps[0].equal([[0, 1, 2]])
            >>> assert sliced.maps[0].fields[0].equal([[5, 6]])

            Picking
            >>> picked = mesh[1]
            >>> assert np.array_equal(picked, [0, 0, 1])
            >>> assert np.array_equal(picked.maps[0], np.empty((0, 3)))
            >>> assert np.array_equal(picked.maps[1], [[0]])

            Masking
            >>> masked = mesh[[True, False, True, True, True]]
            >>> assert masked.equal([[0, 0, 0], [0, -1, 0], [1, 1, 1], [-1, -1, -1]])
            >>> assert masked.fields[0].equal([42, 10.5, 1, 1])
            >>> assert masked.fields[1].equal([1, 3, 3, 3])
            >>> assert masked.maps[0].equal([[1, 2, 3]])
            >>> assert masked.maps[1].equal([[0], [1], [2], [3]])

            Iteration
            >>> _ = [vertex for vertex in mesh]

        """
        item = super(TensorMaps, self).__getitem__(index)
        try:
            if issubclass(type(item), TensorMaps):
                if isinstance(index, tuple):
                    index = index[0]
                if item.maps:
                    item.maps = [mp.copy() for mp in item.maps]
                    indices = np.array(range(len(self)))
                    keep_indices = indices[index]
                    if isinstance(keep_indices, int):
                        keep_indices = [keep_indices]
                    delete_indices = set(indices).difference(set(keep_indices))

                    # correct all maps that contain deleted indices
                    for mp_idx in range(len(self.maps)):
                        # build mask, where the map should be deleted
                        map_delete_mask = np.full((len(self.maps[mp_idx]),), False, dtype=bool)
                        for i, mp in enumerate(self.maps[mp_idx]):
                            for index in mp:
                                if index in delete_indices:
                                    map_delete_mask[i] = True
                                    break
                        map_mask = ~map_delete_mask

                        # build the correction counters
                        move_up_counter = np.zeros(self.maps[mp_idx].shape, dtype=int)
                        for p in delete_indices:
                            move_up_counter[self.maps[mp_idx] > p] -= 1

                        item.maps[mp_idx] = (self.maps[mp_idx] + move_up_counter)[map_mask]
        except IndexError as err:
            warnings.warn("Index error occured for field.__getitem__. Error "
                          "message: {err}".format(**locals()))

        return item

    @classmethod
    def merged(cls, *objects, **kwargs):
        if not all([isinstance(o, cls) for o in objects]):
            # TODO: could allow if all faceScalars are none
            raise TypeError("Merge constructor only accepts {cls} instances."
                            .format(**locals()))
        tensor_lengths = [len(o) for o in objects]
        cum_tensor_lengths = [sum(tensor_lengths[:i]) for i in range(len(objects))]

        maps = []
        dims = []
        for i, o in enumerate(objects):
            for map_field in o.maps:
                map_field = map_field + cum_tensor_lengths[i]
                try:
                    mp_idx = dims.index(map_field.dim)
                except ValueError:
                    maps.append(map_field)
                    dims.append(map_field.dim)
                else:
                    maps[mp_idx] = TensorFields.merged(maps[mp_idx], map_field)
        # kwargs['maps'] = maps

        inst = super(TensorMaps, cls).merged(*objects, **kwargs)
        inst = cls.__new__(cls, inst, maps=maps)
        return inst

    def equal(self, other, **kwargs):
        """
        Test, whether the instance has the same content as other.
        Args:
            other (iterable)
            optional:
                see TensorFields.equal
        Examples:
            >>> import tfields
            >>> maps = [tfields.TensorFields([[1]], [42])]
            >>> tm = tfields.TensorMaps(maps[0], maps=maps)

            # >>> assert tm.equal(tm)
            >>> cp = tm.copy()

            # >>> assert tm.equal(cp)
            >>> cp.maps[0].fields[0] = -42
            >>> assert tm.maps[0].fields[0] == 42
            >>> assert not tm.equal(cp)

        """
        if not issubclass(type(other), Tensors):
            return super(TensorMaps, self).equal(other, **kwargs)
        else:
            with other.tmp_transform(self.coordSys):
                mask = super(TensorMaps, self).equal(other, **kwargs)
                if issubclass(type(other), TensorMaps):
                    if len(self.maps) != len(other.maps):
                        mask &= False
                    else:
                        for i, mp in enumerate(self.maps):
                            mask &= mp.equal(other.maps[i], **kwargs)
                return mask

    def stale(self):
        """
        Returns:
            Mask for all vertices that are stale i.e. are not refered by maps
        Examples:
            >>> import tfields
            >>> vectors = tfields.Tensors([[0, 0, 0], [0, 0, 1], [0, -1, 0], [4, 4, 4]])
            >>> tm = tfields.TensorMaps(vectors, maps=[[[0, 1, 2], [0, 1, 2]],
            ...                                       [[1, 1], [2, 2]]])
            >>> assert np.array_equal(tm.stale(), [False, False, False, True])

        """
        staleMask = np.full(self.shape[0], False, dtype=bool)
        used = set([ind for mp in self.maps for ind in mp.flatten()])
        for i in range(self.shape[0]):
            if i not in used:
                staleMask[i] = True
        return staleMask

    def cleaned(self, stale=True, duplicates=True):
        """
        Args:
            stale (bool): remove stale vertices
            duplicates (bool): replace duplicate vertices by originals
        Examples:
            >>> import tfields
            >>> mp1 = tfields.TensorFields([[0, 1, 2], [3, 4, 5]],
            ...                            *zip([1,2,3,4,5], [6,7,8,9,0]))
            >>> mp2 = tfields.TensorFields([[0], [3]])

            >>> tm = tfields.TensorMaps([[0,0,0], [1,1,1], [2,2,2], [0,0,0],
            ...                          [3,3,3], [4,4,4], [5,6,7]],
            ...                         maps=[mp1, mp2])

            >>> c = tm.cleaned()
            >>> assert c.equal([[0., 0., 0.],
            ...                 [1., 1., 1.],
            ...                 [2., 2., 2.],
            ...                 [3., 3., 3.],
            ...                 [4., 4., 4.]])
            >>> assert np.array_equal(c.maps[0], [[0, 1, 2], [0, 3, 4]])
            >>> assert np.array_equal(c.maps[1], [[0], [0]])


        Returns:
            copy of self without stale vertices and duplicat points (depending on arguments)
        """
        # remove stale vertices
        if stale:
            stale_mask = self.stale()
        else:
            stale_mask = np.full(self.shape[0], False, dtype=bool)
        # remove duplicates in order to not have any artificial separations
        inst = self
        if duplicates:
            inst = self.copy()
            duplicates = tfields.duplicates(self, axis=0)
            for tensor_index, duplicate_index in zip(range(self.shape[0]), duplicates):
                if duplicate_index != tensor_index:
                    stale_mask[tensor_index] = True
                    # redirect maps
                    for mp_idx in range(len(self.maps)):
                        for f in range(len(self.maps[mp_idx])):
                            if tensor_index in self.maps[mp_idx][f]:
                                index = tfields.index(self.maps[mp_idx][f], tensor_index)
                                inst.maps[mp_idx][f][index] = duplicate_index

        return inst.removed(stale_mask)

    def removed(self, remove_condition):
        """
        Return copy of self without vertices where remove_condition is True
        Copy because self is immutable

        Examples:
            >>> import tfields
            >>> m = tfields.TensorMaps([[0,0,0], [1,1,1], [2,2,2], [0,0,0],
            ...                         [3,3,3], [4,4,4], [5,5,5]],
            ...                        maps=[tfields.TensorFields([[0, 1, 2], [0, 1, 3],
            ...                                                    [3, 4, 5], [3, 4, 1],
            ...                                                    [3, 4, 6]],
            ...                                                   [1, 3, 5, 7, 9],
            ...                                                   [2, 4, 6, 8, 0])])
            >>> c = m.keep([False, False, False, True, True, True, True])
            >>> c.equal([[0, 0, 0],
            ...          [3, 3, 3],
            ...          [4, 4, 4],
            ...          [5, 5, 5]])
            True
            >>> c.maps[0]
            TensorFields([[0, 1, 2],
                          [0, 1, 3]])
            >>> assert c.maps[0].fields[0].equal([5, 9])
            >>> assert c.maps[0].fields[1].equal([6, 0])

        """
        remove_condition = np.array(remove_condition)
        # # built instance that only contains the vaild points
        # inst = self[~remove_condition].copy()
        # delete_indices = np.arange(self.shape[0])[remove_condition]
        # face_keep_masks = self.to_maps_masks(~remove_condition)

        # for mp_idx, face_keep_mask in enumerate(face_keep_masks):
        #     move_up_counter = np.zeros(self.maps[mp_idx].shape, dtype=int)

        #     # correct map:
        #     for p in delete_indices:
        #         move_up_counter[self.maps[mp_idx] > p] -= 1

        #     inst.maps[mp_idx] = (self.maps[mp_idx] + move_up_counter)[face_keep_mask]
        # return inst
        return self[~remove_condition]

    def keep(self, keep_condition):
        """
        Return copy of self with vertices where keep_condition is True
        Copy because self is immutable

        Examples:
            >>> import tfields
            >>> m = tfields.TensorMaps([[0,0,0], [1,1,1], [2,2,2], [0,0,0],
            ...                         [3,3,3], [4,4,4], [5,5,5]],
            ...                        maps=[tfields.TensorFields([[0, 1, 2], [0, 1, 3],
            ...                                                    [3, 4, 5], [3, 4, 1],
            ...                                                    [3, 4, 6]],
            ...                                                   [1, 3, 5, 7, 9],
            ...                                                   [2, 4, 6, 8, 0])])
            >>> c = m.removed([True, True, True, False, False, False, False])
            >>> c.equal([[0, 0, 0],
            ...          [3, 3, 3],
            ...          [4, 4, 4],
            ...          [5, 5, 5]])
            True
            >>> c.maps[0]
            TensorFields([[0, 1, 2],
                          [0, 1, 3]])
            >>> assert c.maps[0].fields[0].equal([5, 9])
            >>> assert c.maps[0].fields[1].equal([6, 0])

        """
        keep_condition = np.array(keep_condition)
        return self[keep_condition]

    def to_maps_masks(self, mask):
        """
        Examples:
            >>> from tfields import TensorMaps
            >>> import numpy as np
            >>> m = TensorMaps([[1,2,3], [3,3,3], [0,0,0], [5,6,7]],
            ...                maps=[[[0, 1, 2], [1, 2, 3]],
            ...                      [[0], [3]]])
            >>> from sympy.abc import x,y,z
            >>> vertexMask = m.evalf(z < 6)
            >>> faceMask = m.to_maps_masks(vertexMask)
            >>> assert np.array_equal(faceMask, [[True, False], [True, False]])
            >>> index_face_mask = m.to_maps_masks(0)
            >>> assert np.array_equal(index_face_mask, [[False, False], [True, False]])

        Returns:
            masks of maps with all vertices in mask
        """
        indices = np.array(range(len(self)))
        keep_indices = indices[mask]
        if isinstance(keep_indices, int):
            keep_indices = [keep_indices]
        delete_indices = set(indices).difference(set(keep_indices))
        # delete_indices = indices[~mask]
        # delete_indices = set(delete_indices)  # set speeds up everything enormously

        masks = []
        for mp_idx in range(len(self.maps)):
            map_delete_mask = np.full((len(self.maps[mp_idx]),), False, dtype=bool)
            for i, mp in enumerate(self.maps[mp_idx]):
                for index in mp:
                    if index in delete_indices:
                        map_delete_mask[i] = True
                        break
            masks.append(~map_delete_mask)
        return masks

    def parts(self, *map_descriptions):
        """
        Args:
            *map_descriptions (tuple): tuples of
                map_pos_idx (int): reference to map position
                    used like: self.maps[map_pos_idx]
                map_indices_list (list of list of int): each int refers
                    to index in a map.
        """
        # raise ValueError(map_descriptions)
        parts = []
        for map_description in map_descriptions:
            map_pos_idx, map_indices_list = map_description
            for map_indices in map_indices_list:
                obj = self.copy()
                map_indices = set(map_indices)  # for speed up
                map_delete_mask = np.array(
                    [True if i not in map_indices else False
                     for i in range(len(self.maps[map_pos_idx]))])
                obj.maps[map_pos_idx] = obj.maps[map_pos_idx][~map_delete_mask]
                obj = obj.cleaned(duplicates=False)
                parts.append(obj)
        return parts

    def disjoint_map(self, mp_idx):
        """
        Find the disjoint sets of map = self.maps[mp_idx]
        Args:
            mp_idx (int): reference to map position
                used like: self.maps[mp_idx]
        Returns:
            map description(tuple): see self.parts

        Examples:
            >>> import tfields
            >>> a = tfields.TensorMaps([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]],
            ...                        maps=[[[0, 1, 2], [0, 2, 3]]])
            >>> b = a.copy()

            >>> b[:, 0] += 2
            >>> m = tfields.TensorMaps.merged(a, b)
            >>> mp_description = m.disjoint_map(0)
            >>> parts = m.parts(mp_description)
            >>> aa, ba = parts
            >>> assert aa.maps[0].equal(ba.maps[0])
            >>> assert aa.equal(a)
            >>> assert ba.equal(b)

        """
        maps_list = tfields.lib.sets.disjoint_group_indices(self.maps[mp_idx])
        return (0, maps_list)


if __name__ == '__main__':  # pragma: no cover
    import doctest
    doctest.testmod()
    # doctest.run_docstring_examples(TensorFields.__getitem__, globals())
