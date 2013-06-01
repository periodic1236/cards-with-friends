#!/usr/bin/env python2.7
#
# Copyright 2013 Cards with Friends LLC. All Rights Reserved.

"""The main game engine module."""

__author__ = "mqian@caltech.edu (Mike Qian)"

from gevent import monkey; monkey.patch_all()

import base64
import functools
import os
import socket
import sys
import uuid
import weakref

from flask import Flask, flash, redirect, render_template, request, send_file, session, url_for
from gevent import Greenlet, sleep
from gevent.event import Event
from socketio import socketio_manage
from socketio.mixins import RoomsMixin, BroadcastMixin
from socketio.namespace import BaseNamespace
from socketio.server import SocketIOServer
from werkzeug.wsgi import SharedDataMiddleware

from games import *
from player import Player
from pylib import utils
from pylib.mixins import MessageMixin


GAMES = {
    "Hearts": Hearts,
    "HighestCard": HighestCard,
    "Spades": Spades,
}
PORT = 8080


##################################################
##### FLASK ROUTES AND BASIC SETUP
##################################################

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.debug = True

def login_required(f):
  @functools.wraps(f)
  def wrapper(*args, **kwargs):
    if "nickname" not in session:
      flash("You are not logged in.")
      return redirect(url_for("login"))
    return f(*args, **kwargs)
  return wrapper

@app.route("/")
def index():
  return render_template("index.html")

@app.route("/about_making_games")
def documentation():
  #TODO write documentation page
  return render_template("documentation.html")

@app.route("/game_table")
@login_required
def game_table():
  return render_template("game_table.html")

@app.route("/login", methods=["GET", "POST"])
def login():
  """Procedure to handle the login page."""
  if request.method == "POST":
    nickname = request.form["nick"]
    if HandleLogin(nickname):
      session["nickname"] = nickname
      password = base64.urlsafe_b64encode(os.urandom(64))
      session["password"] = password
      SetPassword(nickname, password)
      return redirect(url_for("room_list"))
    else:
      flash("Nickname is already taken. Pick another one.")
      return render_template("login.html")
  return render_template("login.html")

@app.route("/room_list", methods=["GET", "POST"])
@login_required
def room_list():
  return render_template("room_list.html")

# this runs as soon as a client is started
@app.route("/socket.io/<path:path>")
def run_socketio(path):
  # second argument maps urls to namespace classes
  socketio_manage(request.environ, {"": CardNamespace}, request)
  return "out"


##################################################
##### SERVER HANDLERS
##################################################

def HandleLogin(nickname):
  if nickname in CardNamespace.players:
    return False
  CardNamespace.players[nickname] = None
  return True

def SetPassword(nickname, password):
  CardNamespace.passwords[nickname] = password

def AddToTrickArea(player, cards):
  # cards is a list of Card objects
  player_socket = CardNamespace.players[player]
  for card in cards:
    player_socket.add_to_trick_area(card.id, card.image_loc)

def EndGame(results):
  # TODO(brazon)
  # results is a list of tuples (nickname, score)
  pass

def GetBidFromPlayer(player, valid_bids):
  player_socket = CardNamespace.players[player]
  player_socket.bid = None
  player_socket.start_turn(player)
  print "here are the valid bids for player %s:" % player, valid_bids
  player_socket.get_bid(valid_bids)
  while player_socket.bid is None:
    print "waiting for player %s" % player
    sleep(1)
  player_socket.end_turn()

  return player_socket.bid

def GetCardFromPlayer(player, valid_plays, num_cards=1):
  player_socket = CardNamespace.players[player]
  player_socket.card = None
  plays = []
  valid_plays_map = dict(((x.id, x) for x in valid_plays))
  valid_plays_list = valid_plays_map.keys()
  print "here are the valid plays for player %s:" % player, valid_plays_map.values()
  player_socket.start_turn()
  while num_cards > 0:
    player_socket.get_card(valid_plays_list)
    while player_socket.card is None:
      print "waiting for player %s" % player
      sleep(1)
    valid_plays_list.remove(player_socket.card)
    plays += [player_socket.card]
    player_socket.card = None
    num_cards -= 1
  player_socket.end_turn()
  return [valid_plays_map[i] for i in plays]

