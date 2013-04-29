#!/usr/bin/env python2.7
#
# Copyright 2013 Cards with Friends LLC. All Rights Reserved.

"""Implementation of the Spades trick-taking card game."""

__author__ = "ding@caltech.edu (David Ding)"

from ..trick_taking_game import TrickTakingGame

class Spades(TrickTakingGame):
  """The Spades card game."""

  def __init__(self, players, deck=None, manager=None):
    super(Hearts, self).__init__(players, deck or "standard", manager)
    self.ResetGame()

  def PlayGame(self):
    """Play the game."""
    # Play until a team's score is >= 500.
    while not self._IsTerminal():
      # Reset hands, shuffle, and deal cards.
      self._NewRound()
      # Get bids from each player
      self._Bid()

      # Play 13 tricks.
      for i in xrange(13):
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
    return sorted(self._players, key=lambda x: x.score)


  def ResetGame(self):
    """Reset the entire game state."""
    # Initialize players.
    self.ResetPlayers(score=0)

    # Establish initial round state.
    self._state.clear()
    self._state.round_num = 0
    self._state.team_scores = [0, 0]

  def _GetTrickWinner(self):
    """Determine who won the most recent trick"""

  def _GetValidMoves(self, player):
    """Get a valid move from the given player."""
    # If the play leads the trick.
    if not self.cards_played:
      # If spades is broken, any play from the hand is valid.
      if self.spades_broken:
        return (None, list(player.hand))
      # Otherwise, cannot play spades if hand has other suits.
      other = any(c.suit != "spades" for c in player.hand)
      return ("Spades not broken",
              [c for c in player.hand if (c.suit != "spades" if other else True)])
    # Otherwise, must follow suit if possible.
    lead_suit = self.cards_played[0].suit
    follow = [c for c in player.hand if c.suit == lead_suit]
    if follow:
      return ("Must follow suit", follow)
    # If can't follow suit and this is the first trick, cannot spades if
    # hand has other suits.
    if not self.trick_num:
      other = any(c.suit != "spades" for c in player.hand)
      return ("Cannot play spades on the first trick (unless all spades)",
              [c for c in player.hand if (c.suit != "spades" if other else True)])
    # At this point, any play from the hand is valid.
    return (None, list(player.hand))

  def _GetValidPlay(self, player):
    card = player.GetPlay(*self._GetValidMoves(player))
    if card.suit == "spades" and not self.spades_broken:
      self.spades_broken = True
    return card

  def _GetValidBids(self, player):
    """Return a list of valid bids for the given player based on the current state."""
    return ("Bid must be between 1 and 13, inclusive", range(1, 14))

  def _GetValidBid(self, player):
    """Get a valid bid from the given player."""
    return player.GetBid(*self._GetValidBids(player))

  def _IsTerminal(self):
    return max(self.team_scores) >= 500

  def _NewRound(self):
    self.round_num += 1
    if self.round_num == 1:
      self._state.dealer = 0
    else:
      self.dealer = self.GetPlayerByIndex(self.dealer + 1)
    self._state.update({
        "cards_played": [],
        "player_bids": [0] * 4
        "spades_broken": False,
        "lead": self.dealer + 1,
        "trick_num": 0,
    })
    self.ResetPlayers()
    self.deck.Shuffle()
    self._DealCards(0, (len(self.deck) // self.num_players, [1] * self.num_players))

  def _ScoreRound(self):
    """Update team scores"""
    tricks_taken = [len(p.hand) / 4 for p in self.players]
    team_bids = [self.player_bids[0] + self.player_bids[2], self.player_bids[1] + self.player_bids[3]]
    team_taken = [tricks_taken[0] + tricks_taken[2], tricks_taken[1] + tricks_taken[3]]

    for i in xrange(2):
      # If the team took less than they bid, penalize them 10 per bid
      if team_bids[i] > team_taken[i]:
        self.team_scores[i] -= 10 * team_bids[i]
      # Otherwise, add 10 per bid plus 1 per extra trick ("bag") taken
      else:
        num_bags = team_taken[i] - team_bids[i]
        self.team_scores[i] += 10 * team_taken + num_bags

      # Update individual player scores based on new team scores
      self.players[i] = self.team_scores[i]
      self.players[i + 2] = self.team_scores[i]

  def _Bid(self):
    """Get bids from each player."""
    for i in xrange(num_players):
      # Proceed clockwise starting from the dealer's left
      bidder = self.dealer + 1 + i
      self.player_bids[bidder] = GetValidBid(GetPlayerByIndex(bidder))


if __name__ == "__main__":
  pass