"""
Core plotting tools for tfields library. Especially PlotOptions class
is basis for many plotting expansions
"""
import warnings
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from .mpl import *


def setDefault(dictionary, attr, value):
    """
    Set defaults to a dictionary
    """
    if attr not in dictionary:
        dictionary[attr] = value


def gca(dim=None, **kwargs):
    """
    Forwarding to plt.gca but translating the dimension to projection
    correct dimension
    """
    if dim == 3:
        axis = plt.gca(projection='3d', **kwargs)
    else:
        axis = plt.gca(**kwargs)
        if dim != axisDim(axis):
            if dim is not None:
                warnings.warn("You have another dimension set as gca."
                              "I will force the new dimension to return.")
                axis = plt.gcf().add_subplot(1, 1, 1, **kwargs)
    return axis


def axisDim(axis):
    """
    Returns int: axis dimension
    """
    if hasattr(axis, 'get_zlim'):
        return 3
    else:
        return 2


def setLabels(axis, *labels):
    axis.set_xlabel(labels[0])
    axis.set_ylabel(labels[1])
    if axisDim(axis) == 3:
        axis.set_zlabel(labels[2])


def autoscale3D(axis, array=None, xLim=None, yLim=None, zLim=None):
    if array is not None:
        xMin, yMin, zMin = array.min(axis=0)
        xMax, yMax, zMax = array.max(axis=0)
        xLim = (xMin, xMax)
        yLim = (yMin, yMax)
        zLim = (zMin, zMax)
    xLimAxis = axis.get_xlim()
    yLimAxis = axis.get_ylim()
    zLimAxis = axis.get_zlim()

    if not False:
        # not empty axis
        xMin = min(xLimAxis[0], xLim[0])
        yMin = min(yLimAxis[0], yLim[0])
        zMin = min(zLimAxis[0], zLim[0])
        xMax = max(xLimAxis[1], xLim[1])
        yMax = max(yLimAxis[1], yLim[1])
        zMax = max(zLimAxis[1], zLim[1])
    axis.set_xlim([xMin, xMax])
    axis.set_ylim([yMin, yMax])
    axis.set_zlim([zMin, zMax])


