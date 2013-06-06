#!/usr/bin/env python2.7
#
# Copyright 2013 Cards with Friends LLC. All Rights Reserved.

"""Abstract class for trick-taking card games."""

__author__ = "mqian@caltech.edu (Mike Qian)"

import collections
from game import Game
from player import Player


class TrickTakingGame(Game):
  """A trick-taking game."""

  def __init__(self, players, deck):
    """Constructor.

    Args:
      players: A list of Player objects.
      deck: The name of the deck for this game.
    """
    super(TrickTakingGame, self).__init__(players, deck)

  @classmethod
  def GetCardValue(cls, *args, **kwargs):
    raise NotImplementedError("This method should be implemented by users.")

  @classmethod
  def SortCards(cls, cards, reverse=True):
    """Sort a list of cards by value. Returns an iterator."""
    return iter(sorted(cards, key=cls.GetCardValue, reverse=reverse))

  def PlayGame(self, *args, **kwargs):
    raise NotImplementedError("This method should be implemented by users.")

  def ResetGame(self, *args, **kwargs):
    raise NotImplementedError("This method should be implemented by users.")

  def _DealCards(self, first, *patterns):
    """Deal cards to players.

    Args:
      first: The first player to deal to (or his index).
      patterns: Tuples of the form (# phases, deal pattern).
    Usage:
      self.DealCards(0, (13, [1, 1, 1, 1]))
    """
    if not isinstance(first, (Player, int)):
      raise TypeError("first must be a Player or int, got type '{}'".format(type(first)))
    try:
      deal_idx = first if isinstance(first, int) else self.GetPlayerIndex(first)
    except ValueError:
      raise ValueError("Player '{}' not found in this game".format(first.name))
    if len(self.deck) < sum(i * sum(j) for i, j in patterns):
      raise ValueError("Not enough cards for the given deal pattern")
    drawn = collections.defaultdict(set)
    for num_phases, pattern in patterns:
      for _ in xrange(num_phases):
        for num_cards in pattern:
          drawn[self.GetPlayerByIndex(deal_idx)] |= set(self.deck.Draw(num_cards))
          deal_idx += 1
    for player, cards in drawn.items():
      player.AddToHand(*self.SortCards(cards, reverse=False))

  def _EvaluateTrick(self, *args, **kwargs):
    raise NotImplementedError("This method should be implemented by users.")

  def _GetFirstPlayer(self, *args, **kwargs):
    raise NotImplementedError("This method should be implemented by users.")

  def _IsTerminal(self, *args, **kwargs):
    raise NotImplementedError("This method should be implemented by users.")

  def _NewRound(self, *args, **kwargs):
    raise NotImplementedError("This method should be implemented by users.")

  def _PassCards(self, *patterns):
    """Pass cards between players.
    Args:
      patterns: Tuples of the form (from, to, # cards[, list of valid cards]).
    Usage:
      self.PassCards(...)
    """
    accum = collections.defaultdict(set)

    def process(from_, to, num_cards, valid=None):
      valid = list(from_.hand) if valid is None else list(valid)
      message = "Select {} cards to pass to {}".format(num_cards, to.name)
      self.Notify("display_message", player=from_.name, message=message)
      cards = from_.GetCard("Cannot pass selected card", valid, num_cards)
      if not isinstance(cards, collections.Iterable):
        cards = [cards]
      accum[to] |= set(cards)

    for pattern in patterns:
      process(*pattern)
    for to, cards in accum.items():
      to.AddToHand(*self.SortCards(cards, reverse=False))


if __name__ == "__main__":
  pass
