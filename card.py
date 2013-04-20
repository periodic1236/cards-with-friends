from PIL import Image

class Card:
  def __init__(self, short_name, long_name, image_loc, labels, values):
    self._short_name = short_name
    self._long_name = long_name
    self._image_loc = image_loc
    self._properties = dict(zip(labels,values))

  def GetShortName(self):
    return self._short_name
  short_name = property(GetShortName)

  def GetLongName(self):
    return self._long_name
  long_name = property(GetLongName)

  def GetImageLoc(self):
    return 'card-images/' + self._image_loc
  image_loc = property(GetImageLoc)

  def GetProperties(self):
    return self._properties
  properties = property(GetProperties)

  def GetImage(self):
    return Image.open('card-images/' + self._image_loc)
