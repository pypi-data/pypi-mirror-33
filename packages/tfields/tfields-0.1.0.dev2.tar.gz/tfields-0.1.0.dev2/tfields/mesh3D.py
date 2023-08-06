#!/usr/bin/env
# encoding: utf-8
"""
Author:     Daniel Boeckenhoff
Mail:       daniel.boeckenhoff@ipp.mpg.de

part of tfields library
"""
import numpy as np
import sympy
import tfields
from tfields.lib.decorators import cached_property


def _dist_from_plane(point, plane):
    return plane['normal'].dot(point) + plane['d']


def _segment_plane_intersection(p0, p1, plane):
    """
    Returns:
        points, direction
    """
    distance0 = _dist_from_plane(p0, plane)
    distance1 = _dist_from_plane(p1, plane)
    p0OnPlane = abs(distance0) < np.finfo(float).eps
    p1OnPlane = abs(distance1) < np.finfo(float).eps
    points = []
    direction = 0
    if p0OnPlane:
        points.append(p0)

    if p1OnPlane:
        points.append(p1)
    # remove duplicate points
    if len(points) > 1:
        points = np.unique(points, axis=0)
    if p0OnPlane and p1OnPlane:
        return points, direction

    if distance0 * distance1 > np.finfo(float).eps:
        return points, direction

    direction = np.sign(distance0)
    if abs(distance0) < np.finfo(float).eps:
        return points, direction
    elif abs(distance1) < np.finfo(float).eps:
        return points, direction
    if abs(distance0 - distance1) > np.finfo(float).eps:
        t = distance0 / (distance0 - distance1)
    else:
        return points, direction

    points.append(p0 + t * (p1 - p0))
    # remove duplicate points
    if len(points) > 1:
        points = np.unique(points, axis=0)
    return points, direction


def _intersect(triangle, plane, vertices_rejected):
    """
    Intersect a triangle with a plane. Give the info, which side of the
    triangle is rejected by passing the mask vertices_rejected
    Returns:
        list of list. The inner list is of length 3 and refers to the points of
        new triangles. The reference is done with varying types:
            int: reference to triangle index
            complex: reference to duplicate point. This only happens in case
                two triangles are returned. Then only in the second triangle
            iterable: new vertex

    TODO:
        align norm vectors with previous face
    """
    nTrue = vertices_rejected.count(True)
    lonely_bool = True if nTrue == 1 else False
    index = vertices_rejected.index(lonely_bool)
    s0, d0 = _segment_plane_intersection(triangle[0], triangle[1], plane)
    s1, d1 = _segment_plane_intersection(triangle[1], triangle[2], plane)
    s2, d2 = _segment_plane_intersection(triangle[2], triangle[0], plane)

    single_index = index
    couple_indices = [j for j in range(3)
                      if not vertices_rejected[j] == lonely_bool]

    # TODO handle special cases. For now triangles with at least two points on plane are excluded
    new_points = None

    if len(s0) == 2:
        # both points on plane
        return new_points
    if len(s1) == 2:
        # both points on plane
        return new_points
    if len(s2) == 2:
        # both points on plane
        return new_points
    if lonely_bool:
        # two new triangles
        if len(s0) == 1 and len(s1) == 1:
            new_points = [[couple_indices[0], s0[0], couple_indices[1]],
                          [couple_indices[1], complex(1), s1[0]]]
        elif len(s1) == 1 and len(s2) == 1:
            new_points = [[couple_indices[0], couple_indices[1], s1[0]],
                          [couple_indices[0], complex(2), s2[0]]]
        elif len(s0) == 1 and len(s2) == 1:
            new_points = [[couple_indices[0], couple_indices[1], s0[0]],
                          [couple_indices[1], s2[0], complex(2)]]

    else:
        # one new triangle
        if len(s0) == 1 and len(s1) == 1:
            new_points = [[single_index, s1[0], s0[0]]]
        elif len(s1) == 1 and len(s2) == 1:
            new_points = [[single_index, s2[0], s1[0]]]
        elif len(s0) == 1 and len(s2) == 1:
            new_points = [[single_index, s0[0], s2[0]]]
    return new_points


