#!/usr/bin/env python2.7
#
# Copyright 2013 Cards with Friends LLC. All Rights Reserved.

"""Implementation of a playing card."""

__author__ = "razon.ben@gmail.com (Ben Razon)"

import collections
import os
from PIL import Image
from pylib import utils

_CARD_IMAGE_BASE = "card_images"


class Card(object):
  """A playing card."""

  def __init__(self, name, long_name, image_loc, **props):
    self._name = name
    self._long_name = long_name
    self._image_loc = utils.CheckPath(_CARD_IMAGE_BASE, image_loc)
    self._props = collections.OrderedDict(sorted(props.items()))
    self._faceup = False

  def __attrs(self):
    return tuple([self.name, self.long_name] + self.props.values())

  def __eq__(self, other):
    return isinstance(other, Card) and self.__attrs() == other.__attrs()

  def __getattribute__(self, name):
    try:
      return object.__getattribute__(self, "_props")[name]
    except KeyError:
      return object.__getattribute__(self, name)

  def __hash__(self):
    return hash(self.__attrs())

  def __ne__(self, other):
    return not self.__eq__(other)

  def __repr__(self):
    return self._name

  def __str__(self):
    return self._long_name

  def Flip(self):
    self.faceup = not self.faceup

  def GetImage(self):
    return Image.open(self.image_loc)

  @property
  def faceup(self):
    return self._faceup

  @faceup.setter
  def faceup(self, value):
    self.faceup = bool(value)

  @property
  def image_loc(self):
    return self._image_loc

  @property
  def long_name(self):
    return self._long_name

  @property
  def name(self):
    return self._name

  @property
  def props(self):
    return self._props