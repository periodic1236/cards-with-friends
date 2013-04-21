#!/usr/bin/env python
#
# Copyright 2013 Cards with Friends LLC. All Rights Reserved.

"""Tests for deck."""

__author__ = "razon.ben@gmail.com (Ben Razon)"

from deck import Deck


if __name__ == "__main__":
  d = Deck.fromjson("decks/test.json")
  assert(d.name == "test")
  assert(d.long_name == "Small Test Deck")
  d.get_back_image().show()
  initial_cards_list = d._cards_list[:]
  print [i.short_name for i in initial_cards_list]
  d.shuffle()
  new_cards_list = d._cards_list[:]
  print [i.short_name for i in new_cards_list]