#!/usr/bin/env python2.7
#
# Copyright 2013 Cards with Friends LLC. All Rights Reserved.

"""Implementation of a player in a game."""

__author__ = "ding@caltech.edu (David Ding)"

import collections
from card import Card


def Player(object):
  """A player in a game."""

  def __init__(self, name):
    self._name = name
    self._hand = Hand(self)
    self._score = None
    self._money = None
    self._taken = collections.Counter()

  def ClearHand(self):
    self._hand.clear()

  def ClearTaken(self):
    self._taken.clear()

  def GetBet(self):
    # TODO(brazon): Interact with front-end to get bet.
    bet = None
    return bet

  def GetPlay(self):
    # TODO(brazon): Interact with front-end to get card.
    card = None
    return card

  def Take(self, *cards):
    for card in cards:
      self._taken[card] += 1

  @property
  def hand(self):
    return self._hand

  @property
  def score(self):
    return self._score

  @score.setter
  def score(self, value):
    self._score = value

  @property
  def money(self):
    return self.money

  @property
  def taken(self):
    return self._taken.elements()


class Hand(object):
  """A player's hand."""

  def __init__(self, player):
    self._player = player
    self._cards = collections.Counter()

  def __contains__(self, item):
    if not isinstance(item, Card):
      return False
    return bool(self._cards[card])

  def Add(self, *cards):
    """Add one or more cards to the player's hand."""
    for card in cards:
      self._cards[card] += 1

  def Clear(self):
    """Remove all cards from the player's hand."""
    self._cards.clear()

  def Remove(self, *cards):
    """Remove one or more cards from the player's hand."""
    if not all(card in self for card in cards):
      # TODO(mqian): Raise a more meaningful error.
      raise KeyError
    for card in cards:
      self._cards[card] -= 1
    return True


if __name__ == "__main__":
  pass