# coding: utf-8
"""Grid Parameters with instructions for generating SensorGrids."""
from __future__ import division

from ladybug_geometry.geometry3d import Vector3D
from honeybee.typing import float_in_range, float_positive, int_positive, valid_string
from honeybee.altnumber import autocalculate


class _GridParameterBase(object):
    """Base object for all GridParameters.

    This object records all of the methods that must be overwritten on a grid
    parameter object for it to be successfully be applied in dragonfly workflows.

    Args:
        dimension: The dimension of the grid cells as a number.
        offset: A number for how far to offset the grid from the base
            geometries. (Default: 0).
        include_mesh: A boolean to note whether the resulting SensorGrid should
            include the mesh. (Default: True).
    """
    __slots__ = ('_dimension', '_offset', '_include_mesh')

    def __init__(self, dimension, offset=0, include_mesh=True):
        self._dimension = float_positive(dimension, 'grid dimension')
        self._offset = float_in_range(offset, input_name='grid offset')
        self._include_mesh = bool(include_mesh)

    @property
    def dimension(self):
        """Get a number for the dimension of the grid cells."""
        return self._dimension

    @property
    def offset(self):
        """Get a number for how far to offset the grid from the base geometries."""
        return self._offset

    @property
    def include_mesh(self):
        """Get a boolean for whether the resulting SensorGrid should include the mesh."""
        return self._include_mesh

    def generate_grid_from_room(self, honeybee_room):
        """Get a SensorGrid from a Honeybee Room using these GridParameter.

        Args:
            honeybee_room: A Honeybee Room to which these grid parameters
                are applied.

        Returns:
            A honeybee-radiance SensorGrid generated from the Honeybee Room.
        """
        pass

    def scale(self, factor):
        """Get a scaled version of these GridParameters.

        This method is called within the scale methods of the Room2D.

        Args:
            factor: A number representing how much the object should be scaled.
        """
        return _GridParameterBase(
            self.dimension * factor, self.offset * factor, self.include_mesh)

    @classmethod
    def from_dict(cls, data):
        """Create GridParameterBase from a dictionary.

        .. code-block:: python

            {
            "type": "GridParameterBase",
            "dimension": 0.5,
            "offset": 1.0,
            "include_mesh": True
            }
        """
        assert data['type'] == 'GridParameterBase', \
            'Expected GridParameterBase dictionary. Got {}.'.format(data['type'])
        offset = data['offset'] \
            if 'offset' in data and data['offset'] is not None else 0
        include_mesh = data['include_mesh'] \
            if 'include_mesh' in data and data['include_mesh'] is not None else True
        return cls(data['dimension'], offset, include_mesh)

    def to_dict(self):
        """Get GridParameterBase as a dictionary."""
        base = {
            'type': 'GridParameterBase',
            'dimension': self.dimension,
            'offset': self.offset
        }
        if not self.include_mesh:
            base['include_mesh'] = self.include_mesh
        return base

    def duplicate(self):
        """Get a copy of this object."""
        return self.__copy__()

    def ToString(self):
        return self.__repr__()

    def __copy__(self):
        return _GridParameterBase(self.dimension, self.offset, self.include_mesh)

    def __repr__(self):
        return 'GridParameterBase'


