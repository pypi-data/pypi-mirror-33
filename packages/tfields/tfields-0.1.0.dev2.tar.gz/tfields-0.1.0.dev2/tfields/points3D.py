#!/usr/bin/env
# encoding: utf-8
"""
Author:     Daniel Boeckenhoff
Mail:       daniel.boeckenhoff@ipp.mpg.de

basic threedimensional tensors
"""
import tfields


class Points3D(tfields.Tensors):
    # pylint: disable=R0904
    """
    Points3D is a general class for 3D Point operations and storage.
    Points are stored in np.arrays of shape (len, 3).
    Thus the three coordinates of the Points stay close.

    Args:
        points3DInstance  -> copy constructor
        [points3DInstance1, points3DInstance2, ...]  -> coordSys are correctly treated
        list of coordinates (see examples)

    Kwargs:
        coordSys (str):
            Use tfields.bases.CARTESIAN -> x, y, z
            Use tfields.bases.CYLINDER -> r, phi, z
            Use tfields.bases.SPHERICAL -> r, phi, theta

    Examples:
        Initializing with 3 vectors
        >>> import tfields
        >>> import numpy as np
        >>> p1 = tfields.Points3D([[1., 2., 3.], [4., 5., 6.], [1, 2, -6]])
        >>> p1
        Points3D([[ 1.,  2.,  3.],
                  [ 4.,  5.,  6.],
                  [ 1.,  2., -6.]])

        Initializing with list of coordinates
        >>> p2 = tfields.Points3D(np.array([[1., 2., 3., 4, 5,],
        ...                                 [4., 5., 6., 7, 8],
        ...                                 [1, 2, -6, -1, 0]]).T)
        >>> p2
        Points3D([[ 1.,  4.,  1.],
                  [ 2.,  5.,  2.],
                  [ 3.,  6., -6.],
                  [ 4.,  7., -1.],
                  [ 5.,  8.,  0.]])
        >>> p2.transform(tfields.bases.CYLINDER)
        >>> p2
        Points3D([[ 4.12310563,  1.32581766,  1.        ],
                  [ 5.38516481,  1.19028995,  2.        ],
                  [ 6.70820393,  1.10714872, -6.        ],
                  [ 8.06225775,  1.05165021, -1.        ],
                  [ 9.43398113,  1.01219701,  0.        ]])

        Copy constructor with one instance preserves coordSys of instance
        >>> assert tfields.Points3D(p2).coordSys == p2.coordSys

        Unless you specify other:
        >>> tfields.Points3D(p2, coordSys=tfields.bases.CARTESIAN)
        Points3D([[ 1.,  4.,  1.],
                  [ 2.,  5.,  2.],
                  [ 3.,  6., -6.],
                  [ 4.,  7., -1.],
                  [ 5.,  8.,  0.]])

        Copy constructor with many instances chooses majority of coordinates
        systems to avoid much transformation
        >>> tfields.Points3D.merged(p1, p2, p1)
        Points3D([[ 1.,  2.,  3.],
                  [ 4.,  5.,  6.],
                  [ 1.,  2., -6.],
                  [ 1.,  4.,  1.],
                  [ 2.,  5.,  2.],
                  [ 3.,  6., -6.],
                  [ 4.,  7., -1.],
                  [ 5.,  8.,  0.],
                  [ 1.,  2.,  3.],
                  [ 4.,  5.,  6.],
                  [ 1.,  2., -6.]])
        >>> p1.transform(tfields.bases.CYLINDER)

        ... unless specified other. Here it is specified
        >>> tfields.Points3D.merged(p1, p2, coordSys=tfields.bases.CYLINDER)
        Points3D([[ 2.23606798,  1.10714872,  3.        ],
                  [ 6.40312424,  0.89605538,  6.        ],
                  [ 2.23606798,  1.10714872, -6.        ],
                  [ 4.12310563,  1.32581766,  1.        ],
                  [ 5.38516481,  1.19028995,  2.        ],
                  [ 6.70820393,  1.10714872, -6.        ],
                  [ 8.06225775,  1.05165021, -1.        ],
                  [ 9.43398113,  1.01219701,  0.        ]])

        Shape is always (..., 3)
        >>> p = tfields.Points3D([[1., 2., 3.], [4., 5., 6.],
        ...                       [1, 2, -6], [-5, -5, -5], [1,0,-1], [0,1,-1]])
        >>> p.shape
        (6, 3)

        Empty array will create an ndarray of the form (0, 3)
        >>> tfields.Points3D([])
        Points3D([], shape=(0, 3), dtype=float64)

        Use it as np.ndarrays -> masking etc. is inherited
        >>> mask = np.array([True, False, True, False, False, True])
        >>> mp = p[mask].copy()

        Copy constructor
        >>> mp
        Points3D([[ 1.,  2.,  3.],
                  [ 1.,  2., -6.],
                  [ 0.,  1., -1.]])
        >>> tfields.Points3D(mp)
        Points3D([[ 1.,  2.,  3.],
                  [ 1.,  2., -6.],
                  [ 0.,  1., -1.]])

        Coordinate system is implemented. Default is cartesian
        >>> p_cart = p.copy()
        >>> p.transform(tfields.bases.CYLINDER)
        >>> assert p.equal(
        ...     tfields.Points3D([[2.236,  1.107,  3.],
        ...                       [6.403,  0.896,  6.],
        ...                       [2.236,  1.107, -6.],
        ...                       [7.071, -2.356, -5.],
        ...                       [1.   ,  0.   , -1.],
        ...                       [1.   ,  1.571, -1.]],
        ...                      coordSys=tfields.bases.CYLINDER),
        ...     atol=1e-3)
        >>> p.transform(tfields.bases.CARTESIAN)
        >>> assert p.equal(p_cart, atol=1e-15)

    """
    def __new__(cls, tensors, **kwargs):
        if not issubclass(type(tensors), Points3D):
            kwargs['dim'] = 3
        return super(Points3D, cls).__new__(cls, tensors, **kwargs)


if __name__ == '__main__':  # pragma: no cover
    import doctest
    doctest.testmod()
    # doctest.run_docstring_examples(Points3D, globals())
