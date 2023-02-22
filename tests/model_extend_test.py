# coding=utf-8
import pytest

from ladybug_geometry.geometry3d.pointvector import Point3D
from ladybug_geometry.geometry3d.plane import Plane
from ladybug_geometry.geometry3d.face import Face3D

from honeybee_radiance.modifierset import ModifierSet
from honeybee_radiance.modifier import Modifier
from honeybee_radiance.modifier.material import Glass, Plastic

from dragonfly.model import Model
from dragonfly.building import Building
from dragonfly.story import Story
from dragonfly.room2d import Room2D
from dragonfly.context import ContextShade
from dragonfly.windowparameter import SimpleWindowRatio

from dragonfly_radiance.properties.model import ModelRadianceProperties


def test_radiance_properties():
    """Test the existence of the Model radiance properties."""
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

    tree_canopy_geo1 = Face3D.from_regular_polygon(6, 6, Plane(o=Point3D(5, -10, 6)))
    tree_canopy_geo2 = Face3D.from_regular_polygon(6, 2, Plane(o=Point3D(-5, -10, 3)))
    tree_canopy = ContextShade('TreeCanopy', [tree_canopy_geo1, tree_canopy_geo2])
    bright_leaves = Plastic('Bright_Light_Leaves', 0.6, 0.7, 0.8, 0, 0)
    tree_canopy.properties.radiance.modifier = bright_leaves

    model = Model('NewDevelopment', [building], [tree_canopy])

    assert hasattr(model.properties, 'radiance')
    assert isinstance(model.properties.radiance, ModelRadianceProperties)
    assert isinstance(model.properties.host, Model)
    for mat in model.properties.radiance.modifiers:
        assert isinstance(mat, Modifier)
    assert len(model.properties.radiance.shade_modifiers) == 1
    assert len(model.properties.radiance.modifier_sets) == 0


def test_check_duplicate_modifier_set_identifiers():
    """Test the check_duplicate_modifier_set_identifiers method."""
    pts_1 = (
        Point3D(0, 0, 3), Point3D(0, 10, 3), Point3D(10, 10, 3), Point3D(10, 0, 3))
    pts_2 = (
        Point3D(10, 0, 3), Point3D(10, 10, 3), Point3D(20, 10, 3), Point3D(20, 0, 3))
    room2d_1 = Room2D('Office1', Face3D(pts_1), 3)
    room2d_2 = Room2D('Office2', Face3D(pts_2), 3)
    story = Story('OfficeFloor', [room2d_1, room2d_2])
    story.solve_room_2d_adjacency(0.01)
    story.set_outdoor_window_parameters(SimpleWindowRatio(0.4))
    story.multiplier = 4
    building = Building('OfficeBuilding', [story])
    building.separate_top_bottom_floors()

    default_set = ModifierSet('Tinted_Window_Set')
    glass_material = Glass.from_single_transmittance('test_glass', 0.6)
    default_set.aperture_set.exterior_modifier = glass_material
    building.unique_room_2ds[-1].properties.radiance.modifier_set = default_set
    building.unique_room_2ds[-2].properties.radiance.modifier_set = default_set

    tree_canopy_geo1 = Face3D.from_regular_polygon(6, 6, Plane(o=Point3D(5, -10, 6)))
    tree_canopy_geo2 = Face3D.from_regular_polygon(6, 2, Plane(o=Point3D(-5, -10, 3)))
    tree_canopy = ContextShade('TreeCanopy', [tree_canopy_geo1, tree_canopy_geo2])

    model = Model('NewDevelopment', [building], [tree_canopy])

    assert model.properties.radiance.check_duplicate_modifier_set_identifiers(False) \
        == ''
    constr_set2 = ModifierSet('Tinted_Window_Set')
    building.unique_room_2ds[-2].properties.radiance.modifier_set = constr_set2
    assert model.properties.radiance.check_duplicate_modifier_set_identifiers(False) \
        != ''
    with pytest.raises(ValueError):
        model.properties.radiance.check_duplicate_modifier_set_identifiers(True)


