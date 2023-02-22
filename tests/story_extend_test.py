"""Tests the features that dragonfly_radiance adds to dragonfly_core Story."""
from ladybug_geometry.geometry3d.pointvector import Point3D
from ladybug_geometry.geometry3d.face import Face3D
import honeybee.model as hb_model
from honeybee_radiance.modifierset import ModifierSet
from honeybee_radiance.modifier.material import Glass

from dragonfly.story import Story
from dragonfly.room2d import Room2D
from dragonfly.windowparameter import SimpleWindowRatio

from dragonfly_radiance.properties.story import StoryRadianceProperties


def test_radiance_properties():
    """Test the existence of the Story radiance properties."""
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

    assert hasattr(story.properties, 'radiance')
    assert isinstance(story.properties.radiance, StoryRadianceProperties)
    assert isinstance(story.properties.radiance.modifier_set, ModifierSet)


def test_set_modifier_set():
    """Test the setting of a ModifierSet on a Story."""
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

    default_set = ModifierSet('Tinted_Window_Set')
    glass_material = Glass.from_single_transmittance('test_glass', 0.6)
    default_set.aperture_set.exterior_modifier = glass_material

    story.properties.radiance.modifier_set = default_set
    assert story.properties.radiance.modifier_set == default_set
    assert story[0].properties.radiance.modifier_set == default_set

    rooms = story.to_honeybee()
    model = hb_model.Model(story.identifier, rooms)
    assert len(model.properties.radiance.modifier_sets) == 1
    assert model.properties.radiance.modifier_sets[0] == default_set
    assert model.rooms[0].properties.radiance.modifier_set == default_set


def test_duplicate():
    """Test what happens to radiance properties when duplicating a Story."""
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
    story_original = Story('OfficeFloor', [room2d_1, room2d_2, room2d_3, room2d_4])
    story_original.solve_room_2d_adjacency(0.01)
    story_original.set_outdoor_window_parameters(SimpleWindowRatio(0.4))
    story_dup_1 = story_original.duplicate()

    assert story_original.properties.radiance.host is story_original
    assert story_dup_1.properties.radiance.host is story_dup_1
    assert story_original.properties.radiance.host is not \
        story_dup_1.properties.radiance.host

    assert story_original.properties.radiance.modifier_set == \
        story_dup_1.properties.radiance.modifier_set
    story_dup_1.properties.radiance.modifier_set = default_set
    assert story_original.properties.radiance.modifier_set != \
        story_dup_1.properties.radiance.modifier_set

    room_dup_2 = story_dup_1.duplicate()

    assert story_dup_1.properties.radiance.modifier_set == \
        room_dup_2.properties.radiance.modifier_set
    room_dup_2.properties.radiance.modifier_set = None
    assert story_dup_1.properties.radiance.modifier_set != \
        room_dup_2.properties.radiance.modifier_set


def test_to_dict():
    """Test the Story to_dict method with radiance properties."""
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

    sd = story.to_dict()
    assert 'properties' in sd
    assert sd['properties']['type'] == 'StoryProperties'
    assert 'radiance' in sd['properties']
    assert sd['properties']['radiance']['type'] == 'StoryRadianceProperties'
    assert 'modifier_set' not in sd['properties']['radiance'] or \
        sd['properties']['radiance']['modifier_set'] is None

    story.properties.radiance.modifier_set = default_set
    sd = story.to_dict()
    assert sd['properties']['radiance']['modifier_set'] is not None


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

    default_set = ModifierSet('Tinted_Window_Set')
    story.properties.radiance.modifier_set = default_set

    sd = story.to_dict()
    new_story = Story.from_dict(sd)
    assert new_story.properties.radiance.modifier_set.identifier == \
        'Tinted_Window_Set'
    assert new_story.to_dict() == sd
