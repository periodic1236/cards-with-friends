// create new room
function create_room() {
    game_name = $("#select_game").find('option:selected').attr('value');
    num_players = $("#select_players").find('option:selected').attr('value');
    socket.emit('create_room', game_name, num_players);
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
socket.on('update_room_list', function(game_list, host_list, players_list, capacity_list, my_room, host) {
    var holder = document.getElementById('room_list');
    while (holder.hasChildNodes()) {
        holder.removeChild(holder.lastChild);
    }
    for (var i = 0; i < host_list.length; i++) {
        var newDiv = document.createElement('div');
        newDiv.innerHTML = "Game: " + game_list[i] + "&nbsp;&nbsp;&nbsp;Host: " + host_list[i] + "&nbsp;&nbsp;&nbsp;Players: " + players_list[i] + "/" + capacity_list[i] + "&nbsp;&nbsp;&nbsp;";
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
        document.getElementById('new_room_menu').style.visibility="hidden";
    }
    else {
        document.getElementById('new_room_menu').style.visibility="visible";
        
        games = get_game_names();
        current_game = games[0];
        num_players = get_valid_num_player_list(current_game);

        // populate game list
        var options = $("#select_game");
	    options.empty();
        for (i = 0; i < games.length; i++){
		    opt = document.createElement('option');
		    opt.value = games[i];
		    opt.innerHTML = games[i];
		    options.append(opt);
	    }

        // populate num_player list
        populate_num_player_list(num_players);

        // when game type changed, repopulate num_player list
        $("#select_game").change(function(){
            current_game = $(this).find('option:selected').attr('value');
            num_players = get_valid_num_player_list(current_game);
            populate_num_player_list(num_players);
        });
        
    }
});

// populate num_player list
// num_players is a list of valid player numbers
function populate_num_player_list(num_players) {
    var nums = $("#select_players");
    nums.empty();
    for (i = 0; i < num_players.length; i++){
	    num = document.createElement('option');
	    num.value = num_players[i];
	    num.innerHTML = num_players[i];
	    nums.append(num);
    }
}

// get list of game names that can be played
function get_game_names() {
    // TODO
    return ['Hearts', 'Spades', 'Bridge'];
}

// get valid num_player list given a game name
function get_valid_num_player_list(game_name) {
    // TODO
    if (game_name == 'Hearts') {
        return [2, 3, 4, 5];
    }
    return [1, 2, 3, 4];
}

// called when the game starts
// redirect everyone in the room to the game table page
socket.on('go_to_game_table', function() {
    window.location = '/game_table';
});
