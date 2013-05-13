var myPlayerNum = 0;
var cardImagePath = "static/card_images/";
var allowedCards = [];
var socket = io.connect();

function returnCard(e, card) {
  //TODO check that it is the players turn so that we can move allowedCards
  //to a function argument.
  if ($.inArray(card, allowedCards) != -1) {
    //document.getElementById('hand').removeChild(e.target);  // remove card from screen
    socket.emit('card', card);
    allowedCards = [];
  }
}

function addCard(card, image) {
	var hand = $('#hand');
	// add the card to the hand
	var newCard = document.createElement("img");
	newCard.setAttribute("class", 'card');
  newCard.setAttribute("id", card);
	newCard.setAttribute("src", image);
  newCard.addEventListener('click', function(e) { returnCard(e, card); });
  hand.append(newCard);
}

function removeCard(card) {
  var hand = $('#hand');
  hand.removeChild($('#' + card));
}

function add_card_to_hand(playerNum, card) {
  //Add to hand if it is being added to my hand
  if (playerNum == myPlayerNum) {
    addCard(card);
  }
}

function remove_card_from_hand(playerNum, card) {
  //Remove from hand if it is being removed from my hand
  if (playerNum == myPlayerNum) {
    removeCard(card);
  }
}

function get_card(playerNum, allowed_cards) {
  if (playerNum == myPlayerNum) {  
    allowedCards = allowed_cards;
  }
}

function clear_hand(playerNum) {
  if (playerNum == myPlayerNum) {
    $('#hand').empty();
  }
}

socket.on('player_num', function(playernum) {
  myPlayerNum = playernum;
});

socket.on('add_to_hand', add_card_to_hand);

socket.on('remove_from_hand', remove_card_from_hand);

socket.on('get_card', get_card);

socket.on('clear_hand', clear_hand);

//Todo rename and clean up this function
socket.on('play_card', function (username, data) {
  $('#trick').append('<b>'+username + ':</b> ' + data + '<br>');
});

//TODO Should this call a separate function like clear_hand?
socket.on('clear_trick', function() {
  $('#trick').empty();
}

//Todo rename and clean up this function
socket.on('update_sequence', function (sender, data) {
  $('#playersequence').empty();
  $('#playersequence').append(sender + ': ' + '<b>' +  data  + '</b><br>');
});

//Todo rename and clean up this function
socket.on('update_players', function(data) {
  $('#players').empty();
  $.each(data, function(key, value) {
    $('#players').append('<div>' + key + '</div>');
  });
});
