#!/usr/bin/env python2.7
#
# Copyright 2013 Cards with Friends LLC. All Rights Reserved.

"""Implementation of a deck of playing cards."""

__author__ = "razon.ben@gmail.com (Ben Razon)"

import collections
import json
import os
import random
from PIL import Image
from card import Card
from pylib import utils

_CARD_IMAGE_BASE = "card_images"


class Deck(collections.Iterator):
  """A deck of playing cards."""

  def __init__(self, name, long_name, back_image_loc):
    """Create a deck from a list of cards.

    Args:
      name: A unique identifier for the deck.
      long_name: The long name of the deck.
      back_image_loc: The image location for the back of each card.
    """
    self._name = name
    self._long_name = long_name
    self._back_image_loc = utils.CheckPath(_CARD_IMAGE_BASE, back_image_loc)
    self._cards = {}
    self._deck = []

  def __len__(self):
    return len(self._deck)

  @classmethod
  def fromjson(cls, filename):
    """Create a deck from a JSON file.

    The file format is explained elsewhere.
    """
    # TODO(brazon): Add reference to documentation
    deck_keys = ("name", "long_name", "back_image_loc", "labels", "cards")
    card_keys = ("name", "long_name", "image_loc")
    with open(filename, "r") as f:
      d = json.load(f, object_pairs_hook=utils.AttributeDict)
    utils.CheckJSON(d, "deck", deck_keys)
    deck = cls(d.name, d.long_name, d.back_image_loc)
    for c in d.cards:
      utils.CheckJSON(c, "card", card_keys)
      props = dict((l.name, utils.ConvertLabel(c[l.name], l.type)) for l in d.labels)
      deck._AddCard(c.name, c.long_name, c.image_loc, **props)
    deck.Shuffle()
    return deck

  def next(self):
    if not self:
      raise StopIteration
    return self._deck.pop()

  def _AddCard(self, name, long_name, image_loc, **props):
    if name in self._cards:
      raise KeyError("Card already exists: %s" % name)
    self._cards[name] = Card(name, long_name, image_loc, **props)

  def Draw(self, num_cards=1):
    """Remove and return the top num_card cards from the deck (default 1).

    If num_cards > 1, then a list is returned. This also updates num_cards.
    """
    if num_cards < 1:
      raise ValueError("num_cards must be positive, got: %d" % num_cards)
    if len(self) < num_cards:
      raise IndexError("Tried to draw %d cards, but deck only has %d." % 
                       (num_cards, self.num_cards))
    if num_cards > 1:
      return [next(self) for _ in xrange(num_cards)]
    return next(self)

  def GetBackImage(self):
    return Image.open(self.back_image_loc)

  def Shuffle(self, reset=True):
    if reset:
      self._deck = self._cards.values()
    random.shuffle(self._deck)

  def WriteToFile(self, filename, indent=2):
    if os.path.exists(filename):
      raise IOError("You don't have permission to overwrite files.")
    with open(filename, "w+") as f:
      # TODO(brazon): Figure out how to recreate json
      raise NotImplementedError("TODO(brazon)")

  @property
  def back_image_loc(self):
    return self._back_image_loc

  @property
  def long_name(self):
    return self._long_name

  @property
  def name(self):
    return self._name