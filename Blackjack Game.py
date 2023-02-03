import random
import math

MAX_PLAYERS = 3
MIN_BET = 5
MAX_BET = 100

DECKS = 6
CARD_VALUES = {"2":2, "3":3, "4":4, "5":5, "6":6, "7":7, "8":8, "9":9, "10":10, "J":10, "Q":10, "K":10, "A":11}
COUNT_VALUES = {"2":1, "3":1, "4":1, "5":1, "6":1, "7":0, "8":0, "9":0, "10":-1, "J":-1, "Q":-1, "K":-1, "A":-1}

shoe = []
players = []
cut = 0
up_card = None
running_count = 0


# Todo check for sufficient funds as a function
# Todo rework get player bets


class Player:
    def __init__(self, name, balance=None):
        self.name = name
        self.balance = balance
        self.hands = []
        self.hand_type = None
        self.hand_value = 0
        self.bet = None
        self.resolved = False


class Hand:
    def __init__(self):
        self.cards = []
        self.type = None
        self.value = 0
        self.bet = None
        self.resolved = False
        self.completed = False


class Dealer:
    def __init__(self):
        self.name = "Dealer"
        self.balance = None
        self.hand = []
        self.hand_type = None
        self.hand_value = 0


def read_hand(hand):
    value = CARD_VALUES[hand[0]] + CARD_VALUES[hand[1]]
    if "A" in hand:
        hand_type = "Soft"
    else:
        hand_type = "Hard"

    if value == 21:
        hand_type = "BLACKJACK"
    elif value == 22:
        value = 12

    return hand_type, value


def update_hand(hand):
    card = deal_card()
    hand.cards.append(card)

    if card == "A":
        if hand.value <= 10:
            hand.type = "Soft"
            hand.value += 11
        else:
            hand.value += 1

    else:
        hand.value += CARD_VALUES[card]

    if hand.type == "Soft" and hand.value > 21:
        hand.type = "Hard"
        hand.value -= 10

    return


def build_prompt(player, hand):
    prompt = "What would you like to do? \n" \
             "1: Hit \n" \
             "2: Stand \n"

    valid_inputs = ["1", "2"]


    if len(hand.cards) == 2 and player.balance > hand.bet:
        prompt += "3: Double \n"
        valid_inputs.append("3")

        if CARD_VALUES[hand.cards[0]] == CARD_VALUES[hand.cards[1]] and len(player.hands) < 4:
                prompt += "4: Split \n"
                valid_inputs.append("4")

    prompt += f"Enter a number from 1 to {len(valid_inputs)}: "

    return prompt, valid_inputs

# Todo - organize splitting functionality properly
# Todo - get action as separate function

def player_turn(player):
    global up_card

    for hand in player.hands:
        while not hand.completed and not hand.resolved:
            print(f"{player.name}, you have {hand.cards}: {hand.type} {hand.value}.")
            print(f"Dealer has: {up_card}")
            print("")

            prompt, valid_actions = build_prompt(player, hand)

            while True:
                action = input(prompt)
                if action.isdigit() and action in valid_actions:
                    action = int(action)
                    break
                else:
                    print("")
                    print("Please enter a valid action.")
                    print("")

            print("")

            # Split
            if action == 4:
                new_hand = Hand()

                new_hand.bet = hand.bet
                player.balance -= new_hand.bet

                card = hand.cards.pop(1)
                new_hand.cards.append(card)

                hand.cards.append(deal_card())
                new_hand.cards.append(deal_card())

                hand.type, hand.value = read_hand(hand.cards)
                new_hand.type, new_hand.value = read_hand(new_hand.cards)

                if card == "A":
                    hand.completed = True
                    new_hand.completed = True

                for h in [hand, new_hand]:
                    if h.type == "BLACKJACK":
                        print(f"{player.name} has {h.type}: {h.cards}")
                        print("")
                        player.balance += 2.5*h.bet
                        h.completed = True
                        h.resolved = True

                player.hands.append(new_hand)

            # Double
            elif action == 3:
                player.balance -= hand.bet
                hand.bet *= 2
                update_hand(hand)
                print(hand.cards)
                if hand.value > 21:
                    print("Bust")
                    hand.resolved = True
                hand.completed = True

            # Stand
            elif action == 2:
                hand.completed = True

            # Hit
            elif action == 1:
                update_hand(hand)

                if hand.value > 21:
                    print(hand.cards)
                    print("Bust")
                    hand.completed = True

    return


