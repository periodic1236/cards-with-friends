#!/usr/bin/env python
#
# Copyright 2013 Cards with Friends LLC. All Rights Reserved.

"""Implementation of a player in a game."""

__author__ = "ding@caltech.edu (David Ding)"

import collections


def Player(object):
    """A player in a game."""

    def __init__(self, name):
        self._name = name
        self._hand = Hand()
        self._score = None
        self._money = None
        self._cards_taken = collections.Counter()

    def make_bet(self):
        # TODO(brazon): Interact with front-end to get bet.
        bet = None
        return bet

    def play_card(self):
        # TODO(brazon): Interact with front-end to get card.
        card = None
        return card

    def take_card(self, card):
        self._cards_taken[card] += 1


class Hand(object):
    """A player's hand."""

    def __init__(self):
        self._cards = collections.Counter()

    def add_card(self, card):
        """Add a card to the player's hand."""
        self._cards[card] += 1

    def has_card(self, card):
        """Check if the player's hand has the given card."""
        return bool(self._cards[card])

    def remove_card(self, card):
        """Remove a given card from the player's hand."""
        if not self.has_card(card):
            # Raise an error.
            raise KeyError
        self._cards[card] -= 1
        return card


if __name__ == "__main__":
    pass