from flask import Flask, request, send_file, render_template, url_for

import config
from card_frontend import *
'''
# Test "game" function
def PlayGame(players):
  # "deal" cards
  p1 = players[0]
  p2 = players[1]
  p1.add_card('std_7_H')
  p1.add_card('std_J_C')
  p2.add_card('std_4_S')
  p2.add_card('std_A_D')
  curr_card = p1.cardPlayed
  p1.start_turn()  # player 1's turn first
  while(curr_card == p1.cardPlayed):
    sleep(1)
  print p1.cardPlayed
'''

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

