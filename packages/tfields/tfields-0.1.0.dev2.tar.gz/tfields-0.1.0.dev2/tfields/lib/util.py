"""
Various utility functions
"""
import itertools
from six import string_types


def pairwise(iterable):
    """
    iterator s -> (s0,s1), (s1,s2), (s2, s3), ...
    Source:
        https://stackoverflow.com/questions/5434891/iterate-a-list-as-pair-current-next-in-python
    Returns:
        two iterators, one ahead of the other
    """
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)


def flatten(seq, container=None, keep_types=None):
    """
    Approach to flatten a nested sequence.
    Args:
        seq (iterable): iterable to be flattened
        containter (iterable): iterable defining an append method. Values will
            be appended there
        keep_types (list of type): types that should not be flattened but kept
            in nested form
    Examples:
        >>> from tfields.lib.util import flatten
        >>> import numpy as np
        >>> flatten([[1,2,3],4,[[5,[6]]]])
        [1, 2, 3, 4, 5, 6]
        >>> flatten([[1,2,3],4,[[5,[{6:1}]]]], keep_types=[dict])
        [1, 2, 3, 4, 5, {6: 1}]
        >>> flatten([[1,2,3],4,[[5,[np.array([6])]]]], keep_types=[np.ndarray])
        [1, 2, 3, 4, 5, array([6])]

        Strings work although they have the __iter__ attribute in python3
        >>> flatten([[0, 0, 0, 'A'], [1, 2, 3]])
        [0, 0, 0, 'A', 1, 2, 3]

    """
    if keep_types is None:
        keep_types = []
    if container is None:
        container = []
    for s in seq:
        if hasattr(s, '__iter__') and not isinstance(s, string_types) \
                and not any([isinstance(s, t) for t in keep_types]):
            flatten(s, container, keep_types)
        else:
            container.append(s)
    return container


def multi_sort(array, *others, **kwargs):
    """
    Sort both lists with list 1
    Args:
        array
        *others
        **kwargs:
            method (function): sorting function. Default is 'sorted' 
            ...: further arguments are passed to method. Default rest is 
                'key=array[0]'
    Examples:
        >>> from tfields.lib.util import multi_sort
        >>> multi_sort([1,2,3,6,4], [1,2,3,4,5])
        [[1, 2, 3, 4, 6], [1, 2, 3, 5, 4]]
        >>> a, b = multi_sort([1,2,3,6,4], [1,2,3,4,5])
        >>> b
        [1, 2, 3, 5, 4]

        Expanded to sort as many objects as needed
        >>> multi_sort([1,2,3,6,4], [1,2,3,4,5], [6,5,4,3,2])
        [[1, 2, 3, 4, 6], [1, 2, 3, 5, 4], [6, 5, 4, 2, 3]]

    """
    method = kwargs.pop('method', None)
    if method is None:
        method = sorted
        if 'key' not in kwargs:
            kwargs['key'] = lambda pair: pair[0]
    return [list(x) for x in zip(*method(zip(array, *others), **kwargs))]
