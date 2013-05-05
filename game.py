#!/usr/bin/env python2.7
#
# Copyright 2013 Cards with Friends LLC. All Rights Reserved.

"""Abstract class for card games."""

__author__ = "ding@caltech.edu (David Ding)"

import collections
import threading
import uuid
from deck import Deck
from player import Player
from pylib import thread_tools
from pylib import utils

NUM_THREADS = 8


class Game(object):
  """A card game."""

  def __init__(self, players, deck, manager=None):
    """Constructor.

    Args:
      players: A sequence of player names (expected to be unique).
      deck: The name of the deck for this game.
    """
    # Container for state variables.
    self._state = utils.AttributeDict()

    # Thread tools.
    self._manager = thread_tools.EventManager(NUM_THREADS) if manager is None else manager
    self._lock = threading.RLock()
    self._condition = threading.Condition(self._lock)

    # A unique ID for the game.
    self._id = uuid.uuid1()

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
    self._dealer = None

  def __getattribute__(self, name):
    try:
      return object.__getattribute__(self, "_state")[name]
    except (AttributeError, KeyError):
      return object.__getattribute__(self, name)

  def __repr__(self):
    return "{}({}, deck={}, players={})".format(self.__class__.__name__,
                                                self.id,
                                                self.deck.name,
                                                list(self.players))

  def __setattr__(self, name, value):
    if hasattr(self, "_state") and name in self._state:
      self._state[name] = value
    else:
      object.__setattr__(self, name, value)

  def GetPlayerByIndex(self, index):
    return self.players[index % self.num_players]

  def GetPlayerByName(self, name):
    try:
      return next(player for player in self.players if player.name == name)
    except StopIteration:
      raise ValueError("Player '{}' not found in this game".format(name))

  def GetPlayerIndex(self, player):
    if not isinstance(player, (Player, int)):
      raise TypeError("player must be a Player or int, got type '{}'".format(type(player)))
    try:
      return player % self.num_players if isinstance(player, int) else self.players.index(player)
    except ValueError:
      raise ValueError("Player '{}' not found in this game".format(player.name))

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

  @dealer.setter
  def dealer(self, value):
    self._dealer = value

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