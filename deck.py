#!/usr/bin/env python
#
# Copyright 2013 Cards with Friends LLC. All Rights Reserved.

"""Implementation of a deck of playing cards."""

__author__ = "razon.ben@gmail.com (Ben Razon)"

import json
import os
import random

from PIL import Image

from card import Card


class Deck(object):
  """A deck of playing cards."""

  def __init__(self, name, long_name, labels, cards, back_image_loc):
    """Create a deck from a list of cards.

    Args:
      labels: A list of properties all the cards have.
      cards: A list of elements (name, long_name, image_loc, values).
    """
    self._name = name
    self._long_name = long_name
    self._num_cards = len(cards)
    self._back_image_loc = back_image_loc
    self._cards_list = [None] * self._num_cards
    for i in xrange(self._num_cards):
      card = cards[i]
      self._cards_list[i] = Card(card[0], card[1], card[2], labels, card[3])

  @classmethod
  def fromjson(cls, filename):
    """Create a deck from a JSON file.

    The file format is explained elsewhere.
    """
    # TODO(brazon): add reference to documentation
    with open(filename, "r") as f:
      json_deck = json.load(f)
    for field in ("name", "long_name", "labels", "cards", "back_image_loc"):
      if field not in json_deck:
        raise KeyError("Missing JSON key: %s" % field)
    name = json_deck["name"]
    long_name = json_deck["long_name"]
    labels = [i["name"] for i in json_deck["labels"]]
    cards = [(c["name"], c["long_name"], c["image_loc"], [c[j] for j in labels])
             for c in json_deck["cards"]]
    back_image_loc = json_deck["back_image_loc"]
    return cls(name, long_name, labels, cards, back_image_loc)

  def get_back_image(self):
    return Image.open(self.back_image_loc)

  def get_next_card(self, num_cards=0):
    """Remove and return the top card from the deck.

    This also updates num_cards.
    """
    if self._num_cards <= 0:
      raise IndexError("Tried to get card from empty deck.")
    self._num_cards -= 1
    return self._cards_list.pop(0)

  def shuffle(self):
    random.shuffle(self._cards_list)

  def write_to_file(self, filename, indent=2):
    if os.path.exists(filename):
      raise IOError("You don't have permission to overwrite files.")
    with open(filename, "w+") as f:
      # TODO(brazon): Figure out how to recreate json
      raise NotImplementedError("TODO(brazon)")

  @property
  def back_image_loc(self):
    return os.path.join("card-images", os.path.basename(self._back_image_loc))

  @property
  def long_name(self):
    return self._long_name

  @property
  def name(self):
    return self._name

  @property
  def num_cards(self):
    return self._num_cards