def PlayerAddToHand(player, cards):
  # cards is a list of Card objects
  player_socket = CardNamespace.players[player]
  for card in cards:
    print "Adding card: (%s, %s)" % (player, card)
    player_socket.add_card(card.id, card.image_loc)

def PlayerClearHand(player):
  player_socket = CardNamespace.players[player]
  player_socket.clear_hand()

def PlayerClearTaken(player):
  player_socket = CardNamespace.players[player]
  player_socket.clear_taken()

def PlayerDisplayMessage(player, message):
  player_socket = CardNamespace.players[player]
  player_socket.display_message(message)

def PlayerRemoveFromHand(player, cards):
  # cards is a list of Card objects
  player_socket = CardNamespace.players[player]
  for card in cards:
    print "Removing card: (%s, %s)" % (player, card)
    player_socket.remove_card(card.id)

def PlayerTakeTrick(player, cards):
  # cards is a list of Card objects
  # Note that cards is not used...
  player_socket = CardNamespace.players[player]
  player_socket.take_trick()

def PlayerUpdateMoney(player, money):
  player_socket = CardNamespace.players[player]
  player_socket.update_money(money)

def PlayerUpdateScore(player, score):
  player_socket = CardNamespace.players[player]
  player_socket.update_score(score)


##################################################
##### CLASSES
##################################################


class GameManager(MessageMixin):
  """Manages games and scores."""

  games = {}
  players = {}
  in_room = weakref.WeakValueDictionary()

  def CreateGame(self, game_type, players):
    """Create a new game."""
    if game_type not in GAMES:
      raise ValueError("Game '{}' not found or not supported".format(game))

    objs = [Player(name) for name in players]
    game = GAMES[game_type](objs)

    self.games[game.id] = game
    self.players.update((p.id, p) for p in objs)
    self.in_room.update((p.id, game) for p in objs)
    return (game.id, objs)

  def DeleteGame(self, game_id):
    """Delete a previously-created game."""
    if game_id not in self.games:
      return KeyError("Invalid game ID: {}".format(game_id))
    del self.games[game.id]

  def StartGame(self, game_id):
    """Start a previously-created game."""
    if game_id not in self.games:
      return KeyError("Invalid game ID: {}".format(game_id))
    game = self.games[game_id]
    results = game.PlayGame()
    self.Notify("game_ended", results=results)
    # TODO(mqian): How do we deal with the number of winners?

  def _RecordScore(self, *args, **kwargs):
    raise NotImplementedError

  def _WriteHistory(self, *args, **kwargs):
    raise NotImplementedError


# The socket.io namespace
# always extend BaseNamespace; also add mixins if you want
# a new object of this type is created for each client
class CardNamespace(BaseNamespace, RoomsMixin, BroadcastMixin):

  # state
  manager = GameManager()
  rooms = []  # (static) list of rooms (instances of Room), keys are game names
  players = {}  # (static) dict of players (instances of CardNamespace), keys are nicknames
  passwords = {}

  my_room = None  # room that this player has joined
  isHost = 0  # 0 or 1 indicating whether this player is the host of my_room
  nickname = ""
  ready = False

  # runs when client refreshes the page, keeps sockets up to date
  def on_reconnect(self, nickname, password):
    # add myself to list of players
    if CardNamespace.passwords[nickname] == password:
      if CardNamespace.players[nickname] != None:
        self.my_room = CardNamespace.players[nickname].my_room
        self.isHost = CardNamespace.players[nickname].isHost
        self.ready = CardNamespace.players[nickname].ready

      self.nickname = nickname
      CardNamespace.players[nickname] = self
    else:
      raise RuntimeError('Incorrect Password')

  # runs when client plays a card
  def on_card(self, card):
    self.card = card

  # runs when client plays a bid
  def on_bid(self, bid):
    self.bid = bid

  # add card to hand
  def add_card(self, card, image):
    self.emit("add_to_hand", card, image)

  def get_card(self, cards_allowed):
    self.emit("get_card", cards_allowed)

  def get_bid(self, bids_allowed):
    self.emit("get_bid", bids_allowed)

  def clear_hand(self):
    self.emit("clear_hand")

  def remove_card(self, card):
    self.emit("remove_from_hand", card)

  def add_to_trick_area(self, nickname, card):
    for p in self.my_room.players:
      player = CardNamespace.players[p]
      player.emit("add_to_trick_area", nickname, card)

  def update_money(self, money):
    for p in self.my_room.players:
      player = CardNamespace.players[p]
      player.emit("update_money", self.nickname, money)

  def update_score(self, score):
    for p in self.my_room.players:
      player = CardNamespace.players[p]
      player.emit("update_score", self.nickname, score)

  def take_trick(self):
    for p in self.my_room.players:
      player = CardNamespace.players[p]
      player.emit("clear_trick_area")
      player.emit("increment_tricks_won", self.nickname)

  def clear_taken(self):
    for p in self.my_room.players:
      player = CardNamespace.players[p]
      player.emit("reset_tricks_won", self.nickname)

  def start_turn(self):
    for p in self.my_room.players:
      player = CardNamespace.players[p]
      player.emit("start_turn", self.nickname)

  def end_turn(self):
    for p in self.my_room.players:
      player = CardNamespace.players[p]
      player.emit("end_turn", self.nickname)

  def display_message(self, message):
    self.emit("display_message", message)

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
    host_list = [room.host for room in CardNamespace.rooms]
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
      capacity = 3
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
      # go to game table game
      print "Game Starting!!"
      self.my_room.StartGame()

  def on_ready_game(self):
    if self.my_room is None:
      print "You have no game to start!"
    else:
      # tell game you are ready
      print self.nickname, "is ready to start"
      for p in self.my_room.players:
        self.emit("register_player", p)
      self.ready = True


