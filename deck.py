from card import Card
from PIL import Image
import json
import os
import random

class Deck:
  def __init__(self, name, long_name, labels, cards, back_image_loc):
    """
    labels is a list of properties all the cards have. cards is a list where
    each element is of the form [short_name, long_name, image_loc, values].
    """
    self._name = name
    self._long_name = long_name
    self._num_cards = len(cards)
    self._back_image_loc = back_image_loc
    self._cards_list = [None] * self._num_cards
    for i in range(self._num_cards):
      card = cards[i]
      self._cards_list[i] = Card(card[0], card[1], card[2], labels, card[3])

  def __init__(self, filename):
    """
    Creates a deck from a json file. The file format is explained
    elsewhere.
    """
#TODO(BEN) add reference to documentation
    f = open(filename, 'r')
    json_deck = json.load(f)
    self._name = json_deck['name']
    self._long_name = json_deck['long_name']
    labels = [i['name'] for i in json_deck['labels']]
    cards = json_deck['cards']
    self._num_cards = len(cards)
    self._back_image_loc = json_deck['back_image_loc']
    self._cards_list = [None] * self._num_cards
    for i in range(self._num_cards):
      card = cards[i]
      values = [card[j] for j in labels]
      name = card['name']
      long_name = card['long_name']
      image_loc = card['image_loc']
      self._cards_list[i] = Card(name, long_name, image_loc, labels, values)

  def WriteToFile(self, filename, indent=2):
    if os.path.exists(filename):
      raise IOError('You don\'t have permission to overwrite files.')
    f = open(filename, 'w+')
    #TODO(Ben): figure out how to recreate json
    raise NotImplementedError('TODO(Ben)')
    f.flush()
    f.close()

  def GetNumCards(self):
    return self._num_cards
  num_cards = property(GetNumCards)

  def GetBackImageLoc(self):
    return 'card-images/' + self._back_image_loc
  back_image_loc = property(GetBackImageLoc)

  def GetName(self):
    return self._name
  name = property(GetName)

  def GetLongName(self):
    return self._long_name
  long_name = property(GetLongName)

  def GetBackImage(self):
    return Image.open('card-images/' + self._back_image_loc)

  def Shuffle(self):
    random.shuffle(self._cards_list)

  def GetNextCard(self, num_cards=0):
    """
    Returns the top card of the deck and removes it. This also updates
    num_cards.
    """
    if self._num_cards > 0:
      self._num_cards -= 1
      return self._cards_list.pop(0)
    else:
      raise IndexError("Tried to get card from empty deck.")

