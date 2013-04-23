#!/usr/bin/env python2.7
#
# Copyright 2013 Cards with Friends LLC. All Rights Reserved.

"""Abstract class for card games."""

__author__ = "ding@caltech.edu (David Ding)"

import collections
import uuid
from deck import Deck
from player import Player
from pylib import utils


class Game(object):
  """A card game."""

  def __init__(self, players, deck):
    """Constructor.

    Args:
      players: A sequence of player names (expected to be unique).
      deck: The name of the deck for this game.
    """
    # A unique ID for the game.
    self._id = uuid.uuid1()

    # State variables.
    self._state = utils.AttributeDict()

    # The deck of cards to use.
    try:
      self._deck = Deck.fromjson(utils.CheckPath(deck + ".json", utils.DECK_BASE))
    except IOError:
      raise ValueError("Invalid deck name '{}', deck not found".format(deck))

    # The players of the game.
    if not players:
      raise ValueError("Players cannot be empty")
    self._players = [Player(name) for name in players]
    self._num_players = len(self.players)

  def __getattribute__(self, name):
    try:
      return object.__getattribute__(self, "_state")[name]
    except KeyError:
      return object.__getattribute__(self, name)

  def __repr__(self):
    return "{}({}, deck={}, players={})".format(self.__class__.__name__,
                                                self.id,
                                                self.deck.name,
                                                list(self.players))

  def GetPlayerByIndex(self, index):
    return self.players[index % self._num_players]

  def GetPlayerByName(self, name):
    for player in self.players:
      if player.name == name:
        return player

  def GetPlayerIndex(self, player):
    return self.players.index(player)

  def ResetPlayers(self, score=None):
    """Reset the state of every player."""
    for player in self.players:
      player.ClearHand()
      player.ClearTaken()
      if score is not None:
        player.score = score

  @property
  def dealer(self):
    return self._dealer

  @property
  def deck(self):
    return self._deck

  @property
  def id(self):
    return self._id

  @property
  def num_players(self):
    return self._num_players

  @property
  def players(self):
    return self._players

  @property
  def players_by_name(self):
    return dict((player.name, player) for player in self.players)


if __name__ == "__main__":
  pass