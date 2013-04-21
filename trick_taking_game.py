#!/usr/bin/env python
#
# Copyright 2013 Cards with Friends LLC. All Rights Reserved.

"""Abstract class for trick-taking card games."""

__author__ = "mqian@caltech.edu (Mike Qian)"

import collections

import game


class Hand(object):
    """A player's hand."""

    def __init__(self, player):
        """Constructor.

        Args:
            player: The name of the player to which this hand belongs.
        """
        self.player = player
        self.cards = collections.Counter()

    def add_card(self, card):
        """Add a card to the player's hand."""
        self.cards[card] += 1

    def has_card(self, card):
        """Check if the player's hand has the given card."""
        return bool(self.cards[card])

    def remove_card(self, card):
        """Remove a given card from the player's hand."""
        if self.HasCard(card):
            self.cards[card] -= 1
            return card
        else:
            # Raise an error.
            raise KeyError


class TrickTakingGame(game.Game):
    """A trick-taking game."""

    def __init__(self, deck, players):
        """Constructor.

        Args:
            ...
        """
        super(TrickTakingGame, self).__init__(deck, players)
        self.num_players = len(self.players)
        self.hands = {}
        self.scores = {}
        for player in self.players:
            self.hands[player] = Hand(player)
        for player in self.players:
            self.scores[player] = 0

    def evaluate_trick(self, ...):
        raise NotImplementedError("This class should be implemented by users.")

    def play_game(self):
        # while not self.TerminateGame():
        #     self.NewRound()
        #     self.PlayRound(...)
        raise NotImplementedError("This class should be implemented by users.")

    def terminate_game(self):
        raise NotImplementedError("This class should be implemented by users.")

    def deal_cards(self, first_deal, patterns):
        """Deal cards to players.

        Args:
            first_deal: The identifier of the first player to deal to.
            patterns: A list of tuples of the form (# phases, deal pattern).
        Usage:
            self.DealCards("alpha", [(13, [1, 1, 1, 1])])
        """
        if first_deal not in self.players:
            # Raise an error.
            raise ValueError
        if self.deck.num_cards < sum(i * sum(j) for i, j in patterns):
            # Raise an error.
            raise ValueError
        self.deck.shuffle()
        for num_phases, pattern in patterns:
            deal_idx = self.players.index(first_deal)
            for _ in xrange(num_phases):
                for num_cards in pattern:
                    hand = self.hands[self.players[deal_idx]]
                    for _ in xrange(num_cards):
                        hand.add_card(self.deck.get_next_card())
                    deal_idx = (deal_idx + 1) % self.num_players


if __name__ == "__main__":
    pass