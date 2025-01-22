"""Tests the features that dragonfly_radiance adds to dragonfly_core Room2D."""
from ladybug_geometry.geometry3d.pointvector import Point3D
from ladybug_geometry.geometry3d.face import Face3D

from honeybee.boundarycondition import boundary_conditions as bcs
from honeybee_radiance.modifierset import ModifierSet
from honeybee_radiance.modifier.material import Glass

from dragonfly.room2d import Room2D
from dragonfly.windowparameter import SimpleWindowRatio
from dragonfly.shadingparameter import Overhang

from dragonfly_radiance.properties.room2d import Room2DRadianceProperties
from dragonfly_radiance.gridpar import RoomGridParameter


def test_radiance_properties():
    """Test the existence of the Room2D radiance properties."""
    pts = (Point3D(0, 0, 3), Point3D(10, 0, 3), Point3D(10, 10, 3), Point3D(0, 10, 3))
    ashrae_base = SimpleWindowRatio(0.4)
    overhang = Overhang(1)
    boundarycs = (bcs.outdoors, bcs.ground, bcs.outdoors, bcs.ground)
    window = (ashrae_base, None, ashrae_base, None)
    shading = (overhang, None, None, None)
    room = Room2D('SquareShoebox', Face3D(pts), 3, boundarycs, window, shading)

    assert hasattr(room.properties, 'radiance')
    assert isinstance(room.properties.radiance, Room2DRadianceProperties)
    assert isinstance(room.properties.radiance.modifier_set, ModifierSet)


def test_default_properties():
    """Test the auto-assigning of Room2D properties."""
    pts = (Point3D(0, 0, 3), Point3D(10, 0, 3), Point3D(10, 10, 3), Point3D(0, 10, 3))
    ashrae_base = SimpleWindowRatio(0.4)
    room = Room2D('SquareShoebox', Face3D(pts), 3)
    room.set_outdoor_window_parameters(ashrae_base)

    assert room.properties.radiance.modifier_set.identifier == \
        'Generic_Interior_Visible_Modifier_Set'


def test_set_modifier_set():
    """Test the setting of a ModifierSet on a Room2D."""
    pts = (Point3D(0, 0, 3), Point3D(10, 0, 3), Point3D(10, 10, 3), Point3D(0, 10, 3))
    ashrae_base = SimpleWindowRatio(0.4)
    overhang = Overhang(1)
    boundarycs = (bcs.outdoors, bcs.ground, bcs.outdoors, bcs.ground)
    window = (ashrae_base, None, ashrae_base, None)
    shading = (overhang, None, None, None)
    room = Room2D('SquareShoebox', Face3D(pts), 3, boundarycs, window, shading)

    default_set = ModifierSet('Tinted_Window_Set')
    glass_material = Glass.from_single_transmittance('test_glass', 0.6)
    default_set.aperture_set.exterior_modifier = glass_material

    room.properties.radiance.modifier_set = default_set
    assert room.properties.radiance.modifier_set == default_set

    hb_room, adj = room.to_honeybee()
    assert hb_room.properties.radiance.modifier_set == default_set


def test_duplicate():
    """Test what happens to radiance properties when duplicating a Room2D."""
    default_set = ModifierSet('Tinted_Window_Set')
    pts = (Point3D(0, 0, 3), Point3D(10, 0, 3), Point3D(10, 10, 3), Point3D(0, 10, 3))
    ashrae_base = SimpleWindowRatio(0.4)
    room_original = Room2D('SquareShoebox', Face3D(pts), 3)
    room_original.set_outdoor_window_parameters(ashrae_base)
    room_dup_1 = room_original.duplicate()

    assert room_original.properties.radiance.host is room_original
    assert room_dup_1.properties.radiance.host is room_dup_1
    assert room_original.properties.radiance.host is not \
        room_dup_1.properties.radiance.host

    assert room_original.properties.radiance.modifier_set == \
        room_dup_1.properties.radiance.modifier_set
    room_dup_1.properties.radiance.modifier_set = default_set
    assert room_original.properties.radiance.modifier_set != \
        room_dup_1.properties.radiance.modifier_set

    room_dup_2 = room_dup_1.duplicate()

    assert room_dup_1.properties.radiance.modifier_set == \
        room_dup_2.properties.radiance.modifier_set
    room_dup_2.properties.radiance.modifier_set = None
    assert room_dup_1.properties.radiance.modifier_set != \
        room_dup_2.properties.radiance.modifier_set


def test_to_dict():
    """Test the Room2D to_dict method with radiance properties."""
    default_set = ModifierSet('Tinted_Window_Set')
    pts = (Point3D(0, 0, 3), Point3D(10, 0, 3), Point3D(10, 10, 3), Point3D(0, 10, 3))
    ashrae_base = SimpleWindowRatio(0.4)
    overhang = Overhang(1)
    boundarycs = (bcs.outdoors, bcs.ground, bcs.outdoors, bcs.ground)
    window = (ashrae_base, None, ashrae_base, None)
    shading = (overhang, None, None, None)
    room = Room2D('ShoeBoxZone', Face3D(pts), 3, boundarycs, window, shading)

    rd = room.to_dict()
    assert 'properties' in rd
    assert rd['properties']['type'] == 'Room2DProperties'
    assert 'radiance' in rd['properties']
    assert rd['properties']['radiance']['type'] == 'Room2DRadianceProperties'
    assert 'modifier_set' not in rd['properties']['radiance'] or \
        rd['properties']['radiance']['modifier_set'] is None

    room.properties.radiance.modifier_set = default_set
    room.properties.radiance.grid_parameters = [RoomGridParameter(0.3)]
    rd = room.to_dict()
    assert rd['properties']['radiance']['modifier_set'] is not None
    assert len(rd['properties']['radiance']['grid_parameters']) == 1


def test_from_dict():
    """Test the Room2D from_dict method with radiance properties."""
    pts = (Point3D(0, 0, 3), Point3D(10, 0, 3), Point3D(10, 10, 3), Point3D(0, 10, 3))
    ashrae_base = SimpleWindowRatio(0.4)
    room = Room2D('SquareShoebox', Face3D(pts), 3)
    room.set_outdoor_window_parameters(ashrae_base)

    default_set = ModifierSet('Tinted_Window_Set')
    room.properties.radiance.modifier_set = default_set
    room.properties.radiance.grid_parameters = [RoomGridParameter(0.3)]

    rd = room.to_dict()
    new_room = Room2D.from_dict(rd)
    assert new_room.properties.radiance.modifier_set.identifier == 'Tinted_Window_Set'
    assert len(new_room.properties.radiance.grid_parameters) == 1
    assert new_room.to_dict() == rd
