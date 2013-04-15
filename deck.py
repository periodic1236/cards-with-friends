from card import Card
from PIL import Image
import random

class Deck:
  def __init__(self, labels, cards, back_image_loc):
    self._num_cards = len(cards)
    self._back_image_loc = back_image_loc
    self._cards_list = [None] * self._num_cards
    for i in range(self._num_cards):
      card = cards[i]
      self._cards_list[i] = Card(card[0], card[1], card[2], labels, card[4])

  def __init__(self, filename):
#TODO(Ben) create deck of cards from file
    self._num_cards = -1
    self._cards_list = None

  def getNumCards(self):
    return self._num_cards
  num_cards = property(getNumCards)

  def getBackImageLoc(self):
    return self._back_image_loc
  back_image_loc = property(getBackImageLoc)

  def getBackImage(self):
    return Image.open(self._back_image_loc)

  def shuffle(self):
    random.shuffle(self._cards_list)

  def deal(self):
#TODO(Ben) figure out how hands are being implemented to do this
    pass

