import tfields
import numpy as np
import warnings
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import mpl_toolkits.mplot3d as plt3D




def plotArray(array, **kwargs):
    """
    Points3D plotting method.

    Args:
        axis (matplotlib.Axis) object
        xAxis (int): coordinate index that should be on xAxis
        yAxis (int): coordinate index that should be on yAxis
        zAxis (int or None): coordinate index that should be on zAxis.
            If it evaluates to None, 2D plot will be done.
        methodName (str): method name to use for filling the axis

    Returns:
        Artist or list of Artists (imitating the axis.scatter/plot behaviour).
        Better Artist not list of Artists
    """
    tfields.plotting.setDefault(kwargs, 'methodName', 'scatter')
    po = tfields.plotting.PlotOptions(kwargs)

    labelList = po.pop('labelList', ['x (m)', 'y (m)', 'z (m)'])
    xAxis, yAxis, zAxis = po.getXYZAxis()
    tfields.plotting.setLabels(po.axis, *po.getSortedLabels(labelList))
    if zAxis is None:
        args = [array[:, xAxis],
                array[:, yAxis]]
    else:
        args = [array[:, xAxis],
                array[:, yAxis],
                array[:, zAxis]]
    artist = po.method(*args,
                       **po.plotKwargs)
    return artist


def plotMesh(vertices, faces, **kwargs):
    """
    Args:
        axis (matplotlib axis)
        xAxis (int)
        yAxis (int)
        zAxis (int)
        edgecolor (color)
        color (color): if given, use this color for faces in 2D
        cmap
        vmin
        vmax
    """
    if faces.shape[0] == 0:
        warnings.warn("No faces to plot")
        return None
    if max(faces.flat) > vertices.shape[0]:
        raise ValueError("Some faces point to non existing vertices.")
    po = tfields.plotting.PlotOptions(kwargs)
    if po.dim == 2:
        full = True
        mesh = tfields.Mesh3D(vertices, faces=faces)
        xAxis, yAxis, zAxis = po.getXYZAxis()
        facecolors = po.retrieveChain('facecolors', 'color',
                                      default=0,
                                      keep=False)
        if full:
            # implementation that will sort the triangles by zAxis
            centroids = mesh.centroids()
            axesIndices = [0, 1, 2]
            axesIndices.pop(axesIndices.index(xAxis))
            axesIndices.pop(axesIndices.index(yAxis))
            zAxis = axesIndices[0]
            zs = centroids[:, zAxis]
            zs, faces, facecolors = tfields.lib.util.multi_sort(zs, faces,
                                                                facecolors)
            nFacesInitial = len(faces)
        else:
            # cut away "back sides" implementation
            directionVector = np.array([1., 1., 1.])
            directionVector[xAxis] = 0.
            directionVector[yAxis] = 0.
            normVectors = mesh.triangles.norms()
            dotProduct = np.dot(normVectors, directionVector)
            nFacesInitial = len(faces)
            faces = faces[dotProduct > 0]

        vertices = mesh

        po.plotKwargs['methodName'] = 'tripcolor'
        po.plotKwargs['triangles'] = faces

        """
        sort out color arguments
        """
        facecolors = po.formatColors(facecolors,
                                     fmt='norm',
                                     length=nFacesInitial)
        if not full:
            facecolors = facecolors[dotProduct > 0]
        po.plotKwargs['facecolors'] = facecolors

        d = po.plotKwargs
        d['xAxis'] = xAxis
        d['yAxis'] = yAxis
        artist = plotArray(vertices, **d)
    elif po.dim == 3:
        label = po.pop('label', None)
        color = po.retrieveChain('color', 'c', 'facecolors',
                                 default='grey',
                                 keep=False)
        color = po.formatColors(color,
                                fmt='rgba',
                                length=len(faces))
        nanMask = np.isnan(color)
        if nanMask.any():
            warnings.warn("nan found in colors. Removing the corresponding faces!")
            color = color[~nanMask]
            faces = faces[~nanMask]

        edgecolor = po.pop('edgecolor', None)
        alpha = po.pop('alpha', None)
        po.delNormArgs()

        triangles = np.array([vertices[face] for face in faces])
        artist = plt3D.art3d.Poly3DCollection(triangles, **po.plotKwargs)
        po.axis.add_collection3d(artist)

        if edgecolor is not None:
            artist.set_edgecolor(edgecolor)
            artist.set_facecolors(color)
        else:
            artist.set_color(color)

        if alpha is not None:
            artist.set_alpha(alpha)

        # for some reason auto-scale does not work
        tfields.plotting.autoscale3D(po.axis, array=vertices)

        # legend lables do not work at all as an argument
        if label:
            artist.set_label(label)

        # when plotting the legend edgecolors/facecolors2d are needed
        artist._edgecolors2d = None
        artist._facecolors2d = None

        labelList = ['x (m)', 'y (m)', 'z (m)']
        tfields.plotting.setLabels(po.axis, *po.getSortedLabels(labelList))

    return artist


def plotVectorField(points, vectors, **kwargs):
    """
    Args:
        points (array_like): base vectors
        vectors (array_like): direction vectors
    """
    po = tfields.plotting.PlotOptions(kwargs)
    if points is None:
        points = np.full(vectors.shape, 0.)
    artists = []
    xAxis, yAxis, zAxis = po.getXYZAxis()
    for point, vector in zip(points, vectors):
        if po.dim == 3:
            artists.append(po.axis.quiver(point[xAxis], point[yAxis], point[zAxis],
                                          vector[xAxis], vector[yAxis], vector[zAxis],
                                          **po.plotKwargs))
        else:
            artists.append(po.axis.quiver(point[xAxis], point[yAxis],
                                          vector[xAxis], vector[yAxis],
                                          **po.plotKwargs))
    return artists