# Room class
class Room(object):

  def __init__(self, host, capacity):
    self.id = uuid.uuid4()
    self.host = host.nickname
    self.players = [self.host]
    self.capacity = list(utils.Flatten([capacity]))
    self.game = None

  # delete this room and remove all players
  def __del__(self):
    for p in self.players:
      CardNamespace.players[p].my_room = None

  @property
  def full(self):
    return self.num_players in self.capacity

  @property
  def num_players(self):
    return len(self.players)

  def AddPlayer(self, p):
    if p.nickname in self.players:
      print "Cannot add the same player to a room twice!"
    elif self.full:
      print "Cannot add player because room is full!"
    else:
      self.players.append(p.nickname)
      p.my_room = self

  def RemovePlayer(self, p):
    if not p.nickname in self.players:
      print "Cannot remove player because player is not in room!"
    else:
      self.players.remove(p.nickname)
      p.my_room = None

  def StartGame(self):
    #print "Game 1"
    self.game = Hearts([Player(p) for p in self.players])
    print "Game 2"
    for p in self.players:
      CardNamespace.players[p].emit('go_to_game_table')
    while False in [CardNamespace.players[p].ready for p in self.players]:
      print "Game 3", [CardNamespace.players[p].ready for p in self.players]
      sleep(0.5)
    Greenlet.spawn(self.game.PlayGame)
    #g = Greenlet(self.game.PlayGame)
    #g.start_later(1)
    #g.join()


def Register():
    # Notification handlers.
  notify = {
      "add_card": PlayerAddToHand,
      "clear_hand": PlayerClearHand,
      "clear_taken": PlayerClearTaken,
      "display_message": PlayerDisplayMessage,
      "game_ended": EndGame,
      "played_card": AddToTrickArea,
      "remove_card": PlayerRemoveFromHand,
      "take_trick": PlayerTakeTrick,
      "update_money": PlayerUpdateMoney,
      "update_score": PlayerUpdateScore,
  }
  # Request handlers.
  request = {
      "get_bid": GetBidFromPlayer,
      "get_play": GetCardFromPlayer,
  }
  MessageMixin.RegisterHandler("notify", **notify)
  MessageMixin.RegisterHandler("request", **request)


def main(*args):
  Register()
  global app
  app = SharedDataMiddleware(app, {
      "/": os.path.join(os.path.dirname(__file__), "static")
  })
  server = SocketIOServer(("0.0.0.0", PORT), app, resource="socket.io", policy_server=False)
  print >>sys.stderr, "Starting server at http://{}:{}".format(socket.gethostname(), PORT)
  server.serve_forever()


if __name__ == "__main__":
  if len(sys.argv) != 1:
    print >>sys.stderr, "usage: {}".format(os.path.basename(sys.argv[0]))
    sys.exit(1)
  main(*sys.argv[1:])
