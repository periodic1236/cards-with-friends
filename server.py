from functools import wraps
from flask import Flask, request, send_file, render_template, url_for, \
        redirect, flash, session
import config
from card_frontend import *

def login_required(f):
  @wraps(f)
  def decorated_function(*args, **kwargs):
    if 'nickname' not in session:
      return redirect(url_for('login'))
    return f(*args, **kwargs)
  return decorated_function

# Flask routes
# basic Flask setup
app = Flask(__name__)
app.secret_key = config.SECRET_KEY
@app.route('/')
def index():
  return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
  """Procedure to handle the login page."""
  if request.method == 'POST':
    nickname = request.form['nick']
    print nickname
    if HandleLogin(nickname):
      session['nickname'] = nickname
      return redirect(url_for('games'))
    else:
      flash('Nickname is already taken. Pick another one.')
      return render_template('login.html')
  return render_template('login.html')

@app.route('/about_making_games')
def documentation():
  #TODO write documentation page
  return render_template('documentation.html')

@app.route('/games')
@login_required
def games():
  return render_template('games.html')

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

