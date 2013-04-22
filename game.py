#!/usr/bin/env python2.7
#
# Copyright 2013 Cards with Friends LLC. All Rights Reserved.

"""Abstract class for card games."""

__author__ = "ding@caltech.edu (David Ding)"

import collections
import uuid
from player import Player
from pylib import utils


class Game(object):
  """A card game."""

  def __init__(self, players, deck):
    """Constructor.

    Args:
      players: A sequence containing player names.
      deck: The name of the deck for this game.
    """
    # A unique ID for the game.
    self._id = uuid.uuid1()

    # The deck of cards to use.
    self._deck = Deck.fromjson(utils.CheckPath("decks", deck + ".json"))

    # The players of the game.
    self._players = collections.OrderedDict()
    for i, name in enumerate(players):
      self._players[name] = Player(name)
    self._num_players = len(self.players)
    self._dealer = None

  @property
  def dealer(self):
    return self._dealer

  @property
  def deck(self):
    return self._deck

  @property
  def num_players(self):
    return self._num_players

  @property
  def players(self):
    return self._players

  @property
  def players_by_index(self):
    return dict(x for x in enumerate(self.players))


if __name__ == "__main__":
  pass