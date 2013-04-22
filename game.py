#!/usr/bin/env python2.7
#
# Copyright 2013 Cards with Friends LLC. All Rights Reserved.

"""Abstract class for card games."""

__author__ = "ding@caltech.edu (David Ding)"

import collections
from player import Player
from pylib import utils


class Game(object):
  """A card game."""

  def __init__(self, deck, players):
    """Constructor.

    Args:
      deck: The name of the deck for this game.
      players: A sequence containing player names.
    """
    # The deck of cards to use
    self._deck = Deck.fromjson(utils.CheckPath("decks", deck + ".json"))

    # The players of the game
    self._players = collections.OrderedDict()
    for i, name in enumerate(players):
      self._players[name] = Player(name)
    self._num_players = len(self.players)

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