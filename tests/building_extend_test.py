# coding=utf-8
from ladybug_geometry.geometry3d.pointvector import Point3D
from ladybug_geometry.geometry3d.face import Face3D

from honeybee_radiance.modifierset import ModifierSet
from honeybee_radiance.modifier.material import Glass

from dragonfly.building import Building
from dragonfly.story import Story
from dragonfly.room2d import Room2D
from dragonfly.windowparameter import SimpleWindowRatio

from dragonfly_radiance.properties.building import BuildingRadianceProperties


def test_building_init():
    """Test the initialization of Building objects and basic properties."""
    pts_1 = (
        Point3D(0, 0, 3), Point3D(0, 10, 3), Point3D(10, 10, 3), Point3D(10, 0, 3))
    pts_2 = (
        Point3D(10, 0, 3), Point3D(10, 10, 3), Point3D(20, 10, 3), Point3D(20, 0, 3))
    pts_3 = (
        Point3D(0, 10, 3), Point3D(0, 20, 3), Point3D(10, 20, 3), Point3D(10, 10, 3))
    pts_4 = (
        Point3D(10, 10, 3), Point3D(10, 20, 3), Point3D(20, 20, 3), Point3D(20, 10, 3))
    room2d_1 = Room2D('Office1', Face3D(pts_1), 3)
    room2d_2 = Room2D('Office2', Face3D(pts_2), 3)
    room2d_3 = Room2D('Office3', Face3D(pts_3), 3)
    room2d_4 = Room2D('Office4', Face3D(pts_4), 3)
    story = Story('OfficeFloor', [room2d_1, room2d_2, room2d_3, room2d_4])
    story.solve_room_2d_adjacency(0.01)
    story.set_outdoor_window_parameters(SimpleWindowRatio(0.4))
    story.multiplier = 4
    building = Building('OfficeBuilding', [story])

    assert hasattr(building.properties, 'radiance')
    assert isinstance(building.properties.radiance, BuildingRadianceProperties)
    assert isinstance(building.properties.radiance.modifier_set, ModifierSet)


def test_set_modifier_set():
    """Test the setting of a ModifierSet on a Building."""
    pts_1 = (
        Point3D(0, 0, 3), Point3D(0, 10, 3), Point3D(10, 10, 3), Point3D(10, 0, 3))
    pts_2 = (
        Point3D(10, 0, 3), Point3D(10, 10, 3), Point3D(20, 10, 3), Point3D(20, 0, 3))
    pts_3 = (
        Point3D(0, 10, 3), Point3D(0, 20, 3), Point3D(10, 20, 3), Point3D(10, 10, 3))
    pts_4 = (
        Point3D(10, 10, 3), Point3D(10, 20, 3), Point3D(20, 20, 3), Point3D(20, 10, 3))
    room2d_1 = Room2D('Office1', Face3D(pts_1), 3)
    room2d_2 = Room2D('Office2', Face3D(pts_2), 3)
    room2d_3 = Room2D('Office3', Face3D(pts_3), 3)
    room2d_4 = Room2D('Office4', Face3D(pts_4), 3)
    story = Story('OfficeFloor', [room2d_1, room2d_2, room2d_3, room2d_4])
    story.solve_room_2d_adjacency(0.01)
    story.set_outdoor_window_parameters(SimpleWindowRatio(0.4))
    story.multiplier = 4
    building = Building('OfficeBuilding', [story])

    default_set = ModifierSet('Tinted_Window_Set')
    glass_material = Glass.from_single_transmittance('test_glass', 0.6)
    default_set.aperture_set.exterior_modifier = glass_material

    building.properties.radiance.modifier_set = default_set
    assert building.properties.radiance.modifier_set == default_set
    assert building[0].properties.radiance.modifier_set == default_set

    hb_model = building.to_honeybee()
    assert len(hb_model.properties.radiance.modifier_sets) == 1
    assert hb_model.properties.radiance.modifier_sets[0] == default_set
    assert hb_model.rooms[0].properties.radiance.modifier_set == default_set


