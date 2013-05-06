#!/usr/bin/env python2.7
#
# Copyright 2013 Cards with Friends LLC. All Rights Reserved.

"""Implementation of a player in a game."""

__author__ = "ding@caltech.edu (David Ding)"

import collections
import uuid
import weakref
from card import Card
from pylib import utils
import card_frontend


class Player(object):
  """A player in a game."""

  def __init__(self, name):
    self._id = uuid.uuid4()
    self._name = utils.Sanitize(name)
    self._hand = Hand(self)
    self._taken = set()
    self._score = None
    self._money = None
    self._subscribers = weakref.WeakKeyDictionary()

  def __repr__(self):
    return "{}({}, score={}, uuid={})".format(self.__class__.__name__,
                                              self.name,
                                              self.score,
                                              self.id)

  def _NotifySubs(self):
    for cv in self._subscribers:
      if not cv.acquire(blocking=False):
        continue
      cv.notify()
      cv.release()

  def AddToHand(self, *cards):
    result = self.hand.Add(*cards)
    self._NotifySubs()
    return result

  def AddToScore(self, score):
    self.score += score
    self._NotifySubs()

  def ClearHand(self):
    self.hand.Clear()
    self._NotifySubs()

  def ClearTaken(self):
    self.taken.clear()
    self._NotifySubs()

  def GetBid(self, error_msg, valid_bids, num_bids=1, callback=None):
    # TODO(brazon): Interact with front-end to get bid.
    if num_bids < 1:
      raise ValueError("num_bids must be positive, got %d" % num_bids)
    bids = []
    result = bids if num_bids > 1 else bids[0]
    if callback is None:
      return result
    callback(result)

  def GetPlay(self, error_msg, valid_plays, num_cards=1, callback=None):
    if num_cards < 1:
      raise ValueError("num_cards must be positive, got %d" % num_cards)
    if num_cards > 1:
      raise NotImplementedError("Multi-card moves break things")
    cards = []
    card_frontend.GetCardFromPlayer(self._name, valid_plays, cards)
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

  def Subscribe(self, ref, condition):
    if ref in self._subscribers:
      raise ValueError("Already subscribed to this player")
    self._subscribers[ref] = condition

  def Take(self, *cards):
    if not all(isinstance(item, Card) for item in cards):
      # TODO(mqian): Raise a more meaningful error.
      raise TypeError
    self.taken |= set(cards)
    self._NotifySubs()
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

  @money.setter
  def money(self, value):
    self._money = value
    self._NotifySubs()

  @property
  def name(self):
    return self._name

  @property
  def score(self):
    return self._score

  @score.setter
  def score(self, value):
    self._score = value
    self._NotifySubs()

  @property
  def taken(self):
    return self._taken


class Hand(object):
  """A player's hand."""

  def __init__(self, player):
    self._player = player
    self._cards = set()

  def __contains__(self, item):
    if isinstance(item, (str, unicode)):
      return bool(utils.FindCard(self._cards, name=item))
    return item in self._cards

  def __iter__(self):
    return iter(self._cards)

  def __len__(self):
    return len(self._cards)

  def __nonzero__(self):
    return bool(self._cards)

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
