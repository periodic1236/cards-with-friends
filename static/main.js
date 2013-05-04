var myPlayerNum = 0;
var cardImagePath = "static/card_images/";
var allowedCards = [];
var socket = io.connect();

function cardPlayed(e, card) {
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

function start_turn(playerNum, allowed_cards){
  //alert('Your turn! ' + allowed_cards);
  if (playerNum == myPlayerNum){  
    allowedCards = allowed_cards;
  }
}

function login() {
  nickname = $('#nick').val();
  socket.emit('login', nickname);
  console.log("nickname: ", nickname);
  $('#hand').css('display', 'block');
  $('#loginForm').css('display','none');
  return false;
}


socket.on('player_num', function(playernum) {
  myPlayerNum = playernum;
});

socket.on('add_to_hand', add_card_to_hand);

socket.on('start_turn', start_turn);

$(document).ready(function() {
  $('#hand').css('display', 'none')
  $('#loginForm').submit(function () {
    login();
    return false;
  });
});