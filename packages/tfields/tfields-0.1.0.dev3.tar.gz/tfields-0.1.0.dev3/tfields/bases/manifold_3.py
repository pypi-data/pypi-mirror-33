import tfields
import sympy
import numpy as np
import warnings

CARTESIAN = 'cartesian'
CYLINDER = 'cylinder'
SPHERICAL = 'spherical'

m = sympy.diffgeom.Manifold('M', 3)
patch = sympy.diffgeom.Patch('P', m)

# cartesian
x, y, z = sympy.symbols('x, y, z')
cartesian = sympy.diffgeom.CoordSystem(CARTESIAN, patch, ['x', 'y', 'z'])

# cylinder

R, Phi, Z = sympy.symbols('R, Phi, Z')
cylinder = sympy.diffgeom.CoordSystem(CYLINDER, patch, ['R', 'Phi', 'Z'])
cylinder.connect_to(cartesian,
                    [R, Phi, Z],
                    [R * sympy.cos(Phi),
                     R * sympy.sin(Phi),
                     Z],
                    inverse=False,
                    fill_in_gaps=False)


def cylinder_to_cartesian(array):
    rPoints = np.copy(array[:, 0])
    phiPoints = np.copy(array[:, 1])
    array[:, 0] = rPoints * np.cos(phiPoints)
    array[:, 1] = rPoints * np.sin(phiPoints)


cylinder.to_cartesian = cylinder_to_cartesian


cartesian.connect_to(cylinder,
                     [x, y, z],
                     [sympy.sqrt(x**2 + y**2),
                      sympy.Piecewise(
                          (sympy.pi, ((x < 0) & sympy.Eq(y, 0))),
                          (0., sympy.Eq(sympy.sqrt(x**2 + y**2), 0)),
                          (sympy.sign(y) * sympy.acos(x / sympy.sqrt(x**2 + y**2)), True)),
                      z],
                     inverse=False,
                     fill_in_gaps=False)


def cartesian_to_cylinder(array):
    x_vals = np.copy(array[:, 0])
    y_vals = np.copy(array[:, 1])
    problem_phi_indices = np.where((x_vals < 0) & (y_vals == 0))
    array[:, 0] = np.sqrt(x_vals**2 + y_vals**2)  # r
    np.seterr(divide='ignore', invalid='ignore')
    # phi
    array[:, 1] = np.sign(y_vals) * np.arccos(x_vals / array[:, 0])
    np.seterr(divide='warn', invalid='warn')
    array[:, 1][problem_phi_indices] = np.pi
    tfields.convert_nan(array, 0.)  # for cases like cartesian 0, 0, 1


cartesian.to_cylinder = cartesian_to_cylinder

# spherical
r, phi, theta = sympy.symbols('r, phi, theta')
spherical = sympy.diffgeom.CoordSystem(SPHERICAL, patch, ['r', 'phi', 'theta'])
spherical.connect_to(cartesian,
                     [r, phi, theta],
                     [r * sympy.cos(phi - np.pi) * sympy.sin(theta - np.pi / 2),
                      r * sympy.sin(phi - np.pi) * sympy.sin(theta - np.pi / 2),
                      r * sympy.cos(theta - np.pi / 2)],
                     # [r * sympy.cos(phi) * sympy.sin(theta),
                     #  r * sympy.sin(phi) * sympy.sin(theta),
                     #  r * sympy.cos(theta)],
                     inverse=False,
                     fill_in_gaps=False)


def spherical_to_cartesian(array):
    r = np.copy(array[:, 0])
    phi = np.copy(array[:, 1])
    theta = np.copy(array[:, 2])
    array[:, 0] = r * np.sin(theta - np.pi / 2) * np.cos(phi - np.pi)
    array[:, 1] = r * np.sin(theta - np.pi / 2) * np.sin(phi - np.pi)
    array[:, 2] = r * np.cos(theta - np.pi / 2)

    # classical
    # array[:, 0] = r * np.sin(theta) * np.cos(phi)
    # array[:, 1] = r * np.sin(theta) * np.sin(phi)
    # array[:, 2] = r * np.cos(theta)


spherical.to_cartesian = spherical_to_cartesian


cartesian.connect_to(spherical,
                     [x, y, z],
                     [sympy.sqrt(x**2 + y**2 + z**2),
                      sympy.Piecewise(
                          (sympy.pi, ((x < 0) & sympy.Eq(y, 0))),
                          (0., sympy.Eq(sympy.sqrt(x**2 + y**2), 0)),
                          (sympy.sign(y) * sympy.acos(x / sympy.sqrt(x**2 + y**2)), True)),
                      sympy.Piecewise(
                          (0., sympy.Eq(x**2 + y**2 + z**2, 0)),
                          (sympy.atan2(z, sympy.sqrt(x**2 + y**2)), True))],
                      # sympy.Piecewise(
                      #     (0., (sympy.Eq(x, 0) & sympy.Eq(y, 0))),
                      #     (sympy.atan(y / x), True)),
                      # sympy.Piecewise(
                      #     (0., sympy.Eq(x**2 + y**2 + z**2, 0)),
                      #     # (0., (sympy.Eq(x, 0) & sympy.Eq(y, 0) & sympy.Eq(z, 0))),
                      #     (sympy.acos(z / sympy.sqrt(x**2 + y**2 + z**2)), True))],
                     inverse=False,
                     fill_in_gaps=False)


def cartesian_to_spherical(array):
    """
    convert array to r, phi, theta
    r in [0, oo]
    phi in [-pi, pi]
    theta element [0, pi]: elevation angle defined from - Z-axis up
    """
    xy = array[:, 0]**2 + array[:, 1]**2

    # phi for phi between -pi, pi
    problemPhiIndices = np.where((array[:, 0] < 0) & (array[:, 1] == 0))
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', message="invalid value encountered in divide")
        array[:, 1] = np.sign(array[:, 1]) * np.arccos(array[:, 0] / np.sqrt(xy))
    array[:, 1][problemPhiIndices] = np.pi

    tfields.convert_nan(array, 0.)  # for cases like cartesian 0, 0, 1
    # array[:,1] = np.arctan2(array[:,1], array[:,0])  # phi for phi between 0, 2pi

    # r
    array[:, 0] = np.sqrt(xy + array[:, 2]**2)

    # theta
    # for elevation angle defined from - Z-axis up:
    # array[:, 2] = np.arctan2(np.sqrt(xy), array[:, 2])
    # for elevation angle defined from XY-plane up:
    array[:, 2] = np.arctan2(array[:, 2], np.sqrt(xy))


cartesian.to_spherical = cartesian_to_spherical
