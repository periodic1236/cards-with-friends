#!/usr/bin/env python2.7
#
# Copyright 2013 Cards with Friends LLC. All Rights Reserved.

"""Implementation of a playing card."""

__author__ = "razon.ben@gmail.com (Ben Razon)"

import collections
import os
import uuid
from PIL import Image
from pylib import utils

_CARD_IMAGE_DIR = "static/card_images"


class Card(object):
  """A playing card."""

  def __init__(self, name, long_name, image_loc, **props):
    self._id = uuid.uuid4()
    self._name = utils.Sanitize(name)
    self._long_name = long_name
    self._image_loc = utils.CheckPath(image_loc, _CARD_IMAGE_DIR)
    if not props:
      raise ValueError("Card properties cannot be empty")
    self._props = collections.OrderedDict(sorted(props.items()))
    self._faceup = False

  def __attrs(self):
    return (self._faceup, tuple(self.props))

  def __eq__(self, other):
    return isinstance(other, Card) and self.__attrs() == other.__attrs()

  def __getattribute__(self, name):
    try:
      return object.__getattribute__(self, "_props")[name]
    except KeyError:
      return object.__getattribute__(self, name)

  def __ne__(self, other):
    return not self.__eq__(other)

  def __repr__(self):
    return "{}({}, {})".format(self.__class__.__name__,
                               "{}{}".format(self._name, "" if self.faceup else "*"),
                               ", ".join("{}={}".format(*x) for x in self.props))

  def __str__(self):
    return self._long_name

  def Flip(self):
    """Flip the card between face up and face down."""
    self.faceup = not self.faceup

  def GetImage(self):
    """Get the image of the card"""
    return Image.open(self.image_loc)

  @property
  def faceup(self):
    return self._faceup

  @faceup.setter
  def faceup(self, value):
    self._faceup = bool(value)

  @property
  def id(self):
    return str(self._id)

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
    return self._props.items()