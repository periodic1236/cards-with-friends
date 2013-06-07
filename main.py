#!/usr/bin/env python2.7
#
# Copyright 2013 Cards with Friends LLC. All Rights Reserved.

"""The main game engine module."""

__author__ = "mqian@caltech.edu (Mike Qian)"

from gevent import Greenlet, monkey, sleep; monkey.patch_all()

import base64
import functools
import os
import socket
import sys
import uuid
import weakref

from flask import Flask, flash, redirect, render_template, request, send_file, session, url_for
from socketio import socketio_manage
from socketio.mixins import RoomsMixin, BroadcastMixin
from socketio.namespace import BaseNamespace
from socketio.server import SocketIOServer
from werkzeug import secure_filename
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
try:
  PORT = int(os.getenv("PORT"))
except (TypeError, ValueError):
  PORT = 5000
UPLOAD_FOLDER = "uploads"


##################################################
##### FLASK ROUTES AND BASIC SETUP
##################################################

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.debug = False

def allowed_file(filename):
  return '.' in filename and filename.rsplit('.', 1)[1] == 'py'

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

@app.route("/code_submission", methods=['GET', 'POST'])
def code_submission():
  if request.method == 'POST':
    file = request.files['file']
    if file and allowed_file(file.filename):
      filename = secure_filename(file.filename)
      file.save(os.path.join(UPLOAD_FOLDER, filename))
      f = open(os.path.join(UPLOAD_FOLDER, filename + '.submit'), 'w+')
      f.write('email: ' + request.form['email'] + '\n')
      f.write('author: ' + request.form['author'] + '\n')
      f.write('Game name: ' + request.form['game_name'] + '\n')
      return redirect(url_for('uploaded_file', filename=filename))
  return render_template("submit_code.html")

@app.route("/uploaded_file/<filename>")
def uploaded_file(filename):
  return render_template("uploaded_file.html", filename=filename)

@app.route("/about_making_games")
def documentation():
  return render_template("doc/html/index.html")

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
  # results is a list of tuples (nickname, score)
  winning_score = results[0][1]
  for i in results:
    player_socket = CardNamespace.players[i[0]]
    player_socket.display_message('The game is over.')
    if i[1] == winning_score:
      player_socket.display_message('You won.')
    else:
      player_socket.display_message('You lost.')
    player_socket.display_message('The final scores were: ' + str(results))

def GetBidFromPlayer(message, player, valid_bids):
  player_socket = CardNamespace.players[player]
  player_socket.bid = None
  player_socket.start_turn(player)
  print "here are the valid bids for player %s:" % player, valid_bids
  player_socket.display_message(message)
  player_socket.get_bid(valid_bids)
  while player_socket.bid is None:
    print "waiting for player %s" % player
    sleep(1)
  player_socket.end_turn()

  return player_socket.bid

def GetCardFromPlayer(message, player, valid_cards, num_cards=1):
  player_socket = CardNamespace.players[player]
  player_socket.card = None
  plays = []
  valid_cards_map = dict(((x.id, x) for x in valid_cards))
  valid_cards_list = valid_cards_map.keys()
  print "here are the valid plays for player %s:" % player, valid_cards_map.values()
  player_socket.start_turn()
  while num_cards > 0:
    player_socket.get_card(message, valid_cards_list)
    while player_socket.card is None:
      print "waiting for player %s" % player
      sleep(1)
    valid_cards_list.remove(player_socket.card)
    plays += [player_socket.card]
    player_socket.card = None
    num_cards -= 1
  player_socket.end_turn()
  return [valid_cards_map[i] for i in plays]

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

  def get_card(self, message, cards_allowed):
    self.emit("get_card", message, cards_allowed)

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
    game_list = [room.game_name for room in CardNamespace.rooms];
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
          print "Something is wrong with", player.nickname, player.my_room.id
      player.emit("update_room_list", game_list, host_list, players_list, capacity_list, room_index, player.isHost)

  # create a room
  def on_create_room(self, game_name, num_players):
    if self.my_room is None:
      self.my_room = Room(self, game_name, int(num_players))
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
      for p in self.my_room.players:
        CardNamespace.players[p].my_room = None
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

  def __init__(self, host, game_name, capacity):
    self.id = uuid.uuid4()
    self.host = host.nickname
    self.game_name = game_name
    self.players = [self.host]
    self.capacity = capacity
    self.game = None

  @property
  def full(self):
    return self.num_players == self.capacity

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
    # TODO: start correct type of game (self.game_name)
    # with correct number of players (self.capacity)
    self.game = Hearts([Player(p) for p in self.players])
    for p in self.players:
      CardNamespace.players[p].emit('go_to_game_table')
    while False in [CardNamespace.players[p].ready for p in self.players]:
      print [CardNamespace.players[p].ready for p in self.players]
      sleep(0.05)
    g = Greenlet(self.game.PlayGame)
    g.start()
    g.join()


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
      "get_card": GetCardFromPlayer,
  }
  MessageMixin.RegisterHandler("notify", **notify)
  MessageMixin.RegisterHandler("request", **request)


Register()
app = SharedDataMiddleware(app, {
    "/": os.path.join(os.path.dirname(__file__), "static")
})


if __name__ == "__main__":
  if len(sys.argv) != 1:
    print >>sys.stderr, "usage: {}".format(os.path.basename(sys.argv[0]))
    sys.exit(1)
  print >>sys.stderr, "Starting server at http://{}:{}".format(socket.gethostname(), PORT)
  server = SocketIOServer(("0.0.0.0", PORT), app, resource="socket.io", policy_server=False)
  server.serve_forever()