class RoomGridParameter(_GridParameterBase):
    """Instructions for a SensorGrid generated from a Room2D's floors.

    The resulting grid will have the room referenced in its room_identifier
    property. Note that the grid is generated within the XY coordinate system
    of the Room2D's floor_geometry. So rotating the plane of this geometry will
    will result in rotated grid cells.

    Args:
        dimension: The dimension of the grid cells as a number.
        offset: A number for how far to offset the grid from the base
            geometries. (Default: 1, suitable for Rooms in Meters).
        wall_offset: A number for the distance at which sensors close to walls
            should be removed. Note that this option has no effect unless the
            value is more than half of the dimension. (Default: 0).
        include_mesh: A boolean to note whether the resulting SensorGrid should
            include the mesh. (Default: True).
    """
    __slots__ = ('_wall_offset',)

    def __init__(self, dimension, offset=1.0, wall_offset=0, include_mesh=True):
        _GridParameterBase.__init__(self, dimension, offset, include_mesh)
        self._wall_offset = float_positive(wall_offset, 'grid wall offset')

    @property
    def wall_offset(self):
        """Get a number for the distance at which sensors near walls should be removed.
        """
        return self._wall_offset

    def generate_grid_from_room(self, honeybee_room):
        """Get a SensorGrid from a Honeybee Room using these GridParameter.

        Args:
            honeybee_room: A Honeybee Room to which these grid parameters are applied.

        Returns:
            A honeybee-radiance SensorGrid generated from the Honeybee Room. Will
            be None if a valid Grid cannot be generated from the Room.
        """
        ftc_h = honeybee_room.max.z - honeybee_room.min.z
        if self.offset >= ftc_h:
            return None
        s_grid = honeybee_room.properties.radiance.generate_sensor_grid(
            self.dimension, offset=self.offset, wall_offset=self.wall_offset)
        if not self.include_mesh and s_grid is not None:
            s_grid.mesh = None
        return s_grid

    def scale(self, factor):
        """Get a scaled version of these GridParameters.

        This method is called within the scale methods of the Room2D.

        Args:
            factor: A number representing how much the object should be scaled.
        """
        return RoomGridParameter(
            self.dimension * factor, self.offset * factor,
            self.wall_offset * factor, self.include_mesh)

    @classmethod
    def from_dict(cls, data):
        """Create RoomGridParameter from a dictionary.

        .. code-block:: python

            {
            "type": "RoomGridParameter",
            "dimension": 0.5,
            "offset": 1.0,
            "wall_offset": 0.5,
            "include_mesh": True
            }
        """
        assert data['type'] == 'RoomGridParameter', \
            'Expected RoomGridParameter dictionary. Got {}.'.format(data['type'])
        offset = data['offset'] \
            if 'offset' in data and data['offset'] is not None else 1.0
        wall_offset = data['wall_offset'] \
            if 'wall_offset' in data and data['wall_offset'] is not None else 0
        include_mesh = data['include_mesh'] \
            if 'include_mesh' in data and data['include_mesh'] is not None else True
        return cls(data['dimension'], offset, wall_offset, include_mesh)

    def to_dict(self):
        """Get RoomGridParameter as a dictionary."""
        base = {
            'type': 'RoomGridParameter',
            'dimension': self.dimension,
            'offset': self.offset
        }
        if self.wall_offset != 0:
            base['wall_offset'] = self.wall_offset
        if not self.include_mesh:
            base['include_mesh'] = self.include_mesh
        return base

    def duplicate(self):
        """Get a copy of this object."""
        return self.__copy__()

    def ToString(self):
        return self.__repr__()

    def __copy__(self):
        return RoomGridParameter(
            self.dimension, self.offset, self.wall_offset, self.include_mesh)

    def __repr__(self):
        return 'RoomGridParameter [dimension: {}] [offset: {}]'.format(
            self.dimension, self.offset)


