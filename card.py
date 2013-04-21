#!/usr/bin/env python
#
# Copyright 2013 Cards with Friends LLC. All Rights Reserved.

"""Implementation of a playing card."""

__author__ = "razon.ben@gmail.com (Ben Razon)"

import os

from PIL import Image


class Card(object):
  """A playing card."""

  def __init__(self, short_name, long_name, image_loc, labels, values):
    self._short_name = short_name
    self._long_name = long_name
    self._image_loc = image_loc
    self._properties = dict(zip(labels, values))

  def get_image(self):
    return Image.open(self.image_loc)

  @property
  def short_name(self):
    return self._short_name

  @property
  def long_name(self):
    return self._long_name

  @property
  def image_loc(self):
    return os.path.join("card-images", os.path.basename(self._image_loc))

  @property
  def properties(self):
    return self._properties