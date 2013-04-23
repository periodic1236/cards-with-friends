#!/usr/bin/env python2.7
#
# Copyright 2013 Cards with Friends LLC. All Rights Reserved.

"""Abstract class for trick-taking card games."""

__author__ = "mqian@caltech.edu (Mike Qian)"

import collections
from game import Game


class TrickTakingGame(Game):
  """A trick-taking game."""

  def __init__(self, players, deck):
    super(TrickTakingGame, self).__init__(players, deck)

  def PlayGame(self, *args, **kwargs):
    raise NotImplementedError("This class should be implemented by users.")

  def ResetGame(self, *args, **kwargs):
    raise NotImplementedError("This class should be implemented by users.")

  def _DealCards(self, first, patterns):
    """Deal cards to players.

    Args:
      first: The first player to deal to (or his index).
      patterns: A list of tuples of the form (# phases, deal pattern).
    Usage:
      self.DealCards(0, [(13, [1, 1, 1, 1])])
    """
    if not isinstance(first, Player) and not isinstance(first, int):
      raise TypeError("first must be a Player or int, got type '{}'".format(type(first)))
    try:
      deal_idx = first if isinstance(first, int) else self.GetPlayerIndex(first)
    except ValueError:
      raise ValueError("Player '{}' not found in this game".format(first.name))
    if len(self.deck) < sum(i * sum(j) for i, j in patterns):
      raise ValueError("Not enough cards for the given deal pattern")
    for num_phases, pattern in patterns:
      for _ in xrange(num_phases):
        for num_cards in pattern:
          self.GetPlayerByIndex(deal_idx).AddToHand(*self.deck.Draw(num_cards))
          deal_idx += 1

  def _EvaluateTrick(self, *args, **kwargs):
    raise NotImplementedError("This class should be implemented by users.")

  def _GetFirstPlayer(self, *args, **kwargs):
    raise NotImplementedError("This class should be implemented by users.")

  def _IsTerminal(self, *args, **kwargs):
    raise NotImplementedError("This class should be implemented by users.")

  def _NewRound(self, *args, **kwargs):
    raise NotImplementedError("This class should be implemented by users.")


if __name__ == "__main__":
  pass