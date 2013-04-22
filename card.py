#!/usr/bin/env python2.7
#
# Copyright 2013 Cards with Friends LLC. All Rights Reserved.

"""Implementation of a playing card."""

__author__ = "razon.ben@gmail.com (Ben Razon)"

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
    self._props = dict(props)

  def __repr__(self):
    return self._name

  def __str__(self):
    return self._long_name

  def __getattribute__(self, name):
    try:
      return object.__getattribute__(self, "_props")[name]
    except KeyError:
      return object.__getattribute__(self, name)

  def GetImage(self):
    return Image.open(self.image_loc)

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