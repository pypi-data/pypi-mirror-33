#!/usr/bin/env
# encoding: utf-8
"""
Author:     Daniel Boeckenhoff
Mail:       daniel.boeckenhoff@ipp.mpg.de

part of tfields library
"""
import numpy as np
import scipy
import scipy.stats


def mode(array, axis=0, bins='auto', range=None):
    """
    generalisation of the scipy.stats.mode function for floats with binning
    Examples:
        Forwarding usage:
        >>> import tfields
        >>> import numpy as np
        >>> tfields.lib.stats.mode([[2,2,3], [4,5,3]])
        array([[2, 2, 3]])
        >>> tfields.lib.stats.mode([[2,2,3], [4,5,3]], axis=1)
        array([[2],
               [3]])

        Float usage:
        >>> np.random.seed(seed=0)  # deterministic random
        >>> n = np.random.normal(3.1, 2., 1000)
        >>> tfields.lib.stats.mode(n)
        array([ 2.30838613])
        >>> tfields.lib.stats.mode(n, bins='sturges')
        array([ 2.81321206])
        >>> tfields.lib.stats.mode(np.array([n, n]), axis=1)
        array([[ 2.30838613],
               [ 2.30838613]])
        >>> tfields.lib.stats.mode(np.array([n, n]), axis=0).shape
        (1000, 1)
        >>> tfields.lib.stats.mode(np.array([n, n]), axis=1).shape
        (2, 1)
        >>> tfields.lib.stats.mode(np.array([n, n]), axis=None)
        array([ 2.81321206])

    """
    array = np.asarray(array)
    if issubclass(array.dtype.type, np.integer):
        return scipy.stats.mode(array, axis=axis).mode

    # hack only works for 2 dimensional arrays
    if len(array.shape) > 2:
        raise NotImplementedError("Only dimensions <= 2 allowed")

    if len(array.shape) == 2:
        if axis is None:
            array = array.reshape(array.size)
            return mode(array, axis=0, bins=bins, range=range)
        if axis == 0:
            array = array.T
        return np.array([mode(a, axis=0, bins=bins, range=range) for a in array])

    # only 1 d arrays remaining
    if not (axis is None or axis == 0):
        raise NotImplementedError("Axis is not None or 0 but {0}".format(axis))

    hist, binEdges = np.histogram(array, bins)
    maxIndex = hist.argmax(axis=axis)
    return np.array([0.5 * (binEdges[maxIndex] + binEdges[maxIndex + 1])])


mean = np.mean
median = np.median


def getMoment(array, moment):
    """
    Returns:
        Moments of the distribution.
    Note:
        The first moment is given as the mean,
        second as variance etc. Not 0 as it is mathematicaly correct.
    Args:
        moment (int): n-th moment
    """
    if moment == 0:
        return 0
    if moment == 1:  # center of mass
        return np.average(array, axis=0)
    elif moment == 2:  # variance
        return np.var(array, axis=0)
    elif moment == 3 and scipy.stats:  # skewness
        return scipy.stats.skew(array, axis=0)
    elif moment == 4 and scipy.stats:  # kurtosis
        return scipy.stats.kurtosis(array, axis=0)
    else:
        raise NotImplementedError("Moment %i not implemented." % moment)


if __name__ == '__main__':
    import doctest
    import tfields  # NOQA: F401
    doctest.testmod()
