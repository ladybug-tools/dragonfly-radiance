# coding=utf-8
"""Room2D Radiance Properties."""
from honeybee_radiance.properties.room import RoomRadianceProperties
from honeybee_radiance.modifierset import ModifierSet

from honeybee_radiance.lib.modifiersets import generic_modifier_set_visible


class Room2DRadianceProperties(object):
    """Radiance Properties for Dragonfly Room2D.

    Args:
        host: A dragonfly_core Room2D object that hosts these properties.
        modifier_set: A honeybee ModifierSet object to specify all default
            modifiers for the Faces of the Room2D. If None, the Room2D will use
            the honeybee default modifier set, which is only representative
            of typical indoor conditions in the visible spectrum. (Default: None).

    Properties:
        * host
        * modifier_set
    """
    __slots__ = ('_host', '_modifier_set')

    def __init__(self, host, modifier_set=None):
        """Initialize Room2D Radiance properties."""
        self._host = host
        self.modifier_set = modifier_set

    @property
    def host(self):
        """Get the Room2D object hosting these properties."""
        return self._host

    @property
    def modifier_set(self):
        """Get or set the Room2D ModifierSet object.

        If not set, it will be set by the parent Story or will be the Honeybee
        default generic ModifierSet.
        """
        if self._modifier_set is not None:  # set by the user
            return self._modifier_set
        elif self._host.has_parent:  # set by parent story
            return self._host.parent.properties.radiance.modifier_set
        else:
            return generic_modifier_set_visible

    @modifier_set.setter
    def modifier_set(self, value):
        if value is not None:
            assert isinstance(value, ModifierSet), \
                'Expected ModifierSet. Got {}'.format(type(value))
            value.lock()   # lock in case modifier set has multiple references
        self._modifier_set = value

    @classmethod
    def from_dict(cls, data, host):
        """Create Room2DRadianceProperties from a dictionary.

        Note that the dictionary must be a non-abridged version for this
        classmethod to work.

        Args:
            data: A dictionary representation of Room2DRadianceProperties in the
                format below.
            host: A Room2D object that hosts these properties.

        .. code-block:: python

            {
            "type": 'Room2DRadianceProperties',
            "modifier_set": {}  # A ModifierSet dictionary
            }
        """
        assert data['type'] == 'Room2DRadianceProperties', \
            'Expected Room2DRadianceProperties. Got {}.'.format(data['type'])

        new_prop = cls(host)
        if 'modifier_set' in data and data['modifier_set'] is not None:
            new_prop.modifier_set = ModifierSet.from_dict(data['modifier_set'])

        return new_prop

    def apply_properties_from_dict(self, abridged_data, modifier_sets):
        """Apply properties from a Room2DRadiancePropertiesAbridged dictionary.

        Args:
            abridged_data: A Room2DRadiancePropertiesAbridged dictionary (typically
                coming from a Model).
            modifier_sets: A dictionary of ModifierSets with identifiers
                of the sets as keys, which will be used to re-assign modifier_sets.
        """
        if 'modifier_set' in abridged_data and abridged_data['modifier_set'] is not None:
            self.modifier_set = modifier_sets[abridged_data['modifier_set']]

    def to_dict(self, abridged=False):
        """Return Room2D radiance properties as a dictionary.

        Args:
            abridged: Boolean for whether the full dictionary of the Room2D should
                be written (False) or just the identifier of the the individual
                properties (True). Default: False.
        """
        base = {'radiance': {}}
        base['radiance']['type'] = 'Room2DRadianceProperties' if not \
            abridged else 'Room2DRadiancePropertiesAbridged'

        # write the ModifierSet into the dictionary
        if self._modifier_set is not None:
            base['radiance']['modifier_set'] = \
                self._modifier_set.identifier if abridged else \
                self._modifier_set.to_dict()

        return base

    def to_honeybee(self, new_host):
        """Get a honeybee version of this object.

        Args:
            new_host: A honeybee-core Room object that will host these properties.
        """
        mod_set = self.modifier_set  # includes story and building-assigned sets
        hb_mods = mod_set if mod_set is not generic_modifier_set_visible else None
        hb_prop = RoomRadianceProperties(new_host, hb_mods)
        return hb_prop

    def from_honeybee(self, hb_properties):
        """Transfer radiance attributes from a Honeybee Room to Dragonfly Room2D.

        Args:
            hb_properties: The RoomRadianceProperties of the honeybee Room that is being
                translated to a Dragonfly Room2D.
        """
        self._modifier_set = hb_properties._modifier_set

    def duplicate(self, new_host=None):
        """Get a copy of this object.

        Args:
            new_host: A new Room2D object that hosts these properties.
                If None, the properties will be duplicated with the same host.
        """
        _host = new_host or self._host
        df_prop = Room2DRadianceProperties(_host, self._modifier_set)
        return df_prop

    def ToString(self):
        return self.__repr__()

    def __repr__(self):
        return 'Room2D Radiance Properties: {}'.format(self.host.identifier)
