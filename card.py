from PIL import Image

class Card:
  def __init__(self, short_name, long_name, image_loc, labels, values):
    self._short_name = short_name
    self._long_name = long_name
    self._image_loc = image_loc
    self._properties = dict(zip(labels,values))

  def getShortName(self):
    return self._short_name
  short_name = property(getShortName)

  def getLongName(self):
    return self._long_name
  long_name = property(getLongName)

  def getImageLoc(self):
    return self._image_loc
  image_loc = property(getImageLoc)

  def getProperties(self):
    return self._properties
  properties = property(getProperties)

  def getImage(self):
    return Image.open(self._image_loc)
