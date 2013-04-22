#!/usr/bin/env python2.7
#
# Copyright 2013 Cards with Friends LLC. All Rights Reserved.

"""Implementation of the Hearts trick-taking card game."""

__author__ = "ding@caltech.edu (David Ding)"

from ..trick_taking_game import TrickTakingGame


# TODO(ding): After a standard way of referencing cards has been chosen, change
# this code accordingly.
class Hearts(TrickTakingGame):
  """The Hearts card game."""

  def __init__(self, players, deck=None):
    # Invoke superclass constructor.
    super(Hearts, self).__init__(players, deck or "standard")
    # Initialize scores.
    for player in self.players:
      player.score = 0

    # Round number
    self._round_num = 0
    # State of game each round
    self._state = {
        "cards_played": [],
        "first_player": None,
        "hearts_broken": False,
        "trick_num": 0,
    }

  def PlayGame(self):
    # Play until someone's score is >= 100
    while not self.IsTerminal():
      # Reset hands, shuffle and deal cards
      self.NewRound()
      # Pass cards left, right, across, or not at all based on the round number
      self.TradePhase()
      # Identify first player of the round
      self.state["first_player"] = self.GetFirstPlayer()
      # Play 13 tricks
      for trick_num in xrange(13):
        self.state["trick_num"] = trick_num
        self.state["cards_played"] = []
        # Have each player play a valid card for the trick
        # TODO(ding): Change loop syntax after the other classes have settled down a bit
        for i in xrange(4):
          self.state["cards_played"].append(self.get_valid_play(self.players.keys()[(first_player + i) % 4]))
        # Determine who got the trick, and give them the cards
        self.give_cards_to_trick_taker()
      # Calculate and add scores
      self.score_round()
    return [player.score for player in self.players]

  def IsTerminal():
    if max([player.score for player in self.players]) >= 100:
      return True
    return False

  def NewRound():
    for player in self.players:
      player.reset_hand()
      player.reset_taken()
    self.deck = standard_deck()
    self.round_num += 1
    self.state = {"hearts_broken": False, "trick_num": 0, "first_player": None, "cards_played": []}

    self.deck.shuffle()
    # TODO(ding): Figure out how to reference players by index here
    self.deal_cards(self.players[], [(13, [1, 1, 1, 1])])

  # TODO(ding): Discuss with mqian about adding a PassCards function to TrickTakingGame
  def TradePhase():
    if self.round_num % 4 == 1:
      PassCards([self.players[0], self.players[1], 3],
                [self.players[1], self.players[2], 3],
                [self.players[2], self.players[3], 3],
                [self.players[3], self.players[0], 3])
    elif self.round_num % 4 == 2:
      PassCards([self.players[0], self.players[3], 3],
                [self.players[1], self.players[0], 3],
                [self.players[2], self.players[1], 3],
                [self.players[3], self.players[2], 3])
    elif self.round_num % 4 == 3:
      PassCards([self.players[0], self.players[2], 3],
                [self.players[1], self.players[3], 3],
                [self.players[2], self.players[0], 3],
                [self.players[3], self.players[1], 3])
    elif self.round_num % 4 == 0:
      pass

  def GetFirstPlayer():
    # Find first player (has 2 of clubs)
    for player in self.players:
      if "2C" in player.hand:
        return player

  def get_valid_play(player):
    card = None
    # If the play is the first play of the trick
    if len(self.state["cards_played"]) == 0:
      while True:
        card = player.play()
        # Cannot play queen of spades if hearts not broken
        if card == ("QS") and not self.state["hearts_broken"]:
          invalid_warning(card, player, "Hearts not broken")
          player.hand.add(card)
          continue
        # Check if can play a heart
        elif card[-1] == "H" and not self.state["hearts_broken"]:
          # If the player has only hearts, playing a heart is valid
          for c in player.hand.elements():
            if c[-1] != "H": 
              break
          else: 
            self.state["hearts_broken"] = True
            break
          invalid_warning(card, first_player, "Hearts not broken")
          player.hand.add(card)
          continue
        # If the card selected is not the queen of spades or a heart, the play is fine
        break
    else:
      while True:
        card = player.play()
        # Must follow suit if possible
        if card[1] != self.state["cards_played"][0][1]:
          for c in player.hand.elements():
            if c[1] == self.state["cards_played"][0][1]: break
          else: 
            # Cannot play queen of spades the first trick
            if card == ("QS") and self.state["trick_num"] == 0:
              invalid_warning(card, self.players[player], "Hearts not broken")
              player.hand.add(card)
              continue
            # Cannot play heart the first trick, unless hand is all hearts
            elif card[-1] == "H" and self.state["trick_num"] == 0:
              for c in player.hand.elements():
                if c[-1] != "H": break
              else: 
                self.state["hearts_broken"] = True
                break
              invalid_warning(card, player, "Cannot play a heart on the first trick")
              player.hand.add(card)
              continue
            elif card[1] == "H" and not self.state["hearts_broken"]: self.state["hearts_broken"] = True
            break
          invalid_warning(card, self.players[player], "Must follow suit")
          player.hand.add(card)
          continue
        # If the suit matches, the play is valid
        break

    return card

  # TODO(ding): Fix this function once the syntax for cards is standardized
  def give_cards_to_trick_taker():
    trick_taker = 0
    for i in xrange(1, 4):
      if cards_played[i][1] == cards_played[trick_taker][1] and cards_played[i][0] > cards_played[trick_taker][0]: trick_taker = i
    self.taken[self.players[trick_taker]].update(cards_played)

  def score_round():
    # Update scores, taking shooting the moon into account
    curr_round_scores = {}
    for player in self.players:
      curr_round_scores[player] = 0
    for player in self.players:
      for c in player.taken:
        if c == ("QS"): curr_round_scores[p] += 13
        elif c[-1] == "H": curr_round_scores[p] += 1

    if max(curr_round_scores.values()) == 26:
      for player in self.players:
        if curr_round_scores[p] != 26:
          player.score += 26
    else:
      for player in self.players:
        player.score += curr_round_scores[p]

  @property
  def round_num(self):
    return self._round_num
        
  @property
  def state(self):
    return self._state


if __name__ == "__main__":
  pass