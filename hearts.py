class hearts(trick_taking_game):
    def __init__(self):
        # Players of the game
        self.players = ["alpha", "beta", "gamma", "delta"]
        # Hands of the players each round
        self.hands = {"alpha": Set([]), "beta": Set([]), "gamma": Set([]), "delta": Set([])}
        # Cards taken by each player each round
        self.taken = {"alpha": Set([]), "beta": Set([]), "gamma": Set([]), "delta": Set([])}
        # Cumulative score of each player
        self.scores = {"alpha": 0, "beta": 0, "gamma": 0, "delta": 0}
        # Deck of cards to use
        self.deck = standard_deck()
        # Round number
        self.round_num = 0
        # State of game each round. In this case, (hearts broken, trick number, first player, cards played)
        self.state = {"hearts_broken": False, "trick_num": 0, "first_player": None, "cards_played": []}

    def play_game(self):
        # Play until someone's score is >= 100
        while not terminate_game():
            # Reset hands, shuffle and deal cards
            new_round()
            # Pass cards left, right, across, or not at all based on the round number
            pass_cards()
            # Identify first player of the round
            self.state["first_player"] = get_first_player()
            # Play 13 tricks
            for trick_num in range(13):
                self.state["trick_num"] = trick_num
                self.state["cards_played"] = []
                # Have each player play a valid card for the trick
                for i in range(4):
                    self.state["cards_played"].append(get_valid_play(self.players[(first_player + i) % 4]))
                # Determine who got the trick, and give them the cards
                give_cards_to_trick_taker()
            # Calculate and add scores
            score_round()
        return self.scores

    def terminate_game():
        if max(self.scores.values()) <= 100:
            return False
        return True

    def new_round():
        for p in self.players:
            self.hands[p] = Set([])
            self.taken[p] = Set([])
        self.deck = standard_deck()
        self.round_num += 1
        self.state = {"hearts_broken": False, "trick_num": 0, "first_player": None, "cards_played": []}

        self.deck.shuffle()
        deal_cards(self.players, self.hands, self.deck)

    def pass_cards():
        if self.round_num % 4 == 1: pass_cards([self.players[0], self.players[1], 3], [self.players[1], self.players[2], 3], [self.players[2], self.players[3], 3], [self.players[3], self.players[0], 3])
        elif self.round_num % 4 == 2: pass_cards([self.players[0], self.players[3], 3], [self.players[1], self.players[0], 3], [self.players[2], self.players[1], 3], [self.players[3], self.players[2], 3])
        elif self.round_num % 4 == 3: pass_cards([self.players[0], self.players[2], 3], [self.players[1], self.players[3], 3], [self.players[2], self.players[0], 3], [self.players[3], self.players[1], 3])
        elif self.round_num % 4 == 0: pass

    def get_first_player():
        # Find first player (has 2 of clubs)
        for i in range(4):
            if (2, "C") in self.hands[self.players[i]]:
                return i

    def get_valid_play(player):
        card = None
        # If the play is the first play of the trick
        if len(self.state["cards_played"]) == 0:
            while True:
                card = select_card(player)
                # Cannot play queen of spades if hearts not broken
                if card == (12, "S") and not self.state["hearts_broken"]:
                    invalid_warning(card, player, "Hearts not broken")
                    continue
                # Check if can play a heart
                elif card[1] == "H" and not self.state["hearts_broken"]:
                    # If the player has only hearts, playing a heart is valid
                    for c in self.hands[player]:
                        if c[1] != "H": break
                    else: 
                        self.state["hearts_broken"] = True
                        self.hands[player].remove(card)
                        break
                    invalid_warning(card, first_player, "Hearts not broken")
                    continue
                # If the card selected is not the queen of spades or a heart, the play is fine
                self.hands[player].remove(card)
                break
        else:
            while True:
                card = select_card(player)
                # Must follow suit if possible
                if card[1] != self.state["cards_played"][0][1]:
                    for c in self.hands[player]:
                        if c[1] == self.state["cards_played"][0][1]: break
                    else: 
                        # Cannot play queen of spades the first trick
                        if card == (12, "S") and self.state["trick_num"] == 0:
                            invalid_warning(card, self.players[player], "Hearts not broken")
                            continue
                        # Cannot play heart the first trick, unless hand is all hearts
                        elif card[1] == "H" and self.state["trick_num"] == 0:
                            for c in self.hands[player]:
                                if c[1] != "H": break
                            else: 
                                self.state["hearts_broken"] = True
                                self.hands[player].remove(card)
                                break
                            invalid_warning(card, player, "Cannot play a heart on the first trick")
                            continue
                        elif card[1] == "H" and not self.state["hearts_broken"]: self.state["hearts_broken"] = True
                        self.hands[first_player].remove(card)
                        break
                    invalid_warning(card, self.players[player], "Must follow suit")
                    continue
                # If the suit matches, the play is valid
                self.hands[first_player].remove(card)
                break

        return card

    # David needs to fix this function
    def give_cards_to_trick_taker():
        for i in range(1, 4):
            if cards_played[i][1] == cards_played[trick_taker][1] and cards_played[i][0] > cards_played[trick_taker][0]: trick_taker = i
        self.taken[self.players[trick_taker]].update(cards_played)

    def score_round():
        # Update scores, taking shooting the moon into account
        curr_round_scores = {}
        for p in self.players:
            curr_round_scores[p] = 0
        for p in self.players:
            for c in self.taken[p]:
                if c == (12, "S"): curr_round_scores[p] += 13
                elif c[1] == "H": curr_round_scores[p] += 1

        if max(curr_round_scores.values()) == 26:
            for p in self.players:
                if curr_round_scores[p] != 26:
                    self.scores[p] += 26
        else:
            for p in self.players:
                self.scores[p] += curr_round_scores[p]