def test_to_from_dict():
    """Test the Model to_dict and from_dict method."""
    pts_1 = (
        Point3D(0, 0, 3), Point3D(0, 10, 3), Point3D(10, 10, 3), Point3D(10, 0, 3))
    pts_2 = (
        Point3D(10, 0, 3), Point3D(10, 10, 3), Point3D(20, 10, 3), Point3D(20, 0, 3))
    room2d_1 = Room2D('Office1', Face3D(pts_1), 3)
    room2d_2 = Room2D('Office2', Face3D(pts_2), 3)
    story = Story('OfficeFloor', [room2d_1, room2d_2])
    story.solve_room_2d_adjacency(0.01)
    story.set_outdoor_window_parameters(SimpleWindowRatio(0.4))
    story.multiplier = 4
    building = Building('OfficeBuilding', [story])
    building.separate_top_bottom_floors()

    default_set = ModifierSet('Tinted_Window_Set')
    glass_material = Glass.from_single_transmittance('test_glass', 0.6)
    default_set.aperture_set.exterior_modifier = glass_material
    building.unique_room_2ds[-1].properties.radiance.modifier_set = default_set
    building.unique_room_2ds[-2].properties.radiance.modifier_set = default_set

    tree_canopy_geo1 = Face3D.from_regular_polygon(6, 6, Plane(o=Point3D(5, -10, 6)))
    tree_canopy_geo2 = Face3D.from_regular_polygon(6, 2, Plane(o=Point3D(-5, -10, 3)))
    tree_canopy = ContextShade('TreeCanopy', [tree_canopy_geo1, tree_canopy_geo2])
    bright_leaves = Plastic('Bright_Light_Leaves', 0.6, 0.7, 0.8, 0, 0)
    tree_canopy.properties.radiance.modifier = bright_leaves

    model = Model('NewDevelopment', [building], [tree_canopy])

    model_dict = model.to_dict()
    new_model = Model.from_dict(model_dict)
    assert model_dict == new_model.to_dict()

    assert bright_leaves in new_model.properties.radiance.modifiers
    assert glass_material in new_model.properties.radiance.modifiers
    assert default_set in new_model.properties.radiance.modifier_sets
    assert new_model.buildings[0].unique_room_2ds[-1].properties.radiance.modifier_set \
        == default_set


def test_to_honeybee():
    """Test the Model to_honeybee method."""
    pts_1 = (
        Point3D(0, 0, 3), Point3D(10, 0, 3), Point3D(10, 10, 3), Point3D(0, 10, 3))
    pts_2 = (
        Point3D(10, 0, 3), Point3D(20, 0, 3), Point3D(20, 10, 3), Point3D(10, 10, 3))
    pts_3 = (
        Point3D(0, 20, 3), Point3D(20, 20, 3), Point3D(20, 30, 3), Point3D(0, 30, 3))
    room2d_1 = Room2D('Office1', Face3D(pts_1), 3)
    room2d_2 = Room2D('Office2', Face3D(pts_2), 3)
    room2d_3 = Room2D('Office3', Face3D(pts_3), 3)
    story_big = Story('OfficeFloorBig', [room2d_3])
    story = Story('OfficeFloor', [room2d_1, room2d_2])
    story.solve_room_2d_adjacency(0.01)
    story.set_outdoor_window_parameters(SimpleWindowRatio(0.4))
    story.multiplier = 4
    building = Building('OfficeBuilding', [story])
    building.separate_top_bottom_floors()
    story_big.set_outdoor_window_parameters(SimpleWindowRatio(0.4))
    story_big.multiplier = 4
    building_big = Building('OfficeBuildingBig', [story_big])
    building_big.separate_top_bottom_floors()

    default_set = ModifierSet('Tinted_Window_Set')
    glass_material = Glass.from_single_transmittance('test_glass', 0.6)
    default_set.aperture_set.exterior_modifier = glass_material
    building.unique_room_2ds[-1].properties.radiance.modifier_set = default_set
    building.unique_room_2ds[-2].properties.radiance.modifier_set = default_set

    tree_canopy_geo1 = Face3D.from_regular_polygon(6, 6, Plane(o=Point3D(5, -10, 6)))
    tree_canopy_geo2 = Face3D.from_regular_polygon(6, 2, Plane(o=Point3D(-5, -10, 3)))
    tree_canopy = ContextShade('TreeCanopy', [tree_canopy_geo1, tree_canopy_geo2])
    bright_leaves = Plastic('Bright_Light_Leaves', 0.6, 0.7, 0.8, 0, 0)
    tree_canopy.properties.radiance.modifier = bright_leaves

    model = Model('NewDevelopment', [building, building_big], [tree_canopy])

    hb_models = model.to_honeybee('Building', 10, False, tolerance=0.01)
    assert len(hb_models) == 2

    assert bright_leaves in hb_models[0].properties.radiance.modifiers
    assert glass_material in hb_models[0].properties.radiance.modifiers
    assert default_set in hb_models[0].properties.radiance.modifier_sets
    assert hb_models[0].rooms[-1].properties.radiance.modifier_set == default_set
