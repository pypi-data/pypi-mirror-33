#!/usr/bin/env
# encoding: utf-8
"""
Author:     Daniel Boeckenhoff
Mail:       daniel.boeckenhoff@ipp.mpg.de

Collection of additional numpy functions
part of tfields library
"""
import numpy as np


def convert_nan(array, value=0.):
    """
    Replace all occuring NaN values by value
    """
    nanIndices = np.isnan(array)
    array[nanIndices] = value


def view1D(ar):
    """
    https://stackoverflow.com/a/44999009/ @Divakar
    """
    ar = np.ascontiguousarray(ar)
    voidDt = np.dtype((np.void, ar.dtype.itemsize * ar.shape[1]))
    return ar.view(voidDt).ravel()


def argsort_unique(idx):
    """
    https://stackoverflow.com/a/43411559/ @Divakar
    """
    n = idx.size
    sidx = np.empty(n, dtype=int)
    sidx[idx] = np.arange(n)
    return sidx


def duplicates(ar, axis=None):
    """
    View1D version of duplicate search
    Speed up version after
    https://stackoverflow.com/questions/46284660 \
        /python-numpy-speed-up-2d-duplicate-search/46294916#46294916
    Args:
        ar (array_like): array
        other args: see np.isclose
    Examples:
        >>> import tfields
        >>> import numpy as np
        >>> a = np.array([[1, 0, 0], [1, 0, 0], [2, 3, 4]])
        >>> tfields.duplicates(a, axis=0)
        array([0, 0, 2])

    Returns:
        list of int: int is pointing to first occurence of unique value
    """
    if axis != 0:
        raise NotImplementedError()
    sidx = np.lexsort(ar.T)
    b = ar[sidx]

    groupIndex0 = np.flatnonzero((b[1:] != b[:-1]).any(1)) + 1
    groupIndex = np.concatenate(([0], groupIndex0, [b.shape[0]]))
    ids = np.repeat(range(len(groupIndex) - 1), np.diff(groupIndex))
    sidx_mapped = argsort_unique(sidx)
    ids_mapped = ids[sidx_mapped]

    grp_minidx = sidx[groupIndex[:-1]]
    out = grp_minidx[ids_mapped]
    return out


def index(ar, entry, rtol=0, atol=0, equal_nan=False, axis=None):
    """
    Examples:
        >>> import tfields
        >>> a = np.array([[1, 0, 0], [1, 0, 0], [2, 3, 4]])
        >>> tfields.index(a, [2, 3, 4], axis=0)
        2

        >>> a = np.array([[1, 0, 0], [2, 3, 4]])
        >>> tfields.index(a, 4)
        5

    Returns:
        list of int: indices of point occuring
    """
    if axis is None:
        ar = ar.flatten()
    elif axis != 0:
        raise NotImplementedError()
    for i, part in enumerate(ar):
        isclose = np.isclose(part, entry, rtol=rtol, atol=atol,
                             equal_nan=equal_nan)
        if axis is not None:
            isclose = isclose.all()
        if isclose:
            return i


if __name__ == '__main__':
    import doctest
    doctest.testmod()
else:
    from . import grid
    from .grid import igrid
    from . import stats
    from .stats import mode, median, mean
    from . import symbolics
    from . import sets
    from . import util
