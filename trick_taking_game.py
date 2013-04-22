#!/usr/bin/env python2.7
#
# Copyright 2013 Cards with Friends LLC. All Rights Reserved.

"""Abstract class for trick-taking card games."""

__author__ = "mqian@caltech.edu (Mike Qian)"

import collections
from game import Game


class TrickTakingGame(Game):
  """A trick-taking game."""

  def __init__(self, deck, players):
    """Constructor.

    Args:
      deck: The name of the deck for this game.
      players: A sequence containing player names.
    """
    # Invoke superclass constructor.
    super(TrickTakingGame, self).__init__(deck, players)

  def DealCards(self, first_deal, patterns):
    """Deal cards to players.

    Args:
      first_deal: The identifier of the first player to deal to.
      patterns: A list of tuples of the form (# phases, deal pattern).
    Usage:
      self.DealCards("alpha", [(13, [1, 1, 1, 1])])
    """
    if first_deal not in self.players:
      # TODO(mqian): Raise a more meaningful error.
      raise ValueError
    if len(self.deck) < sum(i * sum(j) for i, j in patterns):
      # TODO(mqian): Raise a more meaningful error.
      raise ValueError
    self.deck.Shuffle()
    deal_idx = self.players.keys().index(first_deal)
    players = self.players.values()
    for num_phases, pattern in patterns:
      for _ in xrange(num_phases):
        for num_cards in pattern:
          players[deal_idx].hand.add(*self.deck.Draw(num_cards))
          deal_idx = (deal_idx + 1) % self.num_players

  def EvaluateTrick(self, *args, **kwargs):
    raise NotImplementedError("This class should be implemented by users.")

  def IsTerminal(self, *args, **kwargs):
    raise NotImplementedError("This class should be implemented by users.")

  def PlayGame(self, *args, **kwargs):
    raise NotImplementedError("This class should be implemented by users.")


if __name__ == "__main__":
  pass