from gevent import sleep, monkey; monkey.patch_all()

from socketio import socketio_manage
from socketio.namespace import BaseNamespace
from socketio.mixins import RoomsMixin, BroadcastMixin
import games.highest_card

def GetCardFromPlayer(player, valid_plays, cards, num_cards=1):
  #TODO num_cards not being 1 probably breaks lots of stuff
  player_socket = CardNamespace.players[player]
  player_socket.cardPlayed = None
  player_socket.get_card(valid_plays)
  while(player_socket.cardPlayed == None):
    sleep(1)
  cards.append(player_socket.cardPlayed)

def HandleLogin(nickname):
  if nickname in CardNamespace.players:
    return False
  else:
    CardNamespace.players[nickname] = None
    return True

# The socket.io namespace
# always extend BaseNamespace; also add mixins if you want
# a new object of this type is created for each client
class CardNamespace(BaseNamespace, RoomsMixin, BroadcastMixin):

    # state
    rooms = []  # (static) list of rooms (instances of Room), keys are game names
    players = {}  # (static) dict of players (instances of CardNamespace), keys are nicknames

    my_room = None  # room that this player has joined
    isHost = 0  # 0 or 1 indicating whether this player is the host of my_room
    nickname = ''

    # runs when client enters nickname to log in
    # this is no longer called!!!
    def on_login(self, nickname):

        print 'LOGIN!!'
        
        self.nickname = nickname
        print 'nickname: ', self.nickname

        #self.player_num = CardNamespace.num_players
        #CardNamespace.num_players += 1

        # Empty hand
        #self.hand = []

        # Make sure there aren't too many players
        #if self.player_num > CardNamespace.total_players:
        #    raise Exception('Too many players!')

        # add myself to list of players
        # TODO This seems really insecure...
        CardNamespace.players[nickname] = self

        # send message to my client (only) with player num
        #self.emit('player_num', self.player_num)

        # Just have them join a default-named room
        #self.join('main_room')

        # if all players have joined, start game
        #if CardNamespace.num_players == CardNamespace.total_players:
        #  game = games.highest_card.HighestCard(CardNamespace.players.keys())
        #  game.PlayGame()

    # runs when client refreshes the page, keeps sockets up to date
    def on_reconnect(self, nickname):
        # add myself to list of players
        # TODO This seems really insecure...
        # if session['nickname'] == nickname: (this gives error: 'session' not defined)
        CardNamespace.players[nickname] = self

        # this only needs to happen once but since on_login is not used anymore I decided to put it here
        self.nickname = nickname

    # runs when client plays a card
    def on_card_played(self, card):
        self.hand.remove(card)
        self.cardPlayed = card

    # add card to hand
    def add_card(self, card):
        self.hand.append(card)
        self.emit('add_to_hand', self.player_num, card)

    # start my turn
    def get_card(self, cards_allowed):
        #TODO Figure out how to pass card objects to frontend
        self.emit('get_card', self.player_num, cards_allowed)

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
        players_list = [room.players_joined() for room in CardNamespace.rooms]
        capacity_list = [room.capacity for room in CardNamespace.rooms]
        # TODO: only send to players who are viewing list? (as opposed to playing game)
        for player in CardNamespace.players.itervalues():
            room_index = -1
            if player.my_room != None:
                if player.my_room in CardNamespace.rooms:
                    room_index = CardNamespace.rooms.index(player.my_room)
                else:
                    print 'Something is wrong!'
            player.emit('update_room_list', host_list, players_list, capacity_list, room_index, player.isHost)

    # create a room
    def on_create_room(self):
        if self.my_room == None:
            capacity = 4
            self.my_room = Room(self, capacity)
            self.isHost = 1;
            CardNamespace.rooms.append(self.my_room)
            CardNamespace.update_all_room_lists()
        else:
            print 'Cannot create a room if you are currently in one!'

    # join a room
    # hostname is the nickname of the host of the game you want to join
    def on_join(self, hostname):
        host = CardNamespace.players[hostname]
        room = host.my_room
        if room != None and host.isHost == 1:
            if not room.isFull():
                # joined room successfully
                room.addPlayer(self)
                CardNamespace.update_all_room_lists()
            else:
                print 'Room is full!'
        else:
            print 'Something is wrong!'

    # Leave a room
    # leave whichever room you are currently in
    def on_leave(self):
        if self.my_room == None:
            print 'Cannot leave a room if you are not in one!'
        else:
            # left room successfully
            self.my_room.removePlayer(self)
            CardNamespace.update_all_room_lists()

    # Delete a room
    # delete whichever room you are hosting
    def on_delete_room(self):
        if (not self.isHost) or self.my_room == None:
            print 'You have no room to delete!'
        else:
            # deleted room successfully
            self.isHost = 0
            CardNamespace.rooms.remove(self.my_room)
            self.my_room.delete()
            CardNamespace.update_all_room_lists()

    # Start game
    # called by host of game once enough players have joined
    def on_start_game(self):
        # TODO
        print 'Game started!'

# Room class
class Room:

    # state
    host = None
    players = []  # list of players (CardNamespace objects) currently joined
    capacity = 0  # total number of players
    # should also eventually know which game is being played in this room

    def __init__(self, host, capacity):
        self.host = host
        self.players = [host]
        self.capacity = capacity
    
    def players_joined(self):
        return len(self.players)

    def isFull(self):
        return self.players_joined() >= self.capacity

    def addPlayer(self, p):
        if p in self.players:
            print 'Cannot add the same player to a room twice!'
        elif self.isFull():
            print 'Cannot add player because room is full!'
        else:
            self.players.append(p)
            p.my_room = self

    def removePlayer(self, p):
        if not p in self.players:
            print 'Cannot remove player because player is not in room!'
        else:
            self.players.remove(p)
            p.my_room = None

    # delete this room and remove all players
    def delete(self):
        for p in self.players:
            p.my_room = None
