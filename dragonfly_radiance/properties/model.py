# coding=utf-8
"""Model Radiance Properties."""
try:
    from itertools import izip as zip  # python 2
except ImportError:
    pass   # python 3

from honeybee.checkdup import check_duplicate_identifiers
from honeybee.extensionutil import room_extension_dicts
import honeybee_radiance.properties.model as hb_model_properties
from honeybee_radiance.lib.modifiersets import generic_modifier_set_visible
from honeybee_radiance.lib.modifiers import generic_context

from dragonfly.extensionutil import model_extension_dicts


class ModelRadianceProperties(object):
    """Radiance Properties for Dragonfly Model.

    Args:
        host: A dragonfly_core Model object that hosts these properties.

    Properties:
        * host
        * modifiers
        * shade_modifiers
        * modifier_sets
        * global_modifier_set
    """

    def __init__(self, host):
        """Initialize Model Radiance properties."""
        self._host = host

    @property
    def host(self):
        """Get the Model object hosting these properties."""
        return self._host

    @property
    def modifiers(self):
        """List of all unique modifiers contained within the model.

        This includes modifiers across all Room2Ds, Stories, and Building
        ModifierSets but it does NOT include the Honeybee generic default
        modifier set.
        """
        bldg_mods = []
        for mod_set in self.modifier_sets:
            bldg_mods.extend(mod_set.modified_modifiers_unique)
        all_mods = bldg_mods + self.face_modifiers + self.shade_modifiers
        return list(set(all_mods))

    @property
    def face_modifiers(self):
        """Get a list of all unique modifiers assigned to Faces, Apertures and Doors.

        These objects only exist under the Building.room_3ds property.
        """
        modifiers = []
        for bldg in self.host.buildings:
            for face in bldg.room_3d_faces:
                self._check_and_add_obj_modifier(face, modifiers)
                for ap in face.apertures:
                    self._check_and_add_obj_modifier(ap, modifiers)
                for dr in face.doors:
                    self._check_and_add_obj_modifier(dr, modifiers)
        return list(set(modifiers))

    @property
    def shade_modifiers(self):
        """A list of all unique modifiers assigned to ContextShades in the model."""
        modifiers = []
        for shade in self.host.context_shades:
            self._check_and_add_obj_modifier(shade, modifiers)
        for bldg in self.host.buildings:
            for shd in bldg.room_3d_shades:
                self._check_and_add_obj_modifier(shd, modifiers)
        return list(set(modifiers))

    @property
    def modifier_sets(self):
        """A list of all unique Building-Assigned ModifierSets in the Model.

        Note that this includes ModifierSets assigned to individual Stories and
        Room2Ds in the Building.
        """
        modifier_sets = []
        for bldg in self.host.buildings:
            self._check_and_add_obj_mod_set(bldg, modifier_sets)
            for story in bldg.unique_stories:
                self._check_and_add_obj_mod_set(story, modifier_sets)
                for room in story.room_2ds:
                    self._check_and_add_obj_mod_set(room, modifier_sets)
            for room in bldg.room_3ds:
                self._check_and_add_obj_mod_set(room, modifier_sets)
        return list(set(modifier_sets))  # catch equivalent modifier sets

    @property
    def global_modifier_set(self):
        """The global radiance modifier set.

        This is what is used whenever there is no modifier_set assigned to a
        Room2D, a parent Story, or a parent Building.
        """
        return generic_modifier_set_visible

    def check_all(self, raise_exception=True):
        """Check all of the aspects of the Model radiance properties.

        Args:
            raise_exception: Boolean to note whether a ValueError should be raised
                if any errors are found. If False, this method will simply
                return a text string with all errors that were found.

        Returns:
            A text string with all errors that were found. This string will be empty
            of no errors were found.
        """
        msgs = []
        # perform checks for key honeybee model schema rules
        msgs.append(self.check_duplicate_modifier_set_identifiers(False))
        # output a final report of errors or raise an exception
        full_msgs = [msg for msg in msgs if msg != '']
        full_msg = '\n'.join(full_msgs)
        if raise_exception and len(full_msgs) != 0:
            raise ValueError(full_msg)
        return full_msg

    def check_duplicate_modifier_set_identifiers(self, raise_exception=True):
        """Check that there are no duplicate ModifierSet identifiers in the model."""
        return check_duplicate_identifiers(
            self.modifier_sets, raise_exception, 'ModifierSet')

    def apply_properties_from_dict(self, data):
        """Apply the radiance properties of a dictionary to the host Model of this object.

        Args:
            data: A dictionary representation of an entire dragonfly-core Model.
                Note that this dictionary must have ModelRadianceProperties in order
                for this method to successfully apply the radiance properties.
        """
        assert 'radiance' in data['properties'], \
            'Dictionary possesses no ModelRadianceProperties.'
        modifiers, modifier_sets = \
            hb_model_properties.ModelRadianceProperties.load_properties_from_dict(data)

        # collect lists of radiance property dictionaries
        building_e_dicts, story_e_dicts, room2d_e_dicts, context_e_dicts = \
            model_extension_dicts(data, 'radiance', [], [], [], [])

        # apply radiance properties to objects using the radiance property dictionaries
        for bldg, b_dict in zip(self.host.buildings, building_e_dicts):
            if b_dict is not None:
                bldg.properties.radiance.apply_properties_from_dict(
                    b_dict, modifier_sets)
            if bldg.has_room_3ds and b_dict is not None and 'room_3ds' in b_dict and \
                    b_dict['room_3ds'] is not None:
                room_e_dicts, face_e_dicts, shd_e_dicts, ap_e_dicts, dr_e_dicts = \
                    room_extension_dicts(b_dict['room_3ds'], 'radiance', [], [], [], [], [])
                for room, r_dict in zip(bldg.room_3ds, room_e_dicts):
                    if r_dict is not None:
                        room.properties.radiance.apply_properties_from_dict(
                            r_dict, modifier_sets)
                for face, f_dict in zip(bldg.room_3d_faces, face_e_dicts):
                    if f_dict is not None:
                        face.properties.radiance.apply_properties_from_dict(
                            f_dict, modifiers)
                for aperture, a_dict in zip(bldg.room_3d_apertures, ap_e_dicts):
                    if a_dict is not None:
                        aperture.properties.radiance.apply_properties_from_dict(
                            a_dict, modifiers)
                for door, d_dict in zip(bldg.room_3d_doors, dr_e_dicts):
                    if d_dict is not None:
                        door.properties.radiance.apply_properties_from_dict(
                            d_dict, modifiers)
                for shade, s_dict in zip(bldg.room_3d_shades, shd_e_dicts):
                    if s_dict is not None:
                        shade.properties.radiance.apply_properties_from_dict(
                            s_dict, modifiers)
        for story, s_dict in zip(self.host.stories, story_e_dicts):
            if s_dict is not None:
                story.properties.radiance.apply_properties_from_dict(
                    s_dict, modifier_sets)
        for room, r_dict in zip(self.host.room_2ds, room2d_e_dicts):
            if r_dict is not None:
                room.properties.radiance.apply_properties_from_dict(
                    r_dict, modifier_sets)
        for shade, s_dict in zip(self.host.context_shades, context_e_dicts):
            if s_dict is not None:
                shade.properties.radiance.apply_properties_from_dict(s_dict, modifiers)

    def to_dict(self):
        """Return Model radiance properties as a dictionary."""
        base = {'radiance': {'type': 'ModelRadianceProperties'}}

        # add the global modifier set to the dictionary
        gs = self.global_modifier_set.to_dict(abridged=True, none_for_defaults=False)
        gs['type'] = 'GlobalModifierSet'
        del gs['identifier']
        g_mods = self.global_modifier_set.modifiers_unique
        gs['modifiers'] = [mod.to_dict() for mod in g_mods]
        gs['context_modifier'] = generic_context.identifier
        gs['modifiers'].append(generic_context.to_dict())
        base['radiance']['global_modifier_set'] = gs

        # add all ModifierSets to the dictionary
        base['radiance']['modifier_sets'] = []
        modifier_sets = self.modifier_sets
        for mod_set in modifier_sets:
            base['radiance']['modifier_sets'].append(mod_set.to_dict(abridged=True))

        # add all unique Modifiers to the dictionary
        room_mods = []
        for mod_set in modifier_sets:
            room_mods.extend(mod_set.modified_modifiers_unique)
        all_mods = room_mods + self.face_modifiers + self.shade_modifiers
        modifiers = tuple(set(all_mods))
        base['radiance']['modifiers'] = []
        for mod in modifiers:
            base['radiance']['modifiers'].append(mod.to_dict())

        return base

    def to_honeybee(self, new_host):
        """Get a honeybee version of this object.

        Args:
            new_host: A honeybee-core Model object that will host these properties.
        """
        hb_rad_props = hb_model_properties.ModelRadianceProperties(new_host)
        # gather all of the sensor grid parameters across the model
        sg_dict = {}
        for rm_2d in self.host.room_2ds:
            if len(rm_2d.properties.radiance._grid_parameters) != 0:
                sg_dict[rm_2d.identifier] = rm_2d.properties.radiance._grid_parameters
        # generate and assign sensor grids to the rooms of the new_host
        if len(sg_dict) != 0:
            sensor_grids = []
            for rm_id, g_par in sg_dict.items():
                for room in new_host.rooms:
                    if room.identifier == rm_id:
                        for gp in g_par:
                            sg = gp.generate_grid_from_room(room)
                            if sg is not None:
                                sensor_grids.append(sg)
                        break
            hb_rad_props.sensor_grids = sensor_grids
        return hb_rad_props

    def duplicate(self, new_host=None):
        """Get a copy of this Model.

        Args:
            new_host: A new Model object that hosts these properties.
                If None, the properties will be duplicated with the same host.
        """
        _host = new_host or self._host
        return ModelRadianceProperties(_host)

    def _check_and_add_obj_modifier(self, obj, modifiers):
        """Check if a modifier is assigned to an object and add it to a list."""
        mod = obj.properties.radiance._modifier
        if mod is not None:
            if not self._instance_in_array(mod, modifiers):
                modifiers.append(mod)

    def _check_and_add_obj_mod_set(self, obj, modifier_sets):
        """Check if a modifier set is assigned to an object and add it to a list."""
        m_set = obj.properties.radiance._modifier_set
        if m_set is not None:
            if not self._instance_in_array(m_set, modifier_sets):
                modifier_sets.append(m_set)

    @staticmethod
    def _instance_in_array(object_instance, object_array):
        """Check if a specific object instance is already in an array.

        This can be much faster than  `if object_instance in object_array`
        when you expect to be testing a lot of the same instance of an object for
        inclusion in an array since the builtin method uses an == operator to
        test inclusion.
        """
        for val in object_array:
            if val is object_instance:
                return True
        return False

    def ToString(self):
        return self.__repr__()

    def __repr__(self):
        return 'Model Radiance Properties: {}'.format(self.host.identifier)
