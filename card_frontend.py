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


# The socket.io namespace
# always extend BaseNamespace; also add mixins if you want
# a new object of this type is created for each client
class CardNamespace(BaseNamespace, RoomsMixin, BroadcastMixin):

    # state
    players = {}  # (static) dict of players (instances of CardNamespace)
    num_players = 0  # (static) how many clients connected
    player_num = 0

    # this player's hand
    hand = []  # cards held by this player
    cardPlayed = [] # card played in this trick

    # specific to this hard-coded game
    total_players = 2

    # runs when client enters nickname to log in
    def on_login(self, nickname):

        self.player_num = CardNamespace.num_players
        CardNamespace.num_players += 1

        # Empty hand
        self.hand = []

        # Make sure there aren't too many players
        if self.player_num > CardNamespace.total_players:
            raise Exception('Too many players!')

        # add myself to list of players
        if nickname in CardNamespace.players:
          raise NotImplementedError("Player Name Conflict")
        CardNamespace.players[nickname] = self

        # send message to my client (only) with player num
        self.emit('player_num', self.player_num)

        # Just have them join a default-named room
        self.join('main_room')

        # if all players have joined, start game
        if CardNamespace.num_players == CardNamespace.total_players:
          game = games.highest_card.HighestCard(CardNamespace.players.keys())
          game.PlayGame()


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
        self.emit('get_card', self.player_num, cards_allowed)