class RoomRadialGridParameter(RoomGridParameter):
    """Instructions for a SensorGrid of radial directions around positions from floors.

    This type of sensor grid is particularly helpful for studies of multiple
    view directions, such as imageless glare studies.

    The resulting grid will have the room referenced in its room_identifier
    property. Note that the grid is generated within the XY coordinate system
    of the Room2D's floor_geometry. So rotating the plane of this geometry will
    will result in rotated grid cells.

    Args:
        dimension: The dimension of the grid cells as a number.
        offset: A number for how far to offset the grid from the base
            geometries. (Default: 1.2, suitable for Rooms in Meters).
        wall_offset: A number for the distance at which sensors close to walls
            should be removed. Note that this option has no effect unless the
            value is more than half of the x_dim or y_dim. (Default: 0).
        dir_count: A positive integer for the number of radial directions
            to be generated around each position. (Default: 8).
        start_vector: A Vector3D to set the start direction of the generated
            directions. This can be used to orient the resulting sensors to
            specific parts of the scene. It can also change the elevation of the
            resulting directions since this start vector will always be rotated in
            the XY plane to generate the resulting directions. (Default: (0, -1, 0)).
        mesh_radius: An optional number to override the radius of the meshes
            generated around each sensor. If None or autocalculate, it will be
            equal to 45% of the grid dimension. (Default: None).
        include_mesh: A boolean to note whether the resulting SensorGrid should
            include the mesh. (Default: True).
    """
    __slots__ = ('_dir_count', '_start_vector', '_mesh_radius')

    def __init__(self, dimension, offset=1.2, wall_offset=0, dir_count=8,
                 start_vector=Vector3D(0, -1, 0), mesh_radius=None, include_mesh=True):
        RoomGridParameter.__init__(self, dimension, offset, wall_offset, include_mesh)
        self._dir_count = int_positive(dir_count, 'radial grid dir count')
        assert self._dir_count != 0, 'Radial grid dir count must not be equal to 0.'
        assert isinstance(start_vector, Vector3D), 'Expected Vector3D for radial ' \
            'grid start_vector. Got {}.'.format(type(start_vector))
        self._start_vector = start_vector
        if mesh_radius == autocalculate:
            mesh_radius = None
        elif mesh_radius is not None:
            mesh_radius = float_positive(mesh_radius, 'radial grid mesh_radius')
        self._mesh_radius = mesh_radius

    @property
    def dir_count(self):
        """Get an integer for the number of radial directions around each position.
        """
        return self._dir_count

    @property
    def start_vector(self):
        """Get a Vector3D that sets the start direction of the generated directions.
        """
        return self._start_vector

    @property
    def mesh_radius(self):
        """Get a number that sets the radius of the meshes generated around each sensor.

        If None or autocalculate, it will be equal to 45% of the grid dimension.
        """
        return self._mesh_radius

    def generate_grid_from_room(self, honeybee_room):
        """Get a SensorGrid from a Honeybee Room using these GridParameter.

        Args:
            honeybee_room: A Honeybee Room to which these grid parameters are applied.

        Returns:
            A honeybee-radiance SensorGrid generated from the Honeybee Room. Will
            be None if a valid Grid cannot be generated from the Room.
        """
        ftc_h = honeybee_room.max.z - honeybee_room.min.z
        if self.offset >= ftc_h:
            return None
        m_rad = self.mesh_radius if self.include_mesh else 0
        s_grid = honeybee_room.properties.radiance.generate_sensor_grid_radial(
            self.dimension, offset=self.offset, wall_offset=self.wall_offset,
            dir_count=self.dir_count, start_vector=self.start_vector, mesh_radius=m_rad)
        return s_grid

    def scale(self, factor):
        """Get a scaled version of these GridParameters.

        This method is called within the scale methods of the Room2D.

        Args:
            factor: A number representing how much the object should be scaled.
        """
        m_rad = self.mesh_radius * factor if self.mesh_radius is not None else None
        return RoomRadialGridParameter(
            self.dimension * factor, self.offset * factor,
            self.wall_offset * factor, self.dir_count,
            self.start_vector, m_rad, self.include_mesh)

    @classmethod
    def from_dict(cls, data):
        """Create RoomRadialGridParameter from a dictionary.

        .. code-block:: python

            {
            "type": "RoomRadialGridParameter",
            "dimension": 1.0,
            "offset": 1.2,
            "wall_offset": 1.0,
            "dir_count": 8,
            "start_vector": (0, -1, 0),
            "mesh_radius": 0.5,
            "include_mesh": True
            }
        """
        assert data['type'] == 'RoomRadialGridParameter', \
            'Expected RoomRadialGridParameter dictionary. Got {}.'.format(data['type'])
        offset = data['offset'] \
            if 'offset' in data and data['offset'] is not None else 1.2
        wall_offset = data['wall_offset'] \
            if 'wall_offset' in data and data['wall_offset'] is not None else 0
        dir_count = data['dir_count'] \
            if 'dir_count' in data and data['dir_count'] is not None else 8
        start_vector = Vector3D.from_array(data['start_vector']) if 'start_vector' \
            in data and data['start_vector'] is not None else Vector3D(0, -1, 0)
        mesh_radius = data['mesh_radius'] if 'mesh_radius' in data and \
            data['mesh_radius'] != autocalculate.to_dict() else None
        include_mesh = data['include_mesh'] \
            if 'include_mesh' in data and data['include_mesh'] is not None else True
        return cls(data['dimension'], offset, wall_offset, dir_count, start_vector,
                   mesh_radius, include_mesh)

    def to_dict(self):
        """Get RoomRadialGridParameter as a dictionary."""
        base = {
            'type': 'RoomRadialGridParameter',
            'dimension': self.dimension,
            'offset': self.offset,
            'dir_count': self.dir_count,
            'start_vector': self.start_vector.to_array()
        }
        if self.mesh_radius is not None:
            base['mesh_radius'] = self.mesh_radius
        if self.wall_offset != 0:
            base['wall_offset'] = self.wall_offset
        if not self.include_mesh:
            base['include_mesh'] = self.include_mesh
        return base

    def duplicate(self):
        """Get a copy of this object."""
        return self.__copy__()

    def ToString(self):
        return self.__repr__()

    def __copy__(self):
        return RoomRadialGridParameter(
            self.dimension, self.offset, self.wall_offset, self.dir_count,
            self.start_vector, self.mesh_radius, self.include_mesh)

    def __repr__(self):
        return 'RoomRadialGridParameter [dimension: {}] [offset: {}]'.format(
            self.dimension, self.offset)