def plotPlane(point, normal, **kwargs):

    def plot_vector(fig, orig, v, color='blue'):
        axis = fig.gca(projection='3d')
        orig = np.array(orig)
        v = np.array(v)
        axis.quiver(orig[0], orig[1], orig[2], v[0], v[1], v[2], color=color)
        axis.set_xlim(0, 10)
        axis.set_ylim(0, 10)
        axis.set_zlim(0, 10)
        axis = fig.gca(projection='3d')
        return fig

    def rotation_matrix(d):
        sin_angle = np.linalg.norm(d)
        if sin_angle == 0:
            return np.identity(3)
        d /= sin_angle
        eye = np.eye(3)
        ddt = np.outer(d, d)
        skew = np.array([[0, d[2], -d[1]],
                         [-d[2], 0, d[0]],
                         [d[1], -d[0], 0]],
                        dtype=np.float64)

        M = ddt + np.sqrt(1 - sin_angle**2) * (eye - ddt) + sin_angle * skew
        return M

    def pathpatch_2d_to_3d(pathpatch, z, normal):
        if type(normal) is str:  # Translate strings to normal vectors
            index = "xyz".index(normal)
            normal = np.roll((1.0, 0, 0), index)

        normal /= np.linalg.norm(normal)  # Make sure the vector is normalised
        path = pathpatch.get_path()  # Get the path and the associated transform
        trans = pathpatch.get_patch_transform()

        path = trans.transform_path(path)  # Apply the transform

        pathpatch.__class__ = plt3D.art3d.PathPatch3D  # Change the class
        pathpatch._code3d = path.codes  # Copy the codes
        pathpatch._facecolor3d = pathpatch.get_facecolor  # Get the face color

        verts = path.vertices  # Get the vertices in 2D

        d = np.cross(normal, (0, 0, 1))  # Obtain the rotation vector
        M = rotation_matrix(d)  # Get the rotation matrix

        pathpatch._segment3d = np.array([np.dot(M, (x, y, 0)) + (0, 0, z) for x, y in verts])

    def pathpatch_translate(pathpatch, delta):
        pathpatch._segment3d += delta

    kwargs['alpha'] = kwargs.pop('alpha', 0.5)
    po = tfields.plotting.PlotOptions(kwargs)
    patch = Circle((0, 0), **po.plotKwargs)
    po.axis.add_patch(patch)
    pathpatch_2d_to_3d(patch, z=0, normal=normal)
    pathpatch_translate(patch, (point[0], point[1], point[2]))


def plotSphere(point, radius, **kwargs):
    po = tfields.plotting.PlotOptions(kwargs)
    # Make data
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)
    x = point[0] + radius * np.outer(np.cos(u), np.sin(v))
    y = point[1] + radius * np.outer(np.sin(u), np.sin(v))
    z = point[2] + radius * np.outer(np.ones(np.size(u)), np.cos(v))

    # Plot the surface
    return po.axis.plot_surface(x, y, z, **po.plotKwargs)


"""
Color section
"""
def getColors(scalars, cmap=None, vmin=None, vmax=None):
    """
    retrieve the colors for a list of scalars
    """
    if not hasattr(scalars, '__iter__'):
        scalars = [scalars]
    if vmin is None:
        vmin = min(scalars)
    if vmax is None:
        vmax = max(scalars)
    colorMap = plt.get_cmap(cmap)
    norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
    return colorMap(map(norm, scalars))


def getColorsInverse(colors, cmap, vmin, vmax):
    """
    Reconstruct the numeric values (0 - 1) of given
    Args:
        colors (list or rgba tuple)
        cmap (matplotlib colormap)
        vmin (float)
        vmax (float)
    """
    # colors = np.array(colors)/255.
    r = np.linspace(vmin, vmax, 256)
    norm = matplotlib.colors.Normalize(vmin, vmax)
    mapvals = cmap(norm(r))[:, :4]  # there are 4 channels: r,g,b,a
    scalars = []
    for color in colors:
        distance = np.sum((mapvals - color) ** 2, axis=1)
        scalars.append(r[np.argmin(distance)])
    return scalars


if __name__ == '__main__':
    import tfields
    m = tfields.Mesh3D.grid((0, 2, 2), (0, 1, 3), (0, 0, 1))
    m.maps[0].fields.append(tfields.Tensors(np.arange(m.faces.shape[0])))
    art1 = m.plot(dim=3, map_index=0, label='twenty')

    m = tfields.Mesh3D.grid((4, 7, 2), (3, 5, 3), (2, 2, 1))
    m.maps[0].fields.append(tfields.Tensors(np.arange(m.faces.shape[0])))
    art = m.plot(dim=3, map_index=0, edgecolor='k', vmin=-1, vmax=1, label="something")

    plotSphere([7, 0, 1], 3)

    # mpt.setLegend(mpt.gca(3), [art1, art])
    # mpt.setAspectEqual(mpt.gca())
    # mpt.setView(vector=[0, 0, 1])
    # mpt.save('/tmp/test', 'png')
    # mpt.plt.show()
