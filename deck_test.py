#!/usr/bin/env python2.7
#
# Copyright 2013 Cards with Friends LLC. All Rights Reserved.

"""Tests for deck."""

__author__ = "razon.ben@gmail.com (Ben Razon)"

from deck import Deck


if __name__ == "__main__":
  d = Deck.fromjson("decks/standard.json")
  assert(d.name == "standard")
  assert(d.long_name == "Standard 52-Card Deck")
  # d.GetBackImage().show()
  cards = list(d)
  assert(len(cards) == 52)
  print cards