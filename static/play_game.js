var cardImagePath = "static/card_images/";
var allowedCards = [];
var errorMessage = "That card is not allowed!";
var socket = io.connect();

(function( $ ) {
  $.widget( "custom.combobox", {
    _create: function() {
      this.wrapper = $( "<span>" )
        .addClass( "custom-combobox" )
        .insertAfter( this.element );

      this.element.hide();
      this._createAutocomplete();
      this._createShowAllButton();
    },

    _createAutocomplete: function() {
      var selected = this.element.children( ":selected" ),
        value = selected.val() ? selected.text() : "";

      this.input = $( "<input>" )
        .appendTo( this.wrapper )
        .val( value )
        .attr( "title", "" )
        .addClass( "custom-combobox-input ui-widget ui-widget-content ui-state-default ui-corner-left" )
        .autocomplete({
          delay: 0,
          minLength: 0,
          autoFocus: true,
          source: $.proxy( this, "_source" )
        })
        .tooltip({
          tooltipClass: "ui-state-highlight"
        });

      this._on( this.input, {
        autocompleteselect: function( event, ui ) {
          ui.item.option.selected = true;
          this._trigger( "select", event, {
            item: ui.item.option
          });
        },

        autocompletechange: "_removeIfInvalid"
      });
    },

    _createShowAllButton: function() {
      var input = this.input,
        wasOpen = false;

      $( "<a>" )
        .attr( "tabIndex", -1 )
        .attr( "title", "Show All Items" )
        .tooltip()
        .appendTo( this.wrapper )
        .button({
          icons: {
            primary: "ui-icon-triangle-1-s"
          },
          text: false
        })
        .removeClass( "ui-corner-all" )
        .addClass( "custom-combobox-toggle ui-corner-right" )
        .mousedown(function() {
          wasOpen = input.autocomplete( "widget" ).is( ":visible" );
        })
        .click(function() {
          input.focus();

          // Close if already visible
          if ( wasOpen ) {
            return;
          }

          // Pass empty string as value to search for, displaying all results
          input.autocomplete( "search", "" );
        });
    },

    _source: function( request, response ) {
      var matcher = new RegExp( $.ui.autocomplete.escapeRegex(request.term), "i" );
      response( this.element.children( "option" ).map(function() {
        var text = $( this ).text();
        if ( this.value && ( !request.term || matcher.test(text) ) )
          return {
            label: text,
            value: text,
            option: this
          };
      }) );
    },

    _removeIfInvalid: function( event, ui ) {

      // Selected an item, nothing to do
      if ( ui.item ) {
        return;
      }

      // Search for a match (case-insensitive)
      var value = this.input.val(),
        valueLowerCase = value.toLowerCase(),
        valid = false;
      this.element.children( "option" ).each(function() {
        if ( $( this ).text().toLowerCase() === valueLowerCase ) {
          this.selected = valid = true;
          return false;
        }
      });

      // Found a match, nothing to do
      if ( valid ) {
        return;
      }

      // Remove invalid value
      this.input
        .val( "" )
        .attr( "title", value + " didn't match any item" )
        .tooltip( "open" );
      this.element.val( "" );
      this._delay(function() {
        this.input.tooltip( "close" ).attr( "title", "" );
      }, 2500 );
      this.input.data( "ui-autocomplete" ).term = "";
    },

    _destroy: function() {
      this.wrapper.remove();
      this.element.show();
    }
  });
})( jQuery );

// Given a list of valid bids, will update the drop down list
// of bids that a player can make
function getBid(validBids){
	var bids = $("#bids");
	bids.empty();

	// update combo box of bids with valid bids
	for (i = 0; i < validBids.length; i++){
		aBid = document.createElement('option');
		aBid.value = validBids[i];
		aBid.innerHTML = validBids[i];
		bids.append(aBid);
	}
  $(bids).combobox();
  $('.custom-combobox-input').val('');
}

function returnBid() {
  var bid = $('#bids').val();
  socket.emit('bid', bid);
  $('#bids').empty();
  $('.custom-combobox-input').val('');
  return false;
}

function readyGame() {
  socket.emit('ready_game');
}

function returnCard(e, card) {
  //TODO check that it is the players turn so that we can move allowedCards
  //to a function argument.
  if ($.inArray(card, allowedCards) != -1) {
    $('#' + card).css('border', "solid 2px blue");  
    socket.emit('card', card);
    allowedCards = [];
    errorMessage = "That card is not allowed!";
  }
  else {
    if (allowedCards != '') {
      addMessage(errorMessage);
    }
  }
}

function addCard(card, image) {
	var hand = $('#hand');
  hand.sortable();
	// add the card to the hand
	var newCard = document.createElement("img");
	newCard.setAttribute("class", 'card');
  newCard.setAttribute("id", card);
	newCard.setAttribute("src", image);
  newCard.addEventListener('click', function(e) {
    returnCard(e, card);
  });
  $(newCard).sortable();
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

function addMessage(m) {
  var messageArea = $('#messageBox');
  var newMessage = document.createElement("div");
  $(newMessage).text(m);
  messageArea.append(newMessage);
}

function removeCard(card) {
  var hand = $('#hand');
  $('#' + card).remove();
}

function getCard(message, allowed_cards) {
  errorMessage = message;
  allowedCards = allowed_cards;
}

function clearHand() {
  $('#hand').empty();
}

function incrementTricksWon(nickname) {
  var tricksVal = $('#tricksTaken' + nickname);
  var tricks = parseInt(tricksVal.text().split(' ')[1]);
  tricksVal.text(nickname + ": " + (tricks + 1));
}

function resetTricksWon(nickname) {
  $('#tricksTaken' + nickname).text(nickname + ": 0");
}

function updateMoney(nickname, money) {
  $('#money' + nickname).text(nickname + ": $" + money);
}

function updateScore(nickname, score) {
  $('#score' + nickname).text(nickname + ": " + score);
}

function registerPlayer(nickname) {
  var playerName = document.createElement("div");
  playerName.setAttribute("id", "player" + nickname);
  $(playerName).text(nickname)
  $('#players').append(playerName);
  
  var scoreVal = document.createElement("div");
  scoreVal.setAttribute("id", "score" + nickname);
  $(scoreVal).text(nickname + ": 0");
  $('#score').append(scoreVal);

  var moneyVal = document.createElement("div");
  moneyVal.setAttribute("id", "money" + nickname);
  $('#money').append(moneyVal);
  $(moneyVal).text(nickname + ": $0");

  var tricksVal = document.createElement("div");
  tricksVal.setAttribute("id", "tricksTaken" + nickname);
  $('#tricksTaken').append(tricksVal);
  $(tricksVal).text(nickname + ": 0");
}

function startTurn(nickname) {
  $('#player' + nickname).text('--> ' + nickname);
}

function endTurn(nickname) {
  $('#player' + nickname).text(nickname);
}

function clearTrick() {
  setTimeout(function() { $('#trick').empty()}, 1000);
}

socket.on('add_to_hand', addCard);

socket.on('remove_from_hand', removeCard);

socket.on('get_card', getCard);

socket.on('clear_hand', clearHand);

socket.on('add_to_trick_area', addToTrickArea);

socket.on('clear_trick_area', clearTrick);

socket.on('increment_tricks_won', incrementTricksWon);

socket.on('reset_tricks_won', resetTricksWon);

socket.on('display_message', addMessage);

socket.on('update_money', updateMoney);

socket.on('update_score', updateScore);

socket.on('register_player', registerPlayer);

socket.on('start_turn', startTurn);

socket.on('end_turn', endTurn);

socket.on('get_bid', getBid);

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