def scalars_to_fields(scalars):
    scalars = np.array(scalars)
    if len(scalars.shape) == 1:
        return [tfields.Tensors(scalars)]
    return [tfields.Tensors(fs) for fs in scalars]


def fields_to_scalars(fields):
    return np.array(fields)


def faces_to_maps(faces, *fields):
    return [tfields.TensorFields(faces, *fields, dtype=int, dim=3)]


def maps_to_faces(maps):
    if len(maps) == 0:
        return np.array([])
    elif len(maps) > 1:
        raise NotImplementedError("Multiple maps")
    return np.array(maps[0])


class Mesh3D(tfields.TensorMaps):
    # pylint: disable=R0904
    """
    Points3D child used as vertices combined with faces to build a geometrical mesh of triangles
    Examples:
        >>> import tfields
        >>> import numpy as np
        >>> m = tfields.Mesh3D([[1,2,3], [3,3,3], [0,0,0], [5,6,7]], faces=[[0, 1, 2], [1, 2, 3]])
        >>> m.equal([[1, 2, 3],
        ...          [3, 3, 3],
        ...          [0, 0, 0],
        ...          [5, 6, 7]])
        True
        >>> np.array_equal(m.faces, [[0, 1, 2], [1, 2, 3]])
        True

        conversion to points only
        >>> tfields.Points3D(m).equal([[1, 2, 3],
        ...                            [3, 3, 3],
        ...                            [0, 0, 0],
        ...                            [5, 6, 7]])
        True

        Empty instances
        >>> m = tfields.Mesh3D([]);

        going from Mesh3D to Triangles3D instance is easy and will be cached.
        >>> m = tfields.Mesh3D([[1,0,0], [0,1,0], [0,0,0]], faces=[[0, 1, 2]]);
        >>> assert m.triangles().equal(tfields.Triangles3D([[ 1.,  0.,  0.],
        ...                                               [ 0.,  1.,  0.],
        ...                                               [ 0.,  0.,  0.]]))

        a list of scalars is assigned to each face
        >>> mScalar = tfields.Mesh3D([[1,0,0], [0,1,0], [0,0,0]], faces=[[0, 1, 2]], faceScalars=[.5]);
        >>> np.array_equal(mScalar.faceScalars, [[ 0.5]])
        True

        adding together two meshes:
        >>> m2 = tfields.Mesh3D([[1,0,0],[2,0,0],[0,3,0]],
        ...                     faces=[[0,1,2]], faceScalars=[.7])
        >>> msum = tfields.Mesh3D.merged(mScalar, m2)
        >>> msum.equal([[ 1.,  0.,  0.],
        ...             [ 0.,  1.,  0.],
        ...             [ 0.,  0.,  0.],
        ...             [ 1.,  0.,  0.],
        ...             [ 2.,  0.,  0.],
        ...             [ 0.,  3.,  0.]])
        True
        >>> assert np.array_equal(msum.faces, [[0, 1, 2], [3, 4, 5]])

        Saving and reading
        >>> from tempfile import NamedTemporaryFile
        >>> outFile = NamedTemporaryFile(suffix='.npz')
        >>> m.save(outFile.name)
        >>> _ = outFile.seek(0)
        >>> m1 = tfields.Mesh3D.load(outFile.name)
        >>> bool(np.all(m == m1))
        True
        >>> m1.faces
        array([[0, 1, 2]])

    """
    def __new__(cls, tensors, *fields, **kwargs):
        if not issubclass(type(tensors), Mesh3D):
            kwargs['dim'] = 3
        faces = kwargs.pop('faces', None)
        faceScalars = kwargs.pop('faceScalars', [])
        maps = kwargs.pop('maps', None)
        if maps is not None and faces is not None:
            raise ValueError("Conflicting options maps and faces")
        if maps is not None:
            kwargs['maps'] = maps
        if len(faceScalars) > 0:
            map_fields = scalars_to_fields(faceScalars)
        else:
            map_fields = []
        if faces is not None:
            kwargs['maps'] = faces_to_maps(faces,
                                           *map_fields)
        obj = super(Mesh3D, cls).__new__(cls, tensors, *fields, **kwargs)
        if len(obj.maps) > 1:
            raise ValueError("Mesh3D only allows one map")
        if obj.maps and obj.maps[0].dim != 3:
            raise ValueError("Face dimension should be 3")
        return obj

    @classmethod
    def plane(cls, *base_vectors, **kwargs):
        """
        Alternative constructor for creating a plane from
        Args:
            *base_vectors: see grid constructors in core. One base_vector has to
                be one-dimensional
            **kwargs: forwarded to __new__
        """
        vertices = tfields.Tensors.grid(*base_vectors)

        base_vectors = tfields.grid.ensure_complex(*base_vectors)
        base_vectors = tfields.grid.to_base_vectors(*base_vectors)
        fix_coord = None
        for coord in range(3):
            if len(base_vectors[coord]) > 1:
                continue
            if len(base_vectors[coord]) == 0:
                continue
            fix_coord = coord
        if fix_coord is None:
            raise ValueError("Describe a plane with one variable fiexed")

        var_coords = list(range(3))
        var_coords.pop(var_coords.index(fix_coord))

        faces = []
        base0, base1 = base_vectors[var_coords[0]], base_vectors[var_coords[1]]
        for i1 in range(len(base1) - 1):
            for i0 in range(len(base0) - 1):
                idx_top_left = len(base1) * (i0 + 0) + (i1 + 0)
                idx_top_right = len(base1) * (i0 + 0) + (i1 + 1)
                idx_bot_left = len(base1) * (i0 + 1) + (i1 + 0)
                idx_bot_right = len(base1) * (i0 + 1) + (i1 + 1)
                faces.append([idx_top_left, idx_top_right, idx_bot_left])
                faces.append([idx_top_right, idx_bot_left, idx_bot_right])
        inst = cls.__new__(cls, vertices, faces=faces, **kwargs)
        return inst

    @classmethod
    def grid(cls, *base_vectors, **kwargs):
        """
        Construct 'cuboid' along base_vectors
        """
        if not len(base_vectors) == 3:
            raise AttributeError("3 base_vectors vectors required")

        base_vectors = tfields.grid.ensure_complex(*base_vectors)
        base_vectors = tfields.grid.to_base_vectors(*base_vectors)

        indices = [0, -1]
        coords = range(3)
        baseLengthsAbove1 = [len(b) > 1 for b in base_vectors]
        # if one plane is given: rearrange indices and coords
        if not all(baseLengthsAbove1):
            indices = [0]
            for i, b in enumerate(baseLengthsAbove1):
                if not b:
                    coords = [i]
                    break

        base_vectors = list(base_vectors)
        planes = []
        for ind in indices:
            for coord in coords:
                basePart = base_vectors[:]
                basePart[coord] = np.array([base_vectors[coord][ind]],
                                           dtype=float)

                planes.append(cls.plane(*basePart))
        inst = cls.merged(*planes, **kwargs)
        return inst

    @property
    def faces(self):
        return maps_to_faces(self.maps)

    @faces.setter
    def faces(self, faces):
        self.maps = faces_to_maps(faces)

    @property
    def faceScalars(self):
        return fields_to_scalars(self.maps[0].fields)

    @faceScalars.setter
    def faceScalars(self, scalars):
        self.maps[0].fields = scalars_to_fields(scalars)

    @cached_property()
    def _triangles(self):
        """
        with the decorator, this should be handled like an attribute though it is a function

        """
        if self.faces.size == 0:
            return tfields.Triangles3D([])
        tris = tfields.Tensors.merged(*[self[mp.flatten()] for mp in self.maps])
        map_fields = [mp.fields for mp in self.maps]
        fields = [tfields.Tensors.merged(*fields) for fields in zip(*map_fields)]
        return tfields.Triangles3D(tris, *fields)

    def triangles(self):
        return self._triangles

    def centroids(self):
        return self.triangles().centroids()

    @cached_property()
    def _planes(self):
        if self.faces.size == 0:
            return tfields.Planes3D([])
        return tfields.Planes3D(self.centroids(), self.triangles().norms())

    def planes(self):
        return self._planes

    def nfaces(self):
        return self.faces.shape[0]

    def in_faces(self, points, delta, assign_multiple=False):
        """
        Check whether points lie within triangles with Barycentric Technique
        """
        masks = self.triangles().in_triangles(points, delta,
                                            assign_multiple=assign_multiple)
        return masks

    def removeFaces(self, faceDeleteMask):
        """
        Remove faces where faceDeleteMask is True
        """
        faceDeleteMask = np.array(faceDeleteMask, dtype=bool)
        self.faces = self.faces[~faceDeleteMask]
        self.faceScalars = self.faceScalars[~faceDeleteMask]

    def template(self, sub_mesh, delta=1e-9):
        """
        'Manual' way to build a template that can be used with self.cut
        Returns:
            Mesh3D: template (see cut), can be used as template to retrieve
                sub_mesh from self instance
        Examples:
            >>> mp = tfields.TensorFields([[0,1,2],[2,3,0],[3,2,5],[5,4,3]],
            ...                           [1, 2, 3, 4])
            >>> m = tfields.Mesh3D([[0,0,0], [1,0,0], [1,1,0], [0,1,0], [0,2,0], [1,2,0]],
            ...                     maps=[mp])
            >>> from sympy.abc import y
            >>> m_cut = m.cut(y < 1.5, at_intersection='split')
            >>> template = m.template(m_cut)
            >>> assert m_cut.equal(m.cut(template))

        TODO:
            fields template not yet implemented
        """
        face_indices = np.arange(self.maps[0].shape[0])
        cents = tfields.Tensors(sub_mesh.centroids())
        scalars = []
        mask = self.in_faces(cents, delta=delta)
        scalars = []
        for face_mask in mask:
            scalars.append(face_indices[face_mask][0])
        inst = sub_mesh.copy()
        inst.maps[0].fields = [tfields.Tensors(scalars)]
        return inst

    def _cut_sympy(self, expression, at_intersection="remove", _in_recursion=False):
        """
        Partition the mesh with the cuts given and return the template

        """
        eps = 0.000000001
        # direct return if self is empty
        if len(self) == 0:
            return self.copy(), self.copy()

        inst = self.copy()

        '''
        add the indices of the vertices and maps to the fields. They will be
        removed afterwards
        '''
        if not _in_recursion:
            inst.fields.append(tfields.Tensors(np.arange(len(inst))))
            for mp in inst.maps:
                mp.fields.append(tfields.Tensors(np.arange(len(mp))))

        # mask for points that do not fulfill the cut expression
        mask = inst.evalf(expression)
        # remove the points

        if not any(~mask) or all(~mask):
            inst = inst[mask]
        elif at_intersection == 'split' or at_intersection == 'splitRough':
            '''
            add vertices and faces that are at the border of the cuts
            '''
            expression_parts = tfields.lib.symbolics.split_expression(expression)
            if len(expression_parts) > 1:
                new_mesh = inst.copy()
                if at_intersection == 'splitRough':
                    """
                    the following is, to speed up the process. Problem is, that
                    triangles can exist, where all points lie outside the cut,
                    but part of the area
                    still overlaps with the cut.
                    These are at the intersection line between two cuts.
                    """
                    faceIntersMask = np.full((inst.faces.shape[0]), False, dtype=bool)
                    for i, face in enumerate(inst.faces):
                        vertices_rejected = [-mask[f] for f in face]
                        face_on_edge = any(vertices_rejected) and not all(vertices_rejected)
                        if face_on_edge:
                            faceIntersMask[i] = True
                    new_mesh.removeFaces(-faceIntersMask)

                for exprPart in expression_parts:
                    inst, _ = inst._cut_sympy(exprPart,
                                              at_intersection='split',
                                              _in_recursion=True)
            elif len(expression_parts) == 1:
                # TODO maps[0] -> smthng like inst.get_map(dim=3)
                points = [sympy.symbols('x0, y0, z0'),
                          sympy.symbols('x1, y1, z1'),
                          sympy.symbols('x2, y2, z2')]
                plane_sympy = tfields.lib.symbolics.to_plane(expression)
                norm_sympy = np.array(plane_sympy.normal_vector).astype(float)
                d = -norm_sympy.dot(np.array(plane_sympy.p1).astype(float))
                plane = {'normal': norm_sympy, 'd': d}

                norm_vectors = inst.triangles().norms()
                new_points = np.empty((0, 3))
                new_faces = np.empty((0, 3))
                new_fields = [tfields.Tensors(np.empty((0,) + field.shape[1:]),
                                              coordSys=field.coordSys)
                              for field in inst.fields]
                new_map_fields = [[] for field in inst.maps[0].fields]
                new_norm_vectors = []
                newScalarMap = []
                n_new = 0

                vertices = np.array(inst)
                faces = np.array(inst.maps[0])
                fields = [np.array(field) for field in inst.fields]
                faces_fields = [np.array(field) for field in inst.maps[0].fields]

                face_delete_indices = set([])
                for i, face in enumerate(inst.maps[0]):
                    """
                    vertices_rejected is a mask for each face that is True, where
                    a Point is on the rejected side of the plane
                    """
                    vertices_rejected = [~mask[f] for f in face]
                    if any(vertices_rejected):
                        # delete face
                        face_delete_indices.add(i)
                    if any(vertices_rejected) and not all(vertices_rejected):
                        # face on edge
                        nTrue = vertices_rejected.count(True)
                        lonely_bool = True if nTrue == 1 else False

                        triangle_points = [inst[f] for f in face]
                        """
                        Add the intersection points and faces
                        """
                        newP = _intersect(triangle_points, plane, vertices_rejected)
                        last_idx = len(vertices) - 1
                        for tri_list in newP:
                            new_face = []
                            for item in tri_list:
                                if isinstance(item, int):
                                    # reference to old vertex
                                    new_face.append(face[item])
                                elif isinstance(item, complex):
                                    # reference to new vertex that has been
                                    # concatenated already
                                    new_face.append(last_idx + int(item.imag))
                                else:
                                    # new vertex
                                    new_face.append(len(vertices))
                                    vertices = np.append(vertices,
                                                         [map(float, item)],
                                                         axis=0)
                                    fields = [np.append(field,
                                                        np.full((1,) + field.shape[1:], np.nan),
                                                        axis=0)
                                              for field in fields]
                            faces = np.append(faces, [new_face], axis=0)
                            faces_fields = [np.append(field,
                                                      [field[i]],
                                                      axis=0)
                                            for field in faces_fields]
                            faces_fields[-1][-1] = i

                face_map = tfields.TensorFields(faces, *faces_fields,
                                                dtype=int,
                                                coordSys=inst.maps[0].coordSys)
                inst = tfields.Mesh3D(vertices,
                                      *fields,
                                      maps=[face_map] + inst.maps[1:],
                                      coordSys=inst.coordSys)
                mask = np.full(len(inst.maps[0]), True, dtype=bool)
                for face_idx in range(len(inst.maps[0])):
                    if face_idx in face_delete_indices:
                        mask[face_idx] = False
                inst.maps[0] = inst.maps[0][mask]
            else:
                raise ValueError("Sympy expression is not splitable.")
            inst = inst.cleaned()
        elif at_intersection == 'remove':
            inst = inst[mask]
        else:
            raise AttributeError("No at_intersection method called {at_intersection} "
                                 "implemented".format(**locals()))

        if _in_recursion:
            template = None
        else:
            template_field = inst.fields.pop(-1)
            template_maps = []
            for mp in inst.maps:
                t_mp = tfields.TensorFields(tfields.Tensors(mp),
                                            mp.fields.pop(-1))
                template_maps.append(t_mp)
            template = tfields.Mesh3D(tfields.Tensors(inst),
                                      template_field,
                                      maps=template_maps)
        return inst, template

    def _cut_template(self, template):
        """
        Args:
            template (tfields.Mesh3D)

        Examples:
            >>> import tfields
            >>> import numpy as np

            Build mesh
            >>> mmap = tfields.TensorFields([[0, 1, 2], [0, 3, 4]],
            ...                             [[42, 21], [-42, -21]])
            >>> m = tfields.Mesh3D([[0]*3, [1]*3, [2]*3, [3]*3, [4]*3],
            ...                    [0.0, 0.1, 0.2, 0.3, 0.4],
            ...                    [0.0, -0.1, -0.2, -0.3, -0.4],
            ...                    maps=[mmap])

            Build template
            >>> tmap = tfields.TensorFields([[0, 3, 4], [0, 1, 2]],
            ...                             [1, 0])
            >>> t = tfields.Mesh3D([[0]*3, [-1]*3, [-2]*3, [-3]*3, [-4]*3],
            ...                    [1, 0, 3, 2, 4],
            ...                    maps=[tmap])

            Use template as instruction to make a fast cut
            >>> res = m._cut_template(t)
            >>> assert np.array_equal(res.fields,
            ...                       [[0.1, 0.0, 0.3, 0.2, 0.4],
            ...                        [-0.1, 0.0, -0.3, -0.2, -0.4]])

            >>> assert np.array_equal(res.maps[0].fields[0],
            ...                       [[-42, -21], [42, 21]])
                                   
        """
        # Redirect fields
        fields = []
        if template.fields:
            template_field = np.array(template.fields[0])
            if len(self) > 0:
                '''
                if new vertices have been created in the template, it is
                in principle unclear what fields we have to refer to.
                Thus in creating the template, we gave np.nan.
                To make it fast, we replace nan with 0 as a dummy and correct
                the field entries afterwards with np.nan.
                '''
                nan_mask = np.isnan(template_field)
                template_field[nan_mask] = 0  # dummy reference to index 0.
                template_field = template_field.astype(int)
                for field in self.fields:
                    projected_field = field[template_field]
                    projected_field[nan_mask] = np.nan  # correction for nan
                    fields.append(projected_field)

        # Redirect maps fields
        maps = []
        for mp, template_mp in zip(self.maps, template.maps):
            mp_fields = []
            if len(template_mp.fields) > 0:
                for field in mp.fields:
                    mp_fields.append(field[template_mp.fields[0].astype(int)])
            new_mp = tfields.TensorFields(tfields.Tensors(template_mp),
                                          *mp_fields)
            maps.append(new_mp)

        inst = tfields.Mesh3D(tfields.Tensors(template),
                              *fields,
                              maps=maps)
        return inst

    def cut(self, expression, coordSys=None, at_intersection=None,
            return_template=False):
        """
        cut method for Mesh3D.
        Args:
            expression (sympy logical expression | Mesh3D):
                sympy locical expression: Sympy expression that defines planes
                    in 3D
                Mesh3D: A mesh3D will be interpreted as a template, i.e. a
                    fast instruction of how to cut the triangles.
                    It is the second part of the tuple, returned by a previous
                    cut with a sympy locial expression with 'return_template=True'.
                    We use the vertices and maps of the Mesh as the sceleton of
                    the returned mesh. The fields are mapped according to
                    indices in the template.maps[i].fields.
            coordSys (coordinate system to cut in):
            at_intersection (str): instruction on what to do, when a cut will intersect a triangle.
                Options:    "remove" (Default)
                            "split" - Create new triangles that make up the old one.
            return_template (bool): If True: return the template
                            to redo the same cut fast
        Examples:
            define the cut
            >>> import tfields
            >>> from sympy.abc import x,y,z
            >>> cutExpr = x > 1.5

            >>> m = tfields.Mesh3D.grid((0, 3, 4),
            ...                         (0, 3, 4),
            ...                         (0, 0, 1))
            >>> m.fields.append(tfields.Tensors(np.linspace(0, len(m) - 1,
            ...                                             len(m))))
            >>> m.maps[0].fields.append(
            ...     tfields.Tensors(np.linspace(0,
            ...                                 len(m.maps[0]) - 1,
            ...                                 len(m.maps[0]))))
            >>> mNew = m.cut(cutExpr)
            >>> len(mNew)
            8
            >>> mNew.nfaces()
            6
            >>> float(mNew[:, 0].min())
            2.0

            Cutting with the split option will create new triangles on the edge:
            >>> m_split = m.cut(cutExpr, at_intersection='split')
            >>> float(m_split[:, 0].min())
            1.5
            >>> len(m_split)
            15
            >>> m_split.nfaces()
            15

            Cut with 'return_template=True' will return the exact same mesh but
            additionally an instruction to conduct the exact same cut fast (template)
            >>> m_split_2, template = m.cut(cutExpr, at_intersection='split',
            ...                                    return_template=True)
            >>> m_split_template = m.cut(template)
            >>> assert m_split.equal(m_split_2, equal_nan=True)
            >>> assert m_split.equal(m_split_template, equal_nan=True)
            >>> assert len(template.fields) == 1
            >>> assert len(m_split.fields) == 1
            >>> assert len(m_split_template.fields) == 1
            >>> assert m_split.fields[0].equal(
            ...     list(range(8, 16)) + [np.nan] * 7, equal_nan=True)
            >>> assert m_split_template.fields[0].equal(
            ...     list(range(8, 16)) + [np.nan] * 7, equal_nan=True)

            This seems irrelevant at first but Consider, the map field or the
            tensor field changes:
            >>> m_altered_fields = m.copy()
            >>> m_altered_fields[0] += 42
            >>> assert not m_split.equal(m_altered_fields.cut(template))
            >>> assert tfields.Tensors(m_split).equal(m_altered_fields.cut(template))
            >>> assert tfields.Tensors(m_split.maps[0]).equal(m_altered_fields.cut(template).maps[0])


            The cut expression may be a sympy.BooleanFunction:
            >>> cut_expr_bool_fun = (x > 1.5) & (y < 1.5) & (y >0.2) & (z > -0.5)
            >>> m_split_bool = m.cut(cut_expr_bool_fun, at_intersection='split')

        Returns:
            copy of cut mesh
            * optional: template

        """
        with self.tmp_transform(coordSys or self.coordSys):
            if isinstance(expression, Mesh3D):
                obj = self._cut_template(expression)
            else:
                at_intersection = at_intersection or "remove"
                obj, template = self._cut_sympy(expression, at_intersection=at_intersection)
        if return_template:
            return obj, template
        return obj

    def plot(self, **kwargs):  # pragma: no cover
        """
        Forwarding to plotTools.plotMesh
        """
        scalars_demanded = any([v in kwargs for v in ['vmin', 'vmax', 'cmap']])
        map_index = kwargs.pop('map_index', None if not scalars_demanded else 0)
        if map_index is not None:
            if not len(self.maps[0]) == 0:
                kwargs['color'] = self.maps[0].fields[map_index]

        dim_defined = False
        if 'axis' in kwargs:
            dim_defined = True
        if 'zAxis' in kwargs:
            if kwargs['zAxis'] is not None:
                kwargs['dim'] = 3
            else:
                kwargs['dim'] = 2
            dim_defined = True
        if 'dim' in kwargs:
            dim_defined = True

        if not dim_defined:
            kwargs['dim'] = 2

        return tfields.plotting.plotMesh(self, self.faces, **kwargs)


if __name__ == '__main__':  # pragma: no cover
    import doctest

    # doctest.run_docstring_examples(Mesh3D.cut, globals())
    doctest.testmod()
