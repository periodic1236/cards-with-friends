#!/usr/bin/env python2.7
#
# Copyright 2013 Cards with Friends LLC. All Rights Reserved.

"""Implementation of a player in a game."""

__author__ = "ding@caltech.edu (David Ding)"

import collections
import uuid
from card import Card
import card_frontend
from pylib import utils


class Player(utils.MessageMixin):
  """A player in a game."""

  def __init__(self, name):
    super(Player, self).__init__()
    self._id = uuid.uuid4()
    self._name = utils.Sanitize(name)
    self._hand = _Hand(self)
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

  def AddToScore(self, score):
    self.score += score

  def ClearHand(self):
    self.hand.Clear()

  def ClearTaken(self):
    self.taken.clear()
    self.Notify(self, "clear_taken")

  def GetBid(self, error_msg, valid_bids, callback=None):
    bid = self.Request(self, "get_bid", valid_bids=valid_bids)
    if callback is None:
      return bid
    callback(bid)

  def GetPlay(self, error_msg, valid_plays, num_cards=1, callback=None):
    if num_cards < 1:
      raise ValueError("num_cards must be positive, got {}".format(num_cards))
    # TODO(brazon): Figure out what to do about multi-card plays...
    if num_cards > 1:
      raise NotImplementedError("Multi-card moves break things")
    cards = self.Request(self, "get_play", valid_plays=valid_plays, num_cards=num_cards)
    self.hand.Remove(*cards)
    if callback is None:
      return cards
    callback(cards)

  def MaybeGetPlay(self, num_cards=1, callback=None):
    # TODO(brazon)
    cards = None
    if callback is None:
      return cards
    callback(cards)

  def Take(self, *cards):
    temp = set(cards)
    if not all(isinstance(item, Card) for item in temp):
      # TODO(mqian): Raise a more meaningful error.
      raise TypeError
    self.taken |= temp
    self.Notify(self, "take_trick", cards=temp)
    return True

  @property
  def hand(self):
    return self._hand

  @property
  def id(self):
    return str(self._id)

  @property
  def money(self):
    return self._money

  @money.setter
  def money(self, value):
    self._money = value
    self.Notify(self, "update_money", money=value)

  @property
  def name(self):
    return self._name

  @property
  def score(self):
    return self._score

  @score.setter
  def score(self, value):
    self._score = value
    self.Notify(self, "update_score", score=value)

  @property
  def taken(self):
    return self._taken


class _Hand(utils.MessageMixin):
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
    temp = set(cards)
    if not all(isinstance(item, Card) for item in temp):
      # TODO(mqian): Raise a more meaningful error.
      raise TypeError
    self._cards |= temp
    self.Notify(self.player, "add_card", cards=temp)
    return True

  def Clear(self):
    """Remove all cards from the player's hand."""
    self._cards.clear()
    self.Notify(self.player, "clear_hand")

  def Remove(self, *cards):
    """Remove one or more cards from the player's hand."""
    temp = set(cards)
    if not temp <= self._cards:
      # TODO(mqian): Raise a more meaningful error.
      raise ValueError
    self._cards -= temp
    self.Notify(self.player, "remove_card", cards=temp)
    return True

  @property
  def player(self):
    return self._player


if __name__ == "__main__":
  pass
