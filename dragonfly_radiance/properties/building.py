# coding=utf-8
"""Building Radiance Properties."""
from honeybee_radiance.modifierset import ModifierSet
from honeybee_radiance.lib.modifiersets import generic_modifier_set_visible

import dragonfly_radiance.gridpar as sg_par


class BuildingRadianceProperties(object):
    """Radiance Properties for Dragonfly Building.

    Args:
        host: A dragonfly_core Building object that hosts these properties.
        modifier_set: A honeybee ModifierSet object to specify all default modifiers
            for the Story geometry. If None, it will be the honeybee default modifier
            set, which is only representative of typical indoor conditions in
            the visible spectrum. (Default: None).

    Properties:
        * host
        * modifier_set
    """
    __slots__ = ('_host', '_modifier_set')

    def __init__(self, host, modifier_set=None):
        """Initialize Building radiance properties."""
        self._host = host
        self.modifier_set = modifier_set

    @property
    def host(self):
        """Get the Building object hosting these properties."""
        return self._host

    @property
    def modifier_set(self):
        """Get or set the Building ModifierSet object.

        If not set, it will be the Honeybee default generic ModifierSet.
        """
        if self._modifier_set is not None:  # set by the user
            return self._modifier_set
        else:
            return generic_modifier_set_visible

    @modifier_set.setter
    def modifier_set(self, value):
        if value is not None:
            assert isinstance(value, ModifierSet), \
                'Expected ModifierSet. Got {}'.format(type(value))
            value.lock()   # lock in case modifier set has multiple references
        self._modifier_set = value

    def add_grid_parameter(self, grid_par):
        """Add a GridParameter to all of the children Room2Ds of this Building.

        Args:
            grid_par: A radiance GridParameter object to assign to all children Room2Ds.
        """
        for room_2d in self.host.unique_room_2ds:
            room_2d.properties.radiance.add_grid_parameter(grid_par)

    @classmethod
    def from_dict(cls, data, host):
        """Create BuildingRadianceProperties from a dictionary.

        Note that the dictionary must be a non-abridged version for this
        classmethod to work.

        Args:
            data: A dictionary representation of BuildingRadianceProperties.
            host: A Building object that hosts these properties.
        """
        assert data['type'] == 'BuildingRadianceProperties', \
            'Expected BuildingRadianceProperties. Got {}.'.format(data['type'])

        new_prop = cls(host)
        if 'modifier_set' in data and data['modifier_set'] is not None:
            new_prop.modifier_set = ModifierSet.from_dict(data['modifier_set'])

        return new_prop

    def apply_properties_from_dict(self, abridged_data, modifier_sets):
        """Apply properties from a BuildingRadiancePropertiesAbridged dictionary.

        Args:
            abridged_data: A BuildingRadiancePropertiesAbridged dictionary (typically
                coming from a Model).
            modifier_sets: A dictionary of ModifierSets with identifiers
                of the sets as keys, which will be used to re-assign modifier_sets.
        """
        if 'modifier_set' in abridged_data and \
                abridged_data['modifier_set'] is not None:
            self.modifier_set = modifier_sets[abridged_data['modifier_set']]

    def apply_properties_from_geojson_dict(self, data):
        """Apply properties from a geoJSON dictionary.

        Args:
            data: A dictionary representation of a geoJSON feature properties.
                Specifically, this should be the "properties" key describing
                a Polygon or MultiPolygon object.
        """
        # assign the construction set based on climate zone
        if 'grid_parameters' in data and data['grid_parameters'] is not None:
            for gp in data['grid_parameters']:
                try:
                    g_class = getattr(sg_par, gp['type'])
                except AttributeError:
                    raise ValueError(
                        'GridParameter "{}" is not recognized.'.format(gp['type']))
                self.add_grid_parameter(g_class.from_dict(gp))

    def to_dict(self, abridged=False):
        """Return Building Radiance properties as a dictionary.

        Args:
            abridged: Boolean for whether the full dictionary of the Building should
                be written (False) or just the identifier of the the individual
                properties (True). Default: False.
        """
        base = {'radiance': {}}
        base['radiance']['type'] = 'BuildingRadianceProperties' if not \
            abridged else 'BuildingRadiancePropertiesAbridged'

        # write the ModifierSet into the dictionary
        if self._modifier_set is not None:
            base['radiance']['modifier_set'] = \
                self._modifier_set.identifier if abridged else \
                self._modifier_set.to_dict()

        return base

    def duplicate(self, new_host=None):
        """Get a copy of this object.

        new_host: A new Building object that hosts these properties.
            If None, the properties will be duplicated with the same host.
        """
        _host = new_host or self._host
        return BuildingRadianceProperties(_host, self._modifier_set)

    def ToString(self):
        return self.__repr__()

    def __repr__(self):
        return 'Building Radiance Properties: {}'.format(self.host.identifier)
