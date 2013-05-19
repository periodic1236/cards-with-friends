var cardImagePath = "static/card_images/";
var allowedCards = [];
var socket = io.connect();

// Given a list of valid bids, will update the drop down list
// of bids that a player can make
function updateBids(validBids){
	var theBids = document.getElementById("bids");
	
	// first remove all previous valid bids
	while (theBids.hasChildNodes()){
		theBids.removeChild(theBids.lastChild);
	}
	
	// update combo box of bids with valid bids
	for (i = 0; i < validBids.length; i++){
		aBid = document.createElement('option');
		aBid.value = validBids[i];
		aBid.innerHTML = validBids[i];
		theBids.appendChild(aBid);
	}
}

function readyGame() {
  socket.emit('ready_game');
}

function returnCard(e, card) {
  //TODO check that it is the players turn so that we can move allowedCards
  //to a function argument.
  if ($.inArray(card, allowedCards) != -1) {
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

function addToTrickArea(card, image) {
  var trickArea = $('#trick');
	var newCard = document.createElement("img");
	newCard.setAttribute("class", 'card');
  newCard.setAttribute("id", card);
	newCard.setAttribute("src", image);
  trickArea.append(newCard);
}

function removeCard(card) {
  var hand = $('#hand');
  $('#' + card).remove();
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
socket.on('add_to_trick_area', addToTrickArea);

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
