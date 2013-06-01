#!/usr/bin/env python2.7
#
# Copyright 2013 Cards with Friends LLC. All Rights Reserved.

"""Implementation of the Hearts trick-taking card game."""

__author__ = "ding@caltech.edu (David Ding)"

from pylib import utils
from trick_taking_game import TrickTakingGame


class Hearts(TrickTakingGame):
  """The Hearts card game."""

  def __init__(self, players, deck=None):
    if len(players) not in (3, 4, 5):
      raise ValueError("Hearts is a 3 to 5 player game, got {} players".format(len(players)))
    super(Hearts, self).__init__(players, deck or "standard")
    if self.num_players == 3:
      self.deck.FindAndRemoveCard(name="2D")
    elif self.num_players == 5:
      self.deck.FindAndRemoveCard(name="2C")
      self.deck.FindAndRemoveCard(name="2D")
    self.ResetGame()

  @classmethod
  def GetCardValue(cls, card):
    """Return the value of a card as prescribed by this game."""
    values = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 1]
    suits = ["spades", "diamonds", "clubs", "hearts"]
    return values.index(card.number) + 13 * suits.index(card.suit)

  def PlayGame(self):
    """Play the game."""
    # Play until someone's score is >= 100.
    while not self._IsTerminal():
      # Reset hands, shuffle, and deal cards.
      self._NewRound()
      # Pass cards left, right, across, or not at all based on the round number.
      # TODO(ding): Remove when support for trading is implemented in non-4-player games.
      if self.num_players == 4:
        self._Trade()

      # Identify first player of the round.
      self.lead = self._FindFirstPlayer()
      # Play 13 tricks.
      while self.GetPlayerByIndex(self.lead).hand:
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

  def _FindFirstPlayer(self):
    """Find the first player of a round. The first player has the two of clubs."""
    start = "3C" if self.num_players == 5 else "2C"
    return next(i for i, p in enumerate(self.players) if any(c.name == start for c in p.hand))

  def _GetPlayAndCheck(self, player):
    card = None
    # If the play leads the trick.
    if not self.cards_played:
      while True:
        card = player.MaybeGetPlay()
        # If hearts is broken, the play is fine regardless.
        if self.hearts_broken:
          break
        # Cannot play queen of spades if hearts not broken.
        if card.name == "QS":
          self.WarnPlayer(player, card, "Hearts not broken")
          player.AddToHand(card)
          continue
        # Check if can play hearts.
        if card.suit == "hearts":
          # If the player has only hearts, playing a heart is valid.
          if all(c.suit == "hearts" for c in player.hand):
            self.hearts_broken = True
            break
          self.WarnPlayer(player, card, "Hearts not broken")
          player.AddToHand(card)
          continue
        # If card is not the queen of spades or a heart, the play is fine.
        break
    else:
      while True:
        card = player.MaybeGetPlay()
        # Must follow suit if possible. If the suit matches, the play is valid.
        if card.suit == self.cards_played[0].suit:
          break
        # If another card matches suit, cannot play this card.
        if any(c.suit == self.cards_played[0].suit for c in player.hand):
          self.WarnPlayer(player, card, "Must follow suit")
          player.AddToHand(card)
          continue
        # Cannot play queen of spades the first trick.
        if card.name == "QS" and not self.trick_num:
          self.WarnPlayer(player, card, "Cannot play queen of spades on the first trick")
          player.AddToHand(card)
          continue
        # Cannot play hearts the first trick unless hand is all hearts.
        if card.suit == "hearts" and not self.trick_num:
          if all(c.suit == "hearts" for c in player.hand):
            self.hearts_broken = True
            break
          self.WarnPlayer(player, card, "Cannot play hearts on the first trick")
          player.AddToHand(card)
          continue
        if card.suit == "hearts" and not self.hearts_broken:
          self.hearts_broken = True
        break
    return card

  def _GetTrickWinner(self):
    """Determine who won the most recent trick."""
    leader = self.cards_played[0].suit
    high_card = next(self.SortCards(c for c in self.cards_played if c.suit == leader))
    return self.cards_played.index(high_card)

  def _GetValidMoves(self, player):
    """Return a list of valid moves for the given player based on the current state."""
    # If the play leads the trick.
    if not self.cards_played:
      # If this is also the first trick, only the two of clubs may be played.
      if self.trick_num == 1:
        start = "3C" if self.num_players == 5 else "2C"
        twothree = "three of clubs" if self.num_players == 5 else "two of clubs"
        card = utils.FindCard(player.hand, name=start)
        if not card:
          raise ValueError("Logic error! Player was expected to have the {}.".format(twothree))
        return ("Must lead with {}".format(twothree), [card])
      # If hearts is broken, any play from the hand is valid.
      if self.hearts_broken:
        return (None, list(player.hand))
      # Otherwise, cannot play queen of spades, nor hearts if hand has other suits.
      other = any(c.suit != "hearts" for c in player.hand)
      return ("Hearts not broken",
              [c for c in player.hand if c.name != "QS" and (c.suit != "hearts" if other else True)])
    # Otherwise, must follow suit if possible.
    lead_suit = self.cards_played[0].suit
    follow = [c for c in player.hand if c.suit == lead_suit]
    if follow:
      return ("Must follow suit", follow)
    # If can't follow suit and this is the first trick, cannot play queen of spades, nor hearts if
    # hand has other suits.
    if self.trick_num == 1:
      other = any(c.suit != "hearts" for c in player.hand)
      return ("Cannot play queen of spades or hearts on the first trick (unless all hearts)",
              [c for c in player.hand if c.name != "QS" and (c.suit != "hearts" if other else True)])
    # At this point, any play from the hand is valid.
    return (None, list(player.hand))

  def _GetValidPlay(self, player):
    """Get a valid move from the given player."""
    card = player.GetPlay(*self._GetValidMoves(player))
    if card.suit == "hearts" and not self.hearts_broken:
      self.hearts_broken = True
    return card

  def _IsTerminal(self):
    """Return True iff the game has ended. The game ends when someone's score is >= 100."""
    return max([player.score for player in self.players]) >= 100

  def _NewRound(self):
    """Start a new round of the game."""
    self.round_num += 1
    self._state.update({
        "cards_played": [],
        "hearts_broken": False,
        "lead": None,
        "trick_num": 0,
    })
    self.ResetPlayers()
    self.deck.Shuffle()
    self._DealCards(0, (len(self.deck) // self.num_players, [1] * self.num_players))

  def _ScoreRound(self):
    """Update scores, taking shooting the moon into account."""
    scores = [0] * self.num_players
    for i, p in enumerate(self.players):
      scores[i] = sum(13 if c.name == "QS" else 1 if c.suit == "hearts" else 0 for c in p.taken)

    if 26 in scores:
      for p, score in zip(self.players, scores):
        p.score += 26 if score != 26 else 0
    else:
      for p, score in zip(self.players, scores):
        p.score += score

  def _Trade(self):
    """Trade cards between players. No trading occurs every 4th round."""
    # TODO(ding): Add support for non-4-player games.
    if self.round_num % 4 == 1:
      self._PassCards((self.players[0], self.players[1], 3),
                      (self.players[1], self.players[2], 3),
                      (self.players[2], self.players[3], 3),
                      (self.players[3], self.players[0], 3))
    elif self.round_num % 4 == 2:
      self._PassCards((self.players[0], self.players[3], 3),
                      (self.players[1], self.players[0], 3),
                      (self.players[2], self.players[1], 3),
                      (self.players[3], self.players[2], 3))
    elif self.round_num % 4 == 3:
      self._PassCards((self.players[0], self.players[2], 3),
                      (self.players[1], self.players[3], 3),
                      (self.players[2], self.players[0], 3),
                      (self.players[3], self.players[1], 3))
