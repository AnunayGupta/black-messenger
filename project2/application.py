import os

from collections import deque

from flask import Flask, render_template, session, request, redirect
from flask_socketio import SocketIO, send, emit, join_room, leave_room

from helpers import login_required

app = Flask(__name__)
app.config["SECRET_KEY"] = "my secret key"
socketio = SocketIO(app)

# Keep track of channels created (Check for channel name)
channelsCreated = []

# Keep track of users logged (Check for username)
usersLogged = []

# Instanciate a dict
channelsMessages = dict()

@app.route("/")
@login_required
def index():
    return render_template("index.html", channels=channelsCreated)

@app.route("/signin",methods = ["GET","POST"])
def signin():

    session.clear()

    if request.method == 'POST':
        username = request.form.get("username")

        if len(username) == 0 or username == "" :
            return render_template("error.html",message="username required")
        if username in usersLogged :
            return render_template("error.html",message="username already exists")

        usersLogged.append(username)

        session['username'] = username

        session.permanent = True

        return redirect("/")

    else:
        return render_template("signin.html")

@app.route("/logout",methods=["GET"])
@login_required
def logout() :
    try:
        usersLogged.remove(session['username'])
    except ValueError:
        pass

    # Delete cookie
    session.clear()
    return redirect("/")
@app.route("/create",methods = ["GET","POST"])
@login_required
def create():

    if request.method == "POST" :
        newChannel = request.form.get("channel")

        if newChannel in channelsCreated :
            return render_template("error.html",message= "Channel name not available")

        channelsCreated.append(newChannel)

        channelsMessages[newChannel] = deque()

        return redirect("/channels/" + newChannel)

    else:
        return render_template("index.html", channels = channelsCreated)

@app.route("/channels/<channel>", methods=['GET','POST'])
@login_required
def enter_channel(channel):
    session['current_channel'] = channel

    if request.method == "POST":
        return redirect("/")
    else:
        return render_template("channel.html", channels= channelsCreated, messages=channelsMessages[channel])

@socketio.on("joined", namespace='/')
def joined():
    """ Send message to announce that user has entered the channel """

    # Save current channel to join room.
    room = session.get('current_channel')

    join_room(room)

    emit('status', {
        'userJoined': session.get('username'),
        'channel': room,
        'msg': session.get('username') + ' has entered the channel'},
        room=room)

@socketio.on("left", namespace='/')
def left():
    """ Send message to announce that user has left the channel """

    room = session.get('current_channel')

    leave_room(room)

    emit('status', {
        'msg': session.get('username') + ' has left the channel'},
        room=room)

@socketio.on('send message')
def send_msg(msg, timestamp):
    """ Receive message with timestamp and broadcast on the channel """

    # Broadcast only to users on the same channel.
    room = session.get('current_channel')

    # Save 100 messages and pass them when a user joins a specific channel.

    if len(channelsMessages[room]) > 100:
        # Pop the oldest message
        channelsMessages[room].popleft()

    channelsMessages[room].append([timestamp, session.get('username'), msg])

    emit('announce message', {
        'user': session.get('username'),
        'timestamp': timestamp,
        'msg': msg},
        room=room)