class ExteriorFaceGridParameter(_GridParameterBase):
    """Instructions for a SensorGrid generated from exterior Faces.

    Args:
        dimension: The dimension of the grid cells as a number.
        offset: A number for how far to offset the grid from the base
            geometries. (Default: 0.1, suitable for Rooms in Meters).
        face_type: Text to specify the type of face that will be used to
            generate grids. Note that only Faces with Outdoors boundary
            conditions will be used, meaning that most Floors will typically
            be excluded unless they represent the underside of a cantilever.
            Choose from the following. (Default: Wall).

            * Wall
            * Roof
            * Floor
            * All

        punched_geometry: Boolean to note whether the punched_geometry of the faces
            should be used (True) with the areas of sub-faces removed from the grid
            or the full geometry should be used (False). (Default:False).
        include_mesh: A boolean to note whether the resulting SensorGrid should
            include the mesh. (Default: True).
    """
    __slots__ = ('_face_type', '_punched_geometry')
    FACE_TYPES = ('Wall', 'Roof', 'Floor', 'All')

    def __init__(self, dimension, offset=0.1, face_type='Wall', punched_geometry=False,
                 include_mesh=True):
        _GridParameterBase.__init__(self, dimension, offset, include_mesh)
        clean_face_type = valid_string(face_type).lower()
        for key in self.FACE_TYPES:
            if key.lower() == clean_face_type:
                face_type = key
                break
        else:
            raise ValueError(
                'ExteriorFaceGrid face_type "{}" is not recognized.\nChoose from the '
                'following:\n{}'.format(face_type, self.FACE_TYPES))
        self._face_type = face_type
        self._punched_geometry = bool(punched_geometry)

    @property
    def face_type(self):
        """Get text to specify the type of face that will be used to generate grids.
        """
        return self._face_type

    @property
    def punched_geometry(self):
        """Get a boolean for whether the punched_geometry of the faces should be used.
        """
        return self._punched_geometry

    def generate_grid_from_room(self, honeybee_room):
        """Get a SensorGrid from a Honeybee Room using these GridParameter.

        Args:
            honeybee_room: A Honeybee Room to which these grid parameters are applied.

        Returns:
            A honeybee-radiance SensorGrid generated from the Honeybee Room. Will
            be None if the Room has no exterior Faces.
        """
        s_grid = honeybee_room.properties.radiance.generate_exterior_face_sensor_grid(
            self.dimension, offset=self.offset, face_type=self.face_type,
            punched_geometry=self.punched_geometry)
        if not self.include_mesh and s_grid is not None:
            s_grid.mesh = None
        return s_grid

    def scale(self, factor):
        """Get a scaled version of these GridParameters.

        This method is called within the scale methods of the Room2D.

        Args:
            factor: A number representing how much the object should be scaled.
        """
        return ExteriorFaceGridParameter(
            self.dimension * factor, self.offset * factor,
            self.face_type, self.punched_geometry, self.include_mesh)

    @classmethod
    def from_dict(cls, data):
        """Create ExteriorFaceGridParameter from a dictionary.

        .. code-block:: python

            {
            "type": "ExteriorFaceGridParameter",
            "dimension": 0.5,
            "offset": 0.15,
            "face_type": "Roof",
            "include_mesh": True
            }
        """
        assert data['type'] == 'ExteriorFaceGridParameter', \
            'Expected ExteriorFaceGridParameter dictionary. Got {}.'.format(data['type'])
        offset = data['offset'] \
            if 'offset' in data and data['offset'] is not None else 0.1
        face_type = data['face_type'] \
            if 'face_type' in data and data['face_type'] is not None else 'Wall'
        pg = data['punched_geometry'] if 'punched_geometry' in data \
            and data['punched_geometry'] is not None else False
        include_mesh = data['include_mesh'] \
            if 'include_mesh' in data and data['include_mesh'] is not None else True
        return cls(data['dimension'], offset, face_type, pg, include_mesh)

    def to_dict(self):
        """Get ExteriorFaceGridParameter as a dictionary."""
        base = {
            'type': 'ExteriorFaceGridParameter',
            'dimension': self.dimension,
            'offset': self.offset,
            'face_type': self.face_type
        }
        if self.punched_geometry:
            base['punched_geometry'] = self.punched_geometry
        if not self.include_mesh:
            base['include_mesh'] = self.include_mesh
        return base

    def duplicate(self):
        """Get a copy of this object."""
        return self.__copy__()

    def ToString(self):
        return self.__repr__()

    def __copy__(self):
        return ExteriorFaceGridParameter(
            self.dimension, self.offset, self.face_type,
            self.punched_geometry, self.include_mesh)

    def __repr__(self):
        return 'ExteriorFaceGridParameter [dimension: {}] [type: {}]'.format(
            self.dimension, self.face_type)


