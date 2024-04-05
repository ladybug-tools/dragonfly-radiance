# coding=utf-8
"""Context Shade Radiance Properties."""
from honeybee.shade import Shade
from honeybee_radiance.modifier import Modifier
from honeybee_radiance.properties.shade import ShadeRadianceProperties
from honeybee_radiance.properties.shademesh import ShadeMeshRadianceProperties
from honeybee_radiance.mutil import dict_to_modifier  # imports all modifiers classes
from honeybee_radiance.lib.modifiers import generic_context


class ContextShadeRadianceProperties(object):
    """Radiance Properties for Dragonfly ContextShade.

    Args:
        host_shade: A dragonfly_core ContextShade object that hosts these properties.
        modifier: An optional Modifier object to set the reflectance and specularity
            of the ContextShade. The default is a completely diffuse modifier
            with 0.2 reflectance.

    Properties:
        * host
        * modifier
        * is_modifier_set_by_user
    """

    __slots__ = ('_host', '_modifier')

    def __init__(self, host_shade, modifier=None):
        """Initialize ContextShade radiance properties."""
        self._host = host_shade
        self.modifier = modifier

    @property
    def host(self):
        """Get the Shade object hosting these properties."""
        return self._host

    @property
    def modifier(self):
        """Get or set a Modifier for the context shade."""
        if self._modifier:  # set by user
            return self._modifier
        else:
            return generic_context

    @modifier.setter
    def modifier(self, value):
        if value is not None:
            assert isinstance(value, Modifier), \
                'Expected Modifier. Got {}.'.format(type(value))
            value.lock()  # lock editing in case modifier has multiple references
        self._modifier = value

    @property
    def is_modifier_set_by_user(self):
        """Boolean noting if modifier is user-set."""
        return self._modifier is not None

    @classmethod
    def from_dict(cls, data, host):
        """Create ContextShadeRadianceProperties from a dictionary.

        Note that the dictionary must be a non-abridged version for this
        classmethod to work.

        Args:
            data: A dictionary representation of ContextShadeRadianceProperties.
            host: A ContextShade object that hosts these properties.
        """
        assert data['type'] == 'ContextShadeRadianceProperties', \
            'Expected ContextShadeRadianceProperties. Got {}.'.format(data['type'])

        new_prop = cls(host)
        if 'modifier' in data and data['modifier'] is not None:
            new_prop.modifier = dict_to_modifier(data['modifier'])
        return new_prop

    def apply_properties_from_dict(self, abridged_data, modifiers):
        """Apply properties from a ContextShadeRadiancePropertiesAbridged dictionary.

        Args:
            abridged_data: A ContextShadeRadiancePropertiesAbridged dictionary (typically
                coming from a Model).
            modifiers: A dictionary of modifiers with modifiers identifiers
                as keys, which will be used to re-assign modifiers.
        """
        if 'modifier' in abridged_data and abridged_data['modifier'] is not None:
            self.modifier = modifiers[abridged_data['modifier']]

    def to_dict(self, abridged=False):
        """Return radiance properties as a dictionary.

        Args:
            abridged: Boolean to note whether the full dictionary describing the
                object should be returned (False) or just an abridged version (True).
                Default: False.
        """
        base = {'radiance': {}}
        base['radiance']['type'] = 'ContextShadeRadianceProperties' if not \
            abridged else 'ContextShadeRadiancePropertiesAbridged'
        if self._modifier is not None:
            base['radiance']['modifier'] = self._modifier.identifier if abridged \
                else self._modifier.to_dict()
        return base

    def to_honeybee(self, new_host):
        """Get a honeybee version of this object.

        Args:
            new_host: A honeybee-core Shade or ShadeMesh object that will host
                these properties.
        """
        return ShadeRadianceProperties(new_host, self._modifier) \
            if isinstance(new_host, Shade) else \
            ShadeMeshRadianceProperties(new_host, self._modifier)

    def from_honeybee(self, hb_properties):
        """Transfer radiance attributes from a Honeybee Shade to Dragonfly ContextShade.

        Args:
            hb_properties: The ShadeRadianceProperties of the honeybee Shade
                that is being translated to a Dragonfly ContextShade.
        """
        self._modifier = hb_properties._modifier

    def duplicate(self, new_host=None):
        """Get a copy of this object.

        new_host: A new ContextShade object that hosts these properties.
            If None, the properties will be duplicated with the same host.
        """
        _host = new_host or self._host
        return ContextShadeRadianceProperties(_host, self._modifier)

    def ToString(self):
        return self.__repr__()

    def __repr__(self):
        return 'Context Shade Radiance Properties: {}'.format(self.host.identifier)