def dealer_turn(dealer):
    while dealer.hand_value < 17:
        card = deal_card()
        dealer.hand.append(card)
        print(f"Dealer hits: {dealer.hand}")

        if card == "A":
            if dealer.hand_value <= 10:
                dealer.hand_type = "Soft"
                dealer.hand_value += 11
            else:
                dealer.hand_value += 1
        else:
            dealer.hand_value += CARD_VALUES[card]

        if dealer.hand_type == "Soft" and dealer.hand_value > 21:
            dealer.hand_type = "Hard"
            dealer.hand_value -= 10
    return


def deposit():
    while True:
        amount = input("How much would you like to deposit? $")
        if amount.isdigit():
            amount = int(amount)
            if amount > 0:
                break
            else:
                print("Amount must be greater than 0.")
        else:
            print("Please enter a valid number.")

    return amount


def get_number_of_player():
    while True:
        num_players = input("Enter the number of players (1-" + str(MAX_PLAYERS) + ")? ")
        if num_players.isdigit():
            num_players = int(num_players)
            if 1 <= num_players <= MAX_PLAYERS:
                break
            else:
                print("Enter a valid number.")
        else:
            print("Please enter a valid number.")

    return num_players


def shuffle_shoe():
    global cut
    global shoe
    global running_count

    cards = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]*4*DECKS

    running_count = 0
    shoe = []
    # Todo cut should be calculated based on the number of decks being used.
    cut = int(math.floor(random.normalvariate(65, 13)))

    while cards:
        card = random.choice(cards)
        shoe.append(card)
        cards.remove(card)

    return


def deal_card():
    global running_count

    card = shoe.pop(0)
    running_count += COUNT_VALUES[card]
    return card


def get_bet(player):
    while True:
        amount = input(f"{player.name}, how much would you like to bet? $")
        if amount.isdigit():
            amount = int(amount)
            if MIN_BET <= amount <= MAX_BET:
                break
            else:
                print(f"Amount must be between ${MIN_BET} - ${MAX_BET}")
        else:
            print("Please enter a valid number.")

    return amount


def deal_hands(players, dealer):
    for i in range(2):
        for p in players:
            for h in p.hands:
                h.cards.append(deal_card())
        dealer.hand.append(deal_card())

    return


def resolve_blackjack(players, dealer):
    if dealer.hand_type == "BLACKJACK":
        print(f"{dealer.name} has {dealer.hand_type} {dealer.hand}")
        for p in players:
            for h in p.hands:
                if h.type == "BLACKJACK":
                    print(f"{p.name} has {h.type} ({h.cards}).")
                    print(f"{p.name}, result: Push")
                    p.balance += h.bet
                    h.resolved = True
                    h.completed = True
                else:
                    print(f"{p.name} has {h.cards}.")
                    print(f"Result: Loss")
                    h.resolved = True
                    h.completed = True
    else:
        for p in players:
            for h in p.hands:
                if h.type == "BLACKJACK":
                    print(f"{p.name} has {h.type} ({h.cards}).")
                    print("You won!")
                    print("")
                    p.balance += 2.5 * h.bet
                    h.resolved = True
                    h.completed = True

    return


