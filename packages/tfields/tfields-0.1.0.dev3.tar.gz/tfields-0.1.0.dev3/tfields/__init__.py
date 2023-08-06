__version__ = '0.1.0.dev3'
__author__ = "Daniel Boeckenhoff"
__email__ = "daniel.boeckenhoff@ipp.mpg.de"

from . import core
from . import bases
from . import lib
from .lib import *
from . import plotting

# __all__ = ['core', 'points3D']
from .core import Tensors, TensorFields, TensorMaps
from .points3D import Points3D
from .mask import evalf

# methods:
from .mask import evalf  # NOQA
from .lib import *  # NOQA

# classes:
from .points3D import Points3D  # NOQA
from .mesh3D import Mesh3D  # NOQA
from .mesh3D import fields_to_scalars, scalars_to_fields
from .triangles3D import Triangles3D  # NOQA
from .planes3D import Planes3D  # NOQA
