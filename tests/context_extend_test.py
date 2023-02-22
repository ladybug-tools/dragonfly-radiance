"""Tests the features that dragonfly_radiance adds to dragonfly_core ContextShade."""
from ladybug_geometry.geometry3d.pointvector import Point3D
from ladybug_geometry.geometry3d.plane import Plane
from ladybug_geometry.geometry3d.face import Face3D
from honeybee_radiance.modifier.material import Plastic

from dragonfly.context import ContextShade

from dragonfly_radiance.properties.context import ContextShadeRadianceProperties


def test_radiance_properties():
    """Test the existence of the ContextShade radiance properties."""
    tree_canopy_geo1 = Face3D.from_regular_polygon(6, 6, Plane(o=Point3D(5, -10, 6)))
    tree_canopy_geo2 = Face3D.from_regular_polygon(6, 2, Plane(o=Point3D(-5, -10, 3)))
    tree_canopy = ContextShade('TreeCanopy', [tree_canopy_geo1, tree_canopy_geo2])

    assert hasattr(tree_canopy.properties, 'radiance')
    assert isinstance(tree_canopy.properties.radiance, ContextShadeRadianceProperties)
    assert isinstance(tree_canopy.properties.radiance.modifier, Plastic)


def test_set_modifier():
    """Test the setting of a Construction and Schedule on a ContextShade."""
    tree_canopy_geo1 = Face3D.from_regular_polygon(6, 6, Plane(o=Point3D(5, -10, 6)))
    tree_canopy_geo2 = Face3D.from_regular_polygon(6, 2, Plane(o=Point3D(-5, -10, 3)))
    tree_canopy = ContextShade('TreeCanopy', [tree_canopy_geo1, tree_canopy_geo2])

    bright_leaves = Plastic('Bright_Light_Leaves', 0.6, 0.7, 0.8, 0, 0)

    tree_canopy.properties.radiance.modifier = bright_leaves
    assert tree_canopy.properties.radiance.modifier == bright_leaves


def test_duplicate():
    """Test what happens to radiance properties when duplicating a Room2D."""
    tree_canopy_geo1 = Face3D.from_regular_polygon(6, 6, Plane(o=Point3D(5, -10, 6)))
    tree_canopy_geo2 = Face3D.from_regular_polygon(6, 2, Plane(o=Point3D(-5, -10, 3)))
    shade_original = ContextShade('TreeCanopy', [tree_canopy_geo1, tree_canopy_geo2])
    shade_dup_1 = shade_original.duplicate()

    bright_leaves = Plastic('Bright_Light_Leaves', 0.6, 0.7, 0.8, 0, 0)

    assert shade_original.properties.radiance.host is shade_original
    assert shade_dup_1.properties.radiance.host is shade_dup_1
    assert shade_original.properties.radiance.host is not \
        shade_dup_1.properties.radiance.host

    assert shade_original.properties.radiance.modifier == \
        shade_dup_1.properties.radiance.modifier
    shade_dup_1.properties.radiance.modifier = bright_leaves
    assert shade_original.properties.radiance.modifier != \
        shade_dup_1.properties.radiance.modifier

    shade_dup_2 = shade_dup_1.duplicate()

    assert shade_dup_1.properties.radiance.modifier == \
        shade_dup_2.properties.radiance.modifier
    shade_dup_2.properties.radiance.modifier = None
    assert shade_dup_1.properties.radiance.modifier != \
        shade_dup_2.properties.radiance.modifier


def test_to_dict():
    """Test the Building to_dict method with radiance properties."""
    tree_canopy_geo1 = Face3D.from_regular_polygon(6, 6, Plane(o=Point3D(5, -10, 6)))
    tree_canopy_geo2 = Face3D.from_regular_polygon(6, 2, Plane(o=Point3D(-5, -10, 3)))
    tree_canopy = ContextShade('TreeCanopy', [tree_canopy_geo1, tree_canopy_geo2])

    sd = tree_canopy.to_dict()
    assert 'properties' in sd
    assert sd['properties']['type'] == 'ContextShadeProperties'
    assert 'radiance' in sd['properties']
    assert sd['properties']['radiance']['type'] == 'ContextShadeRadianceProperties'
    assert 'modifier' not in sd['properties']['radiance'] or \
        sd['properties']['radiance']['modifier'] is None

    bright_leaves = Plastic('Bright_Light_Leaves', 0.6, 0.7, 0.8, 0, 0)
    tree_canopy.properties.radiance.modifier = bright_leaves

    sd = tree_canopy.to_dict()
    assert sd['properties']['radiance']['modifier'] is not None


def test_from_dict():
    """Test the Story from_dict method with radiance properties."""
    tree_canopy_geo1 = Face3D.from_regular_polygon(6, 6, Plane(o=Point3D(5, -10, 6)))
    tree_canopy_geo2 = Face3D.from_regular_polygon(6, 2, Plane(o=Point3D(-5, -10, 3)))
    tree_canopy = ContextShade('TreeCanopy', [tree_canopy_geo1, tree_canopy_geo2])

    bright_leaves = Plastic('Bright_Light_Leaves', 0.6, 0.7, 0.8, 0, 0)
    tree_canopy.properties.radiance.modifier = bright_leaves

    sd = tree_canopy.to_dict()
    new_shd = ContextShade.from_dict(sd)
    assert new_shd.properties.radiance.modifier == bright_leaves
    assert new_shd.to_dict() == sd