def resolve_hands(players, dealer):
    for p in players:
        for h in p.hands:
            if not h.resolved:
                if h.value > 21:
                    print(f"{p.name}, you have {h.value}.")
                    print("Result: You bust.")
                    print("")
                    h.resolved = True
                elif dealer.hand_value > 21:
                    print(f"{p.name} has {h.value}, dealer has {dealer.hand_value}.")
                    print(f"Result: You won!")
                    print("")
                    p.balance += 2*h.bet
                    h.resolve = True
                elif h.value > dealer.hand_value:
                    print(f"{p.name} has {h.value}, dealer has {dealer.hand_value}.")
                    print(f"Result: You won!")
                    print("")
                    p.balance += 2*h.bet
                    h.resolve = True
                elif h.value == dealer.hand_value:
                    print(f"{p.name} has {h.value}, dealer has {dealer.hand_value}.")
                    print(f"Result: Push")
                    print("")
                    p.balance += h.bet
                    h.resolve = True
                else:
                    print(f"{p.name} has {h.value}, dealer has {dealer.hand_value}.")
                    print(f"Result: You lost")
                    print("")
                    h.resolve = True

    return


def play_hand(players, dealer):
    global up_card
    global running_count

    for p in players:
        print(f"{p.name}'s balance is: ${p.balance}")

    print("")

    # Todo Write function to check for sufficient funds?
    temp = []
    for p in players:
        while p.balance < MIN_BET:
            response = input(f"{p.name}: Insufficient funds. Would you like to deposit more money? (y/n): ")
            if response == "y":
                p.balance += deposit()
            elif response == "n":
                print("Thank you for playing.")
                print("")
                temp.append(p)
                break
            else:
                print("Please enter a valid response.")

    for p in temp:
        players.remove(p)

    for p in players:
        p.hands = []

    dealer.hand = []

    for p in players:
        hand = Hand()
        p.hands.append(hand)

    # Todo Clean get player bets
    for p in players:
        print(f"{p.name}, your current balance is ${p.balance}")
        print(f"Running count: {running_count}")
        print(f"True count: {math.floor(running_count/math.ceil(len(shoe)/52))}")
        for h in p.hands:
            while True:
                bet = get_bet(p)
                if bet > p.balance:
                    print(f"Insufficient funds. Your current balance is: ${p.balance}")
                else:
                    h.bet = bet
                    h.resolved = False
                    p.balance -= bet
                    print("")
                    break

    deal_hands(players, dealer)

    up_card = dealer.hand[1]

    for p in players:
        for h in p.hands:
            h.type, h.value = read_hand(h.cards)

    dealer.hand_type, dealer.hand_value = read_hand(dealer.hand)

    # Check and resolve for Blackjack
    resolve_blackjack(players, dealer)

    # Allow each player to play their hand
    for p in players:
        for hand in p.hands:
            if not hand.completed and not hand.resolved:
                player_turn(p)

    # Check for unresolved player hands before playing dealer turn
    for p in players:
        for hand in p.hands:
            if hand.value <= 21 and hand.type != "BLACKJACK":
                dealer_turn(dealer)
                break

    if dealer.hand_type != "BLACKJACK":
        print(f"{dealer.name} has: {dealer.hand}")

    print("")

    resolve_hands(players, dealer)

    return


def main():
    # Todo Ask for rules?
    # Todo Print rules

    num_players = get_number_of_player()

    # Create a list of players and initialize player attributes
    for i in range(num_players):
        name = input(f"Enter player{i+1}'s name: ")
        players.append(Player(name, deposit()))

    print("")

    dealer = Dealer()
    shuffle_shoe()

    while True:
        while len(shoe) > cut:
            if len(players) == 0:
                break
            play_hand(players, dealer)
        response = input("Would you like to keep playing (y/n)? ")
        if response == 'n':
            print("")
            break
        elif response == 'y':
            shuffle_shoe()
        else:
            print("please enter a valid response.")

    for p in players:
        print(f"{p.name}, your final balance is: ${p.balance}")

    print("Thank you for playing.")

main()
