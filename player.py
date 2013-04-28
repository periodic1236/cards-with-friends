#!/usr/bin/env python2.7
#
# Copyright 2013 Cards with Friends LLC. All Rights Reserved.

"""Implementation of a player in a game."""

__author__ = "ding@caltech.edu (David Ding)"

import collections
import uuid
from card import Card


class Player(object):
  """A player in a game."""

  def __init__(self, name):
    self._id = uuid.uuid4()
    self._name = name
    self._hand = Hand(self)
    self._taken = set()
    self._score = None
    self._money = None

  def __repr__(self):
    return "{}({}, score={}, uuid={})".format(self.__class__.__name__,
                                              self.name,
                                              self.score,
                                              self.id)

  def AddToHand(self, *cards):
    return self.hand.Add(*cards)

  def ClearHand(self):
    self.hand.Clear()

  def ClearTaken(self):
    self.taken.clear()

  def GetBid(self):
    # TODO(brazon): Interact with front-end to get bid.
    bid = None
    return bid

  def GetPlay(self, error_msg, valid_plays, num_cards=1, callback=None):
    # TODO(brazon): Interact with front-end to get card.
    if num_cards < 1:
      raise ValueError("num_cards must be positive, got %d" % num_cards)
    cards = []
    self.hand.Remove(*cards)
    result = cards if num_cards > 1 else cards[0]
    if callback is None:
      return result
    callback(result)

  def MaybeGetPlay(self, num_cards=1, callback=None):
    # TODO(brazon)
    result = None
    if callback is None:
      return result
    callback(result)

  def Take(self, *cards):
    if not all(isinstance(item, Card) for item in cards):
      # TODO(mqian): Raise a more meaningful error.
      raise TypeError
    self.taken |= set(cards)
    return True

  @property
  def hand(self):
    return self._hand

  @property
  def id(self):
    return self._id

  @property
  def money(self):
    return self._money

  @property
  def name(self):
    return self._name

  @property
  def score(self):
    return self._score

  @score.setter
  def score(self, value):
    self._score = value

  @property
  def taken(self):
    return self._taken


class Hand(object):
  """A player's hand."""

  def __init__(self, player):
    self._player = player
    self._cards = set()

  def __contains__(self, item):
    return item in self._cards

  def __iter__(self):
    return iter(self._cards)

  def __len__(self):
    return len(self._cards)

  def __repr__(self):
    return "{}({})".format(self.__class__.__name__, self._cards)

  def Add(self, *cards):
    """Add one or more cards to the player's hand."""
    if not all(isinstance(item, Card) for item in cards):
      # TODO(mqian): Raise a more meaningful error.
      raise TypeError
    self._cards |= set(cards)
    return True

  def Clear(self):
    """Remove all cards from the player's hand."""
    self._cards.clear()

  def Remove(self, *cards):
    """Remove one or more cards from the player's hand."""
    temp = set(cards)
    if not temp <= self._cards:
      # TODO(mqian): Raise a more meaningful error.
      raise ValueError
    self._cards -= temp
    return True


if __name__ == "__main__":
  pass