def test_duplicate():
    """Test what happens to radiance properties during duplication."""
    default_set = ModifierSet('Tinted_Window_Set')
    pts_1 = (
        Point3D(0, 0, 3), Point3D(0, 10, 3), Point3D(10, 10, 3), Point3D(10, 0, 3))
    pts_2 = (
        Point3D(10, 0, 3), Point3D(10, 10, 3), Point3D(20, 10, 3), Point3D(20, 0, 3))
    pts_3 = (
        Point3D(0, 10, 3), Point3D(0, 20, 3), Point3D(10, 20, 3), Point3D(10, 10, 3))
    pts_4 = (
        Point3D(10, 10, 3), Point3D(10, 20, 3), Point3D(20, 20, 3), Point3D(20, 10, 3))
    room2d_1 = Room2D('Office1', Face3D(pts_1), 3)
    room2d_2 = Room2D('Office2', Face3D(pts_2), 3)
    room2d_3 = Room2D('Office3', Face3D(pts_3), 3)
    room2d_4 = Room2D('Office4', Face3D(pts_4), 3)
    story = Story('OfficeFloor', [room2d_1, room2d_2, room2d_3, room2d_4])
    story.solve_room_2d_adjacency(0.01)
    story.set_outdoor_window_parameters(SimpleWindowRatio(0.4))
    story.multiplier = 4
    building_original = Building('OfficeBuilding', [story])
    building_dup_1 = building_original.duplicate()

    assert building_original.properties.radiance.host is building_original
    assert building_dup_1.properties.radiance.host is building_dup_1
    assert building_original.properties.radiance.host is not \
        building_dup_1.properties.radiance.host

    assert building_original.properties.radiance.modifier_set == \
        building_dup_1.properties.radiance.modifier_set
    building_dup_1.properties.radiance.modifier_set = default_set
    assert building_original.properties.radiance.modifier_set != \
        building_dup_1.properties.radiance.modifier_set

    building_dup_2 = building_dup_1.duplicate()

    assert building_dup_1.properties.radiance.modifier_set == \
        building_dup_2.properties.radiance.modifier_set
    building_dup_2.properties.radiance.modifier_set = None
    assert building_dup_1.properties.radiance.modifier_set != \
        building_dup_2.properties.radiance.modifier_set


def test_to_dict():
    """Test the Building to_dict method with radiance properties."""
    default_set = ModifierSet('Tinted_Window_Set')
    pts_1 = (
        Point3D(0, 0, 3), Point3D(0, 10, 3), Point3D(10, 10, 3), Point3D(10, 0, 3))
    pts_2 = (
        Point3D(10, 0, 3), Point3D(10, 10, 3), Point3D(20, 10, 3), Point3D(20, 0, 3))
    pts_3 = (
        Point3D(0, 10, 3), Point3D(0, 20, 3), Point3D(10, 20, 3), Point3D(10, 10, 3))
    pts_4 = (
        Point3D(10, 10, 3), Point3D(10, 20, 3), Point3D(20, 20, 3), Point3D(20, 10, 3))
    room2d_1 = Room2D('Office1', Face3D(pts_1), 3)
    room2d_2 = Room2D('Office2', Face3D(pts_2), 3)
    room2d_3 = Room2D('Office3', Face3D(pts_3), 3)
    room2d_4 = Room2D('Office4', Face3D(pts_4), 3)
    story = Story('OfficeFloor', [room2d_1, room2d_2, room2d_3, room2d_4])
    story.solve_room_2d_adjacency(0.01)
    story.set_outdoor_window_parameters(SimpleWindowRatio(0.4))
    story.multiplier = 4
    building = Building('OfficeBuilding', [story])

    bd = building.to_dict()
    assert 'properties' in bd
    assert bd['properties']['type'] == 'BuildingProperties'
    assert 'radiance' in bd['properties']
    assert bd['properties']['radiance']['type'] == 'BuildingRadianceProperties'
    assert 'modifier_set' not in bd['properties']['radiance'] or \
        bd['properties']['radiance']['modifier_set'] is None

    building.properties.radiance.modifier_set = default_set
    bd = building.to_dict()
    assert bd['properties']['radiance']['modifier_set'] is not None


def test_from_dict():
    """Test the Story from_dict method with radiance properties."""
    pts_1 = (
        Point3D(0, 0, 3), Point3D(0, 10, 3), Point3D(10, 10, 3), Point3D(10, 0, 3))
    pts_2 = (
        Point3D(10, 0, 3), Point3D(10, 10, 3), Point3D(20, 10, 3), Point3D(20, 0, 3))
    pts_3 = (
        Point3D(0, 10, 3), Point3D(0, 20, 3), Point3D(10, 20, 3), Point3D(10, 10, 3))
    pts_4 = (
        Point3D(10, 10, 3), Point3D(10, 20, 3), Point3D(20, 20, 3), Point3D(20, 10, 3))
    room2d_1 = Room2D('Office1', Face3D(pts_1), 3)
    room2d_2 = Room2D('Office2', Face3D(pts_2), 3)
    room2d_3 = Room2D('Office3', Face3D(pts_3), 3)
    room2d_4 = Room2D('Office4', Face3D(pts_4), 3)
    story = Story('OfficeFloor', [room2d_1, room2d_2, room2d_3, room2d_4])
    story.solve_room_2d_adjacency(0.01)
    story.set_outdoor_window_parameters(SimpleWindowRatio(0.4))
    story.multiplier = 4
    building = Building('OfficeBuilding', [story])

    default_set = ModifierSet('Tinted_Window_Set')
    building.properties.radiance.modifier_set = default_set

    bd = building.to_dict()
    new_bldg = Building.from_dict(bd)
    assert new_bldg.properties.radiance.modifier_set.identifier == \
        'Tinted_Window_Set'
    assert new_bldg.to_dict() == bd
