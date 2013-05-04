from gevent import monkey; monkey.patch_all()
from flask import Flask, request, send_file, render_template, url_for

from socketio import socketio_manage
from socketio.namespace import BaseNamespace
from socketio.mixins import RoomsMixin, BroadcastMixin
import config

# The socket.io namespace
# always extend BaseNamespace; also add mixins if you want
# a new object of this type is created for each client
class CardNamespace(BaseNamespace, RoomsMixin, BroadcastMixin):

    # state
    players = []  # (static) list of players (instances of CardNamespace)
    num_players = 0  # (static) how many clients connected
    player_num = 0

    # this player's hand
    hand = []  # cards held by this player

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
        CardNamespace.players.append(self)

        # send message to my client (only) with player num
        self.emit('player_num', self.player_num)

        # Just have them join a default-named room
        self.join('main_room')

        # if all players have joined, start game
        if CardNamespace.num_players == CardNamespace.total_players:
            # "deal" cards
            p1 = CardNamespace.players[0]
            p2 = CardNamespace.players[1]
            p1.add_card('std_7_H')
            p1.add_card('std_J_C')
            p2.add_card('std_4_S')
            p2.add_card('std_A_D')
            p1.start_turn()  # player 1's turn first

    # runs when client plays a card
    def on_card_played(self, card):
        self.hand.remove(card);
        # begin next player's turn
        next_player = self.player_num + 1
        if next_player >= CardNamespace.num_players:
            next_player = 0
        CardNamespace.players[next_player].start_turn()

    # add card to hand
    def add_card(self, card):
        self.hand.append(card)
        self.emit('add_to_hand', self.player_num, card)

    # start my turn
    def start_turn(self):
        cards_allowed = self.hand
        # emit_to_room does not send to self
        self.emit_to_room('start_turn', self.player_num, cards_allowed)
        self.emit('start_turn', self.player_num, cards_allowed)

# Flask routes
# basic Flask setup
app = Flask(__name__)
app.secret_key = config.SECRET_KEY
@app.route('/')
def login():
    return render_template('main.html');

# this runs as soon as a client is started
@app.route("/socket.io/<path:path>")
def run_socketio(path):
    # second argument maps urls to namespace classes
    socketio_manage(request.environ, {'': CardNamespace})

# main method
# runs when server starts
if __name__ == '__main__':
    print 'Listening on http://localhost:8080'
    app.debug = True
    import os
    from werkzeug.wsgi import SharedDataMiddleware # what is middleware?
    app = SharedDataMiddleware(app, {
        '/': os.path.join(os.path.dirname(__file__), 'static')
        })
    from socketio.server import SocketIOServer
    SocketIOServer(('0.0.0.0', 8080), app,
        resource="socket.io", policy_server=False).serve_forever()

