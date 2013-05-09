var myPlayerNum = 0;
var cardImagePath = "static/card_images/";
var allowedCards = [];
var socket = io.connect();

function cardPlayed(e, card) {
  //TODO check that it is the players turn so that we can move allowedCards
  //to a function argument.
  if ($.inArray(card, allowedCards) != -1) {
    document.getElementById('hand').removeChild(e.target);  // remove card from screen
    socket.emit('card_played', card);
    allowedCards = [];
  }
}

function addCard(card) {
	var hand = $('#hand');
	// add the card to the hand
	var newCard = document.createElement("img");
	newCard.setAttribute("class", 'card');
    newCard.setAttribute("name", card);
	newCard.setAttribute("src", cardImagePath + card + '.png');
    newCard.addEventListener('click', function(e) { cardPlayed(e, card); });
    hand.append(newCard);
}

function add_card_to_hand(playerNum, card) {
  //Add to hand if it is being added to my hand
  if (playerNum == myPlayerNum){
    addCard(card);
  }
}

function get_card(playerNum, allowed_cards){
  //alert('Your turn! ' + allowed_cards);
  if (playerNum == myPlayerNum){  
    allowedCards = allowed_cards;
  }
}

socket.on('player_num', function(playernum) {
  myPlayerNum = playernum;
});

socket.on('add_to_hand', add_card_to_hand);

socket.on('get_card', get_card);

socket.on('play_card', function (username, data) {
  $('#trick').append('<b>'+username + ':</b> ' + data + '<br>');
});

socket.on('clear_trick', function() {
  $('#trick').empty();
}

socket.on('update_sequence', function (sender, data) {
  $('#playersequence').empty();
  $('#playersequence').append(sender + ': ' + '<b>' +  data  + '</b><br>');
});

socket.on('update_players', function(data) {
  $('#players').empty();
  $.each(data, function(key, value) {
    $('#players').append('<div>' + key + '</div>');
  });
});
