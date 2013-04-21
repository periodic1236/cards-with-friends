#!/usr/bin/env python
#
# Copyright 2013 Cards with Friends LLC. All Rights Reserved.

"""Abstract class for card games."""

__author__ = "ding@caltech.edu (David Ding)"


class Game(object):
    """A card game."""

    def __init__(self, deck, players):
        """Constructor.

        Args:
            deck: The name of the deck for this game.
            players: A sequence containing generic player names.
        """
        self.deck = deck
        self.players = players


if __name__ == "__main__":
    pass