class PlotOptions(object):
    """
    processing kwargs for plotting functions and providing easy
    access to axis, dimension and plotting method as well as indices
    for array choice (x..., y..., zAxis)
    """
    def __init__(self, kwargs):
        kwargs = dict(kwargs)
        self.axis = kwargs.pop('axis', None)
        self.dim = kwargs.pop('dim', None)
        self.method = kwargs.pop('methodName', None)
        self.setXYZAxis(kwargs)
        self.plotKwargs = kwargs

    @property
    def method(self):
        """
        Method for plotting. Will be callable together with plotKwargs
        """
        return self._method

    @method.setter
    def method(self, methodName):
        if not isinstance(methodName, str):
            self._method = methodName
        else:
            self._method = getattr(self.axis, methodName)

    @property
    def dim(self):
        """
        axis dimension
        """
        return self._dim

    @dim.setter
    def dim(self, dim):
        if dim is None:
            if self._axis is None:
                dim = 2
            dim = axisDim(self._axis)
        elif self._axis is not None:
            if not dim == axisDim(self._axis):
                raise ValueError("Axis and dim argument are in conflict.")
        if dim not in [2, 3]:
            raise NotImplementedError("Dimensions other than 2 or 3 are not supported.")
        self._dim = dim

    @property
    def axis(self):
        """
        The plt.Axis object that belongs to this instance
        """
        if self._axis is None:
            return gca(self._dim)
        else:
            return self._axis

    @axis.setter
    def axis(self, axis):
        self._axis = axis

    def setXYZAxis(self, kwargs):
        self._xAxis = kwargs.pop('xAxis', 0)
        self._yAxis = kwargs.pop('yAxis', 1)
        zAxis = kwargs.pop('zAxis', None)
        if zAxis is None and self.dim == 3:
            indicesUsed = [0, 1, 2]
            indicesUsed.remove(self._xAxis)
            indicesUsed.remove(self._yAxis)
            zAxis = indicesUsed[0]
        self._zAxis = zAxis

    def getXYZAxis(self):
        return self._xAxis, self._yAxis, self._zAxis

    def setVminVmaxAuto(self, vmin, vmax, scalars):
        """
        Automatically set vmin and vmax as min/max of scalars
        but only if vmin or vmax is None
        """
        if scalars is None:
            return
        if len(scalars) < 2:
            warnings.warn("Need at least two scalars to autoset vmin and/or vmax!")
            return
        if vmin is None:
            vmin = min(scalars)
            self.plotKwargs['vmin'] = vmin
        if vmax is None:
            vmax = min(scalars)
            self.plotKwargs['vmax'] = vmax

    def getNormArgs(self, vminDefault=0, vmaxDefault=1, cmapDefault=None):
        if cmapDefault is None:
            cmapDefault = plt.rcParams['image.cmap']
        cmap = self.get('cmap', cmapDefault)
        vmin = self.get('vmin', vminDefault)
        vmax = self.get('vmax', vmaxDefault)
        return cmap, vmin, vmax

    def formatColors(self, colors, fmt='rgba', length=None):
        """
        format colors according to fmt argument
        Args:
            colors (list/one value of rgba tuples/int/float/str): This argument will
                be interpreted as color
            fmt (str): rgba / norm
            length (int/None): if not None: corrct colors lenght
    
        Returns:
            colors in fmt
        """
        hasIter = True
        if not hasattr(colors, '__iter__'):
            # colors is just one element
            hasIter = False
            colors = [colors]
        if hasattr(colors[0], '__iter__') and fmt == 'norm':
            # rgba given but norm wanted
            cmap, vmin, vmax = self.getNormArgs(cmapDefault='NotSpecified',
                                                vminDefault=None,
                                                vmaxDefault=None)
            colors = getColorsInverse(colors, cmap, vmin, vmax)
            self.plotKwargs['vmin'] = vmin
            self.plotKwargs['vmax'] = vmax
            self.plotKwargs['cmap'] = cmap
        elif fmt == 'rgba':
            if isinstance(colors[0], str) or isinstance(colors[0], unicode):
                # string color defined
                colors = map(mpl.colors.to_rgba, colors)
            else:
                # norm given rgba wanted
                cmap, vmin, vmax = self.getNormArgs(cmapDefault='NotSpecified',
                                                    vminDefault=None,
                                                    vmaxDefault=None)
                self.setVminVmaxAuto(vmin, vmax, colors)
                # update vmin and vmax
                cmap, vmin, vmax = self.getNormArgs()
                colors = getColors(colors,
                                   vmin=vmin,
                                   vmax=vmax,
                                   cmap=cmap)
    
        if length is not None:
            # just one colors value given
            if len(colors) != length:
                if not len(colors) == 1:
                    raise ValueError("Can not correct color length")
                colors = list(colors)
                colors *= length
        elif not hasIter:
            colors = colors[0]
    
        colors = np.array(colors)
        return colors

    def delNormArgs(self):
        self.plotKwargs.pop('vmin', None)
        self.plotKwargs.pop('vmax', None)
        self.plotKwargs.pop('cmap', None)

    def getSortedLabels(self, labels):
        """
        Returns the labels corresponding to the axes
        """
        return [labels[i] for i in self.getXYZAxis() if i is not None]
        
    def get(self, attr, default=None):
        return self.plotKwargs.get(attr, default)

    def pop(self, attr, default=None):
        return self.plotKwargs.pop(attr, default)

    def set(self, attr, value):
        self.plotKwargs[attr] = value

    def setDefault(self, attr, value):
        setDefault(self.plotKwargs, attr, value)

    def retrieve(self, attr, default=None, keep=True):
        if keep:
            return self.get(attr, default)
        else:
            return self.pop(attr, default)

    def retrieveChain(self, *args, **kwargs):
        default = kwargs.pop('default', None)
        keep = kwargs.pop('keep', True)
        if len(args) > 1:
            return self.retrieve(args[0],
                                 self.retrieveChain(*args[1:],
                                                    default=default,
                                                    keep=keep),
                                 keep=keep)
        if len(args) != 1:
            raise ValueError("Invalid number of args ({0})".format(len(args)))
        return self.retrieve(args[0], default, keep=keep)
