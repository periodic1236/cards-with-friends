import deck

if __name__ == "__main__":
  d = deck.Deck('decks/test.json')
  assert(d.name == 'test')
  assert(d.long_name == 'Small Test Deck')
  d.GetBackImage().show()
  initial_cards_list = d._cards_list[:]
  print [i.short_name for i in initial_cards_list]
  d.Shuffle()
  new_cards_list = d._cards_list[:]
  print [i.short_name for i in new_cards_list]

