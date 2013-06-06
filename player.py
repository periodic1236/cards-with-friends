#!/usr/bin/env python2.7
#
# Copyright 2013 Cards with Friends LLC. All Rights Reserved.

"""Implementation of a player in a game."""

__author__ = "ding@caltech.edu (David Ding)"

import collections
import uuid
from card import Card
from pylib import utils
from pylib.mixins import MessageMixin


class Player(MessageMixin):
  """A player in a game."""

  def __init__(self, name):
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
    """Add cards to the player's hand."""
    return self.hand.Add(*cards)

  def AddToScore(self, score):
    """Add the specified amount to the player's current score."""
    self.score += score

  def ClearHand(self):
    """Clear the player's hand"""
    self.hand.Clear()

  def ClearTaken(self):
    """Clear the cards that the player has taken."""
    self.taken.clear()
    self.Notify("clear_taken", player=self.name)

  def GetBid(self, message, valid_bids, validator=None, callback=None):
    """Get a bid from the player, given the message to tell them and the valid bids they can make."""
    validated = False
    while not validated:
      bid = self.Request("get_bid", message=message, player=self.name, valid_bids=valid_bids)
      if bid not in valid_bids:
        raise RuntimeError("Returned bid was not valid: {}".format(bid))
      if validator is not None:
        bid = validator(bid)
        validated = bid is not False
      else:
        validated = True
    if callback is not None:
      callback(bid)
    return bid

  def GetCard(self, message, valid_cards, num_cards=1, validator=None, callback=None):
    """Get cards from the player, given the message to tell them, the valid cards they can play, and the number of cards to play (default set to 1)"""
    if num_cards < 1:
      raise ValueError("num_cards must be positive, got {}".format(num_cards))
    validated = False
    while not validated:
      cards = self.Request("get_card", message=message, player=self.name, valid_cards=valid_cards,
                           num_cards=num_cards)
      if len(cards) != num_cards:
        raise RuntimeError("Expected {} cards, got {}".format(num_cards, len(cards)))
      if not all(c in valid_cards for c in cards):
        raise RuntimeError("Received an invalid play: {}".format(cards))
      if validator is not None:
        cards = validator(cards)
        validated = cards is not False
      else:
        validated = True
    self.hand.Remove(*cards)
    if callback is not None:
      callback(cards)
    return cards

  def GetPlay(self, message, valid_cards, num_cards=1, validator=None, callback=None):
    """Get cards from the player, given the message to tell them, the valid cards they can play, and the number of cards to play (default set to 1)"""
    cards = self.GetCard(message, valid_cards, num_cards, validator, callback)
    self.Notify("played_card", player=self.name, cards=cards)
    return cards

  def Take(self, *cards):
    """Add cards to the cards a player has taken."""
    temp = set(cards)
    if not all(isinstance(item, Card) for item in temp):
      # TODO(mqian): Raise a more meaningful error.
      raise TypeError
    self.taken |= temp
    self.Notify("take_trick", player=self.name, cards=temp)
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
    self.Notify("update_money", player=self.name, money=value)

  @property
  def name(self):
    return self._name

  @property
  def score(self):
    return self._score

  @score.setter
  def score(self, value):
    self._score = value
    self.Notify("update_score", player=self.name, score=value)

  @property
  def taken(self):
    return self._taken

  @taken.setter
  def taken(self, value):
    self._taken = value


class _Hand(MessageMixin):
  """A player's hand."""

  def __init__(self, player):
    self._player = player
    self._cards = set()

  def __contains__(self, item):
    if isinstance(item, basestring):
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
    self.Notify("add_card", player=self.player.name, cards=cards)
    return True

  def Clear(self):
    """Remove all cards from the player's hand."""
    self._cards.clear()
    self.Notify("clear_hand", player=self.player.name)

  def Remove(self, *cards):
    """Remove one or more cards from the player's hand."""
    temp = set(cards)
    if not temp <= self._cards:
      # TODO(mqian): Raise a more meaningful error.
      raise ValueError
    self._cards -= temp
    self.Notify("remove_card", player=self.player.name, cards=cards)
    return True

  @property
  def player(self):
    return self._player


if __name__ == "__main__":
  pass