class ExteriorApertureGridParameter(_GridParameterBase):
    """Instructions for a SensorGrid generated from exterior Aperture.

    Args:
        dimension: The dimension of the grid cells as a number.
        offset: A number for how far to offset the grid from the base
            geometries. (Default: 0.1, suitable for Rooms in Meters).
        aperture_type: Text to specify the type of Aperture that will be used to
            generate grids. Window indicates Apertures in Walls. Skylights
            are in parent Roof faces. Choose from the following. (Default: All).

            * Window
            * Skylight
            * All

        include_mesh: A boolean to note whether the resulting SensorGrid should
            include the mesh. (Default: True).
    """
    __slots__ = ('_aperture_type',)
    APERTURE_TYPES = ('Window', 'Skylight', 'All')

    def __init__(self, dimension, offset=0.1, aperture_type='All', include_mesh=True):
        _GridParameterBase.__init__(self, dimension, offset, include_mesh)
        clean_ap_type = valid_string(aperture_type).lower()
        for key in self.APERTURE_TYPES:
            if key.lower() == clean_ap_type:
                aperture_type = key
                break
        else:
            raise ValueError(
                'ExteriorApertureGrid aperture_type "{}" is not recognized.\nChoose '
                'from the following:\n{}'.format(aperture_type, self.APERTURE_TYPES))
        self._aperture_type = aperture_type

    @property
    def aperture_type(self):
        """Get text to specify the type of face that will be used to generate grids.
        """
        return self._aperture_type

    def generate_grid_from_room(self, honeybee_room):
        """Get a SensorGrid from a Honeybee Room using these GridParameter.

        Args:
            honeybee_room: A Honeybee Room to which these grid parameters are applied.

        Returns:
            A honeybee-radiance SensorGrid generated from the Honeybee Room. Will
            be None if the object has no exterior Apertures.
        """
        s_g = honeybee_room.properties.radiance.generate_exterior_aperture_sensor_grid(
            self.dimension, offset=self.offset, aperture_type=self.aperture_type)
        if not self.include_mesh and s_g is not None:
            s_g.mesh = None
        return s_g

    def scale(self, factor):
        """Get a scaled version of these GridParameters.

        This method is called within the scale methods of the Room2D.

        Args:
            factor: A number representing how much the object should be scaled.
        """
        return ExteriorApertureGridParameter(
            self.dimension * factor, self.offset * factor,
            self.aperture_type, self.include_mesh)

    @classmethod
    def from_dict(cls, data):
        """Create ExteriorApertureGridParameter from a dictionary.

        .. code-block:: python

            {
            "type": "ExteriorApertureGridParameter",
            "dimension": 0.5,
            "offset": 0.15,
            "aperture_type": "Window",
            "include_mesh": True
            }
        """
        assert data['type'] == 'ExteriorApertureGridParameter', 'Expected ' \
            'ExteriorApertureGridParameter dictionary. Got {}.'.format(data['type'])
        offset = data['offset'] \
            if 'offset' in data and data['offset'] is not None else 0.1
        ap_type = data['aperture_type'] \
            if 'aperture_type' in data and data['aperture_type'] is not None else 'All'
        include_mesh = data['include_mesh'] \
            if 'include_mesh' in data and data['include_mesh'] is not None else True
        return cls(data['dimension'], offset, ap_type, include_mesh)

    def to_dict(self):
        """Get ExteriorApertureGridParameter as a dictionary."""
        base = {
            'type': 'ExteriorApertureGridParameter',
            'dimension': self.dimension,
            'offset': self.offset,
            'aperture_type': self.aperture_type
        }
        if not self.include_mesh:
            base['include_mesh'] = self.include_mesh
        return base

    def duplicate(self):
        """Get a copy of this object."""
        return self.__copy__()

    def ToString(self):
        return self.__repr__()

    def __copy__(self):
        return ExteriorApertureGridParameter(
            self.dimension, self.offset, self.aperture_type, self.include_mesh)

    def __repr__(self):
        return 'ExteriorApertureGridParameter [dimension: {}] [type: {}]'.format(
            self.dimension, self.aperture_type)
