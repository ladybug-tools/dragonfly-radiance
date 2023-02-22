# coding=utf-8
from dragonfly.properties import ModelProperties, BuildingProperties, StoryProperties, \
    Room2DProperties, ContextShadeProperties

from .properties.model import ModelRadianceProperties
from .properties.building import BuildingRadianceProperties
from .properties.story import StoryRadianceProperties
from .properties.room2d import Room2DRadianceProperties
from .properties.context import ContextShadeRadianceProperties


# set a hidden radiance attribute on each core geometry Property class to None
# define methods to produce radiance property instances on each Property instance
ModelProperties._radiance = None
BuildingProperties._radiance = None
StoryProperties._radiance = None
Room2DProperties._radiance = None
ContextShadeProperties._radiance = None


def model_radiance_properties(self):
    if self._radiance is None:
        self._radiance = ModelRadianceProperties(self.host)
    return self._radiance


def building_radiance_properties(self):
    if self._radiance is None:
        self._radiance = BuildingRadianceProperties(self.host)
    return self._radiance


def story_radiance_properties(self):
    if self._radiance is None:
        self._radiance = StoryRadianceProperties(self.host)
    return self._radiance


def room2d_radiance_properties(self):
    if self._radiance is None:
        self._radiance = Room2DRadianceProperties(self.host)
    return self._radiance


def context_radiance_properties(self):
    if self._radiance is None:
        self._radiance = ContextShadeRadianceProperties(self.host)
    return self._radiance


# add radiance property methods to the Properties classes
ModelProperties.radiance = property(model_radiance_properties)
BuildingProperties.radiance = property(building_radiance_properties)
StoryProperties.radiance = property(story_radiance_properties)
Room2DProperties.radiance = property(room2d_radiance_properties)
ContextShadeProperties.radiance = property(context_radiance_properties)
