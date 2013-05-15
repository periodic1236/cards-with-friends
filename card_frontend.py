from gevent import sleep, monkey; monkey.patch_all()

from socketio import socketio_manage
from socketio.namespace import BaseNamespace
from socketio.mixins import RoomsMixin, BroadcastMixin
from flask import session
#TODO Figure out circular imports

def HandleLogin(nickname):
  if nickname in CardNamespace.players:
    return False
  else:
    CardNamespace.players[nickname] = None
    return True

def SetPassword(nickname, password):
  CardNamespace.passwords[nickname] = password

def GetBidFromPlayer(player, valid_bids):
  # TODO(brazon): Figure out frontend first
  return None

def GetCardFromPlayer(player, valid_plays, num_cards=1):
  # TODO(brazon): num_cards not being 1 probably breaks lots of stuff
  if num_cards != 1:
    raise NotImplementedError('Multiple card plays are not supported yet.')
  player_socket = CardNamespace.players[player]
  player_socket.card = None
  valid_plays_list = [x.id for x in valid_plays]
  player_socket.get_card(valid_plays)
  while player_socket.card is None:
    sleep(1)
  return [player_socket.card]

def PlayerAddToHand(player, cards):
  # cards is a list of Card objects
  player_socket = CardNamespace.players[player]
  for card in cards:
    player_socket.add_card(card.id, card.image_loc)
  pass

def PlayerClearHand(player):
  player_socket = CardNamespace.players[player]
  player_socket.clear_hand()
  pass

def PlayerClearTaken(player):
  # TODO(theresa) Add trick count field to frontend
  player_socket = CardNamespace.players[player]
  player_socket.clear_taken()
  pass

def PlayerDisplayMessage(player, message):
  # TODO(brazon) Figure out frontend
  pass

def PlayerRemoveFromHand(player, cards):
  # cards is a list of Card objects
  player_socket = CardNamespace.players[player]
  for card in cards:
    player_socket.remove_card(card.id)
  pass

def PlayerTakeTrick(player, cards):
  # cards is a list of Card objects
  # Note that cards is not used...
  player_socket = CardNamespace.players[player]
  player_socket.take_trick()
  pass

def PlayerUpdateMoney(player, money):
  # TODO(brazon) Figure out frontend first
  pass

def PlayerUpdateScore(player, score):
  # TODO(brazon) figure out frontend first
  pass

# The socket.io namespace
# always extend BaseNamespace; also add mixins if you want
# a new object of this type is created for each client
class CardNamespace(BaseNamespace, RoomsMixin, BroadcastMixin):

  # state
  rooms = []  # (static) list of rooms (instances of Room), keys are game names
  players = {}  # (static) dict of players (instances of CardNamespace), keys are nicknames
  passwords = {}

  my_room = None  # room that this player has joined
  isHost = 0  # 0 or 1 indicating whether this player is the host of my_room
  nickname = ""

  # runs when client refreshes the page, keeps sockets up to date
  def on_reconnect(self, nickname, password):
    # add myself to list of players
    if CardNamespace.passwords[nickname] == password:
      CardNamespace.players[nickname] = self
    else:
      raise RuntimeError('Incorrect Password')

    # this only needs to happen once but since on_login is not used anymore I decided to put it here
    self.nickname = nickname

  # runs when client plays a card
  def on_card(self, card):
    self.card = card

  # add card to hand
  def add_card(self, card, image):
    self.emit("add_to_hand", card, image)

  # start my turn
  def get_card(self, cards_allowed):
    self.emit("get_card", cards_allowed)

  def clear_hand(self):
    self.emit("clear_hand")

  def remove_card(self, card):
    self.emit("remove_from_hand", card)

  def take_trick(self):
    for player in self.my_room.players:
      player.emit("clear_trick_area")
      player.emit("increment_tricks_won", self.nickname)

  def clear_taken(self):
    for player in self.my_room.players:
      player.emit("reset_tricks_won", self.nickname)
  # -- Events for room list --

  # client requested room list
  def on_request_room_list(self):
    self.update_room_list()

  # update room list (for this client only)
  def update_room_list(self):
    # For now just update everyone's lists
    CardNamespace.update_all_room_lists()

  # update all room lists (for everyone viewing the room list)
  @staticmethod
  def update_all_room_lists():
    # Compile room list data
    host_list = [room.host.nickname for room in CardNamespace.rooms]
    players_list = [room.num_players for room in CardNamespace.rooms]
    capacity_list = [room.capacity for room in CardNamespace.rooms]
    # TODO: only send to players who are viewing list? (as opposed to playing game)
    for player in CardNamespace.players.itervalues():
      room_index = -1
      if player.my_room != None:
        if player.my_room in CardNamespace.rooms:
          room_index = CardNamespace.rooms.index(player.my_room)
        else:
          print "Something is wrong!"
      player.emit("update_room_list", host_list, players_list, capacity_list, room_index, player.isHost)

  # create a room
  def on_create_room(self):
    if self.my_room is None:
      capacity = 4
      self.my_room = Room(self, capacity)
      self.isHost = 1;
      CardNamespace.rooms.append(self.my_room)
      CardNamespace.update_all_room_lists()
    else:
      print "Cannot create a room if you are currently in one!"

  # join a room
  # hostname is the nickname of the host of the game you want to join
  def on_join(self, hostname):
    host = CardNamespace.players[hostname]
    room = host.my_room
    if room != None and host.isHost == 1:
      if not room.full:
        # joined room successfully
        room.AddPlayer(self)
        CardNamespace.update_all_room_lists()
      else:
        print "Room is full!"
    else:
      print "Something is wrong!"

  # Leave a room
  # leave whichever room you are currently in
  def on_leave(self):
    if self.my_room is None:
      print "Cannot leave a room if you are not in one!"
    else:
      # left room successfully
      self.my_room.RemovePlayer(self)
      CardNamespace.update_all_room_lists()

  # Delete a room
  # delete whichever room you are hosting
  def on_delete_room(self):
    if (not self.isHost) or self.my_room is None:
      print "You have no room to delete!"
    else:
      # deleted room successfully
      self.isHost = 0
      CardNamespace.rooms.remove(self.my_room)
      del self.my_room
      self.my_room = None
      CardNamespace.update_all_room_lists()

  # Start game
  # called by host of game once enough players have joined
  def on_start_game(self):
    if not self.isHost:
      print "You are not a host!"
    elif self.my_room is None:
      print "You have no game to start!"
    else:
      # start game
      print "Game starting!!"
      self.my_room.StartGame();


# Room class
class Room(object):

  def __init__(self, host, capacity):
    self.host = host  # list of players (CardNamespace objects) currently joined
    self.players = [host]
    self.capacity = capacity  # total number of players
    self.game = None;

  # delete this room and remove all players
  def __del__(self):
    for p in self.players:
      p.my_room = None

  @property
  def num_players(self):
    return len(self.players)

  @property
  def full(self):
    return self.num_players >= self.capacity

  def AddPlayer(self, p):
    if p in self.players:
      print "Cannot add the same player to a room twice!"
    elif self.full:
      print "Cannot add player because room is full!"
    else:
      self.players.append(p)
      p.my_room = self

  def RemovePlayer(self, p):
    if not p in self.players:
      print "Cannot remove player because player is not in room!"
    else:
      self.players.remove(p)
      p.my_room = None

  def StartGame(self):
    from games.spades import Spades
    self.game = Spades([p.nickname for p in self.players])
    for p in self.players:
        p.emit('go_to_game_table')
