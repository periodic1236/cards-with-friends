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

function getCard(allowed_cards) {
  allowedCards = allowed_cards;
}

function clearHand() {
  $('#hand').empty();
}

function incrementTricksWon(nickname) {
  //TODO(brazon) implement once frontend complete
}

function resetTricksWon(nickname) {
  //TODO(brazon) implement once frontend complete
}

socket.on('add_to_hand', addCard);

socket.on('remove_from_hand', removeCard);

socket.on('get_card', getCard);

socket.on('clear_hand', clearHand);

//Todo rename and clean up this function
socket.on('play_card', function (username, data) {
  $('#trick').append('<b>'+username + ':</b> ' + data + '<br>');
});

//TODO Should this call a separate function like clear_hand?
socket.on('clear_trick_area', function() {
  $('#trick').empty();
});

socket.on('increment_tricks_won', incrementTricksWon);

socket.on('reset_tricks_won', resetTricksWon);

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
