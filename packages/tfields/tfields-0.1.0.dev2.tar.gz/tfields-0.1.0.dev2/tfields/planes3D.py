#!/usr/bin/env
# encoding: utf-8
"""
Author:     Daniel Boeckenhoff
Mail:       daniel.boeckenhoff@ipp.mpg.de

part of tfields library
"""
import tfields
import sympy


class Planes3D(tfields.TensorFields):
    """
    Point-NormVector representaion of planes
    """

    def symbolic(self):
        """
        Returns:
            list: list with sympy.Plane objects
        """
        return [sympy.Plane(point, normal_vector=vector)
                for point, vector in zip(self.points, self.vectors)]

    def plot(self, **kwargs):  # pragma: no cover
        """
        forward to Mesh3D plotting
        """
        artists = []
        for i in range(len(self)):
            artists.append(tfields.plotting.plotPlane(self[i],
                                                      self.vectors[0],
                                                      **kwargs))
        # symbolic = self.symbolic()
        # planeMeshes = [tfields.Mesh3D([pl.arbitrary_point(t=(i + 1) * 1. / 2 * np.pi)
        #                                for i in range(4)],
        #                               faces=[[0, 1, 2], [1, 2, 3], [2, 3, 0]]) for pl in symbolic]
        # artists = [m.plot(**kwargs) for m in planeMeshes]
        return artists


if __name__ == '__main__':  # pragma: no cover
    import doctest
    doctest.testmod()
