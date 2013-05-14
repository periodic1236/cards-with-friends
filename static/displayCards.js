function addCard(cardimg) {
	var hand = document.getElementById("hand");
	//add the card to the hand
	var newCard = document.createElement("img");
	newCard.setAttribute("class", 'card');
	newCard.setAttribute("src", cardimg);
	hand.appendChild(newCard);
}

window.onload = function(){
	addCard("card_images/std_Q_C.png");
};