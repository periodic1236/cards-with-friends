// create new room
function create_room() {
    socket.emit('create_room');
}

// request list of rooms
function request_room_list() {
    socket.emit('request_room_list');
}

// receive list of rooms
// host_list: list of room hosts
// players_list: list of how many players are currently in each room
// capacity_list: list of capacity of each room
// my_room: index in above lists; which game this player has joined (or -1 if none)
// host: 0 or 1 indicating whether you are the host of my_game
socket.on('update_room_list', function(host_list, players_list, capacity_list, my_room, host) {
    var holder = document.getElementById('room_list');
    while (holder.hasChildNodes()) {
        holder.removeChild(holder.lastChild);
    }
    for (var i = 0; i < host_list.length; i++) {
        var newDiv = document.createElement('div');
        newDiv.innerHTML = "Host: " + host_list[i] + "&nbsp;&nbsp;&nbsp;Players: " + players_list[i] + "/" + capacity_list[i] + "&nbsp;&nbsp;&nbsp;";
        holder.appendChild(newDiv);
        // if not joined a game, display a button for joining this game
        if (my_room < 0) {
            var button = document.createElement('input');
            button.setAttribute('type', 'button');
            button.setAttribute('value', 'Join');
            button.setAttribute('name', 'join_button');
            button.setAttribute('hostname', host_list[i]);  // let this button know which room it corresponds to
            newDiv.appendChild(button);
            button.onclick = function() {
                socket.emit('join', this.getAttribute('hostname'));
            };
        }
        // if already in this game but not the host, display a button for leaving this game
        if (my_room == i && host == 0) {
            var button = document.createElement('input');
            button.setAttribute('type', 'button');
            button.setAttribute('value', 'Leave');
            button.setAttribute('name', 'leave_button');
            newDiv.appendChild(button);
            button.onclick = function() {
                socket.emit('leave');
            };
        }
        // if host of this game, display a button to delete this game
        if (my_room == i && host == 1) {
            var button = document.createElement('input');
            button.setAttribute('type', 'button');
            button.setAttribute('value', 'Delete');
            button.setAttribute('name', 'delete_button');
            newDiv.appendChild(button);
            button.onclick = function() {
                socket.emit('delete_room');
            };
        }
        // if host of this game and it's full, display a button to start
        if (my_room == i && host == 1 && players_list[i] >= capacity_list[i]) {
            var button = document.createElement('input');
            button.setAttribute('type', 'button');
            button.setAttribute('value', 'Start Game');
            button.setAttribute('name', 'start_button');
            newDiv.appendChild(button);
            button.onclick = function() {
                socket.emit('start_game');
            };
        }
    }

    // remove "new room" button if this player has joined a game
    if (my_room >= 0) {
        document.getElementById('new_room_button').style.visibility="hidden";
    }
    else {
        document.getElementById('new_room_button').style.visibility="visible";
    }
});
