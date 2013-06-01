#!/usr/bin/env python2.7
#
# Copyright 2013 Cards with Friends LLC. All Rights Reserved.

"""Implementation of the Highest Card trick-taking card game."""

__author__ = "ding@caltech.edu (David Ding)"

from trick_taking_game import TrickTakingGame


class HighestCard(TrickTakingGame):
  """The Highest Card card game."""

  def __init__(self, players, deck=None):
    if len(players) != 2:
      raise ValueError("Highest Card is a 2-player game, got {} players".format(len(players)))
    super(HighestCard, self).__init__(players, deck or "standard")
    self.ResetGame()

  def PlayGame(self):
    """Play the game."""
    # Play until someone's score is >= 6.
    while not self._IsTerminal():
      # Reset hands, shuffle, and deal cards.
      self._NewRound()
      # Identify first player of the round.
      self.lead = self._FindFirstPlayer()
      # Play tricks.
      #for _ in xrange(len(self.deck) // self.num_players):
      for _ in xrange(5):
        self.trick_num += 1
        self.cards_played = []
        # Have each player play a valid card for the trick.
        for i in xrange(self.num_players):
          play = self._GetValidPlay(self.GetPlayerByIndex(self.lead + i))
          self.cards_played.append(play)
        # Determine who got the trick, and give them the cards.
        self.lead += self._GetTrickWinner()
        self.lead %= self.num_players
        self.GetPlayerByIndex(self.lead).Take(*self.cards_played)
      # Calculate and add scores.
      self._ScoreRound()
    return sorted(self._players, key=lambda x: x.score, reverse=True)

  def ResetGame(self):
    """Reset the entire game state."""
    # Initialize players.
    self.ResetPlayers(score=0)

    # Establish initial round state.
    self._state.clear()
    self._state.round_num = 0

  def _FindFirstPlayer(self):
    """Find the first player of a round. The first player has the two of clubs."""
    return next(i for (i, p) in enumerate(self.players) if any(c.name == "2C" for c in p.hand))

  def _GetTrickWinner(self):
    """Determine who won the most recent trick."""
    lead_suit = self.cards_played[0].suit
    return max((c.number, i) for (i, c) in enumerate(self.cards_played) if c.suit == lead_suit)[-1]

  def _GetValidMoves(self, player):
    """Return a list of valid moves for the given player based on the current state."""
    return (None, list(player.hand))

  def _GetValidPlay(self, player):
    """Get a valid move from the given player."""
    card = player.GetPlay(*self._GetValidMoves(player))
    return card

  def _IsTerminal(self):
    """Return True iff the game has ended. The game ends when someone's score is >= 100."""
    return max([player.score for player in self.players]) >= 6

  def _NewRound(self):
    """Start a new round of the game."""
    self.round_num += 1
    self._state.update({
        "cards_played": [],
        "lead": None,
        "trick_num": 0,
    })
    self.ResetPlayers()
    self.deck.Shuffle()
    self._DealCards(0, (len(self.deck) // self.num_players, [1] * self.num_players))

  def _ScoreRound(self):
    """Update scores."""
    scores = [0] * self.num_players
    for i, p in enumerate(self.players):
      scores[i] = len(p.taken) / self.num_players
    for p, score in zip(self.players, scores):
      p.AddToScore(score)
