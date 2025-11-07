"""chance and community chest"""

from random import shuffle

import state
import utils


class chance_class(utils.parent_class):
    """contains all actions related to chance card management"""

    def __init__(self):

        # note: the numbers at the start are for saving the arrangement of the shuffled cards
        self.cards = [
                      "Advance to go (collect $200)",
                      "Advance to Trafalgar Square. If you pass go, collect $200",
                      "Advance to Pall Mall. If you pass go, collect $200",
                      "Advance to the nearest utility. If unowned, you may buy it from the bank. If owned, throw the dice and pay owner 10x dice roll",
                      "Advance to the nearest station. If unowned, you may buy it from the bank. If owned, pay owner twice the rental to which they are otherwise entitled",
                      "Bank pays you dividend of $50",
                      "Get out of jail free. This card may be kept until needed or traded",
                      "Go back three spaces",
                      "Go directly to jail. Do not pass go, do not collect $200",
                      "Make general repairs on all your property: For each house pay $25, for each hotel pay 100",
                      "Take a trip to Kings Cross Station. If you pass go, collect $200.",
                      "Advance to Mayfair",
                      "You have been elected chairman of the board. Pay each player $50",
                      "Your building loan matures. Collect $150",
                      "Speeding fine $15",
        ]
        self.art = [
                    r"✨     /¯¯¯| |¯| |¯|   /¯\   |¯¯\|¯|  /¯¯¯| |¯¯¯|   ✨  ",
                    r"   ✨ | (⁐⁐  | ¯¯¯ |  / ^ \  | \ \ | | (⁐⁐  | ⁐|_ ✨    ",
                    r" ✨    \___| |_|¯|_| /_/¯\_\ |_|\__|  \___| |___|     ✨",
]

        self.values = [0, 1, 2, 3, 4, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
        shuffle(self.values)
        self.index = -1

    def __str__(self):
        return self.cards[self.values[self.index]]

    def draw_card(self):
        """returns the next shuffled card message"""

        # this draws the next chance card, if exceeded resets to zero
        self.index += 1
        try:
            return self.cards[self.values[self.index]]
        except IndexError:
            self.index = 0
            return self.cards[self.values[self.index]]

    def perform_action(self):
        """
        performs action based on draw_card(). 
        Can be done multiple times per card but requires at least one draw_card()
        """

        drawn_card = self.values[self.index]

        if drawn_card == 0:
            "Advance to go (collect $200)"

            # updates position and money
            state.player[state.player_turn]["last pos"] = state.player[state.player_turn]["pos"]
            state.player[state.player_turn]["pos"] = 0
            state.player[state.player_turn]["$$$"] += 200

            # updates displayed text + icons
            state.refresh_board.passed_go = True
            utils.update_player_position(state.player[state.player_turn]["pos"])
            utils.update_player_position(state.player[state.player_turn]["last pos"], "remove")

        elif drawn_card == 1:
            "Advance to Trafalgar Square. If you pass go, collect $200"
            state.player[state.player_turn]["last pos"] = state.player[state.player_turn]["pos"]
            state.player[state.player_turn]["pos"] = 24

            if state.player[state.player_turn]["last pos"] > 24:
                state.player[state.player_turn]["$$$"] += 200
                state.refresh_board.passed_go = True
            state.player_action(state.player_turn)
            utils.update_player_position(state.player[state.player_turn]["pos"])
            utils.update_player_position(state.player[state.player_turn]["last pos"], "remove")

        elif drawn_card == 2:
            state.player[state.player_turn]["last pos"] = state.player[state.player_turn]["pos"]
            state.player[state.player_turn]["pos"] = 11

            if state.player[state.player_turn]["last pos"] > 11:
                state.player[state.player_turn]["$$$"] += 200
            state.player_action(state.player_turn)
            utils.update_player_position(state.player[state.player_turn]["pos"])
            utils.update_player_position(state.player[state.player_turn]["last pos"], "remove")

        elif drawn_card == 3:

            # this moves the player to waterworks if between electricity
            # company and waterworks, otherwise moves to electricity company
            state.player[state.player_turn]["last pos"] = state.player[state.player_turn]["pos"]
            if state.player[state.player_turn]["pos"] >= 12 and state.player[state.player_turn]["pos"] < 28:
                state.player[state.player_turn]["pos"] = 28

            elif state.player[state.player_turn]["pos"] >= 28:
                state.player[state.player_turn]["pos"] = 12
                state.player[state.player_turn]["$$$"] += 200

            else: state.player[state.player_turn]["pos"] = 12
            state.player_action.rent_mgmt(state.player_turn, 10)
            utils.update_player_position(state.player[state.player_turn]["pos"])
            utils.update_player_position(state.player[state.player_turn]["last pos"], "remove")
           
        elif drawn_card == 4:
            state.player[state.player_turn]["last pos"] = state.player[state.player_turn]["pos"]
            
            if   state.player[state.player_turn]["pos"] >= 35: state.player[state.player_turn]["pos"] = 5
            elif state.player[state.player_turn]["pos"] >= 25: state.player[state.player_turn]["pos"] = 35
            elif state.player[state.player_turn]["pos"] >= 15: state.player[state.player_turn]["pos"] = 25
            elif state.player[state.player_turn]["pos"] >= 5:  state.player[state.player_turn]["pos"] = 15

            # if the player is moved across GO (to Kings Cross), they gain $200
            if state.player[state.player_turn]["pos"] == 5:
                state.player[state.player_turn]["$$$"] += 200
                state.refresh_board.passed_go = True

            state.player_action.rent_mgmt(state.player_turn, 2)
            utils.update_player_position(state.player[state.player_turn]["pos"])
            utils.update_player_position(state.player[state.player_turn]["last pos"], "remove")

        elif drawn_card == 5:
            state.player[state.player_turn]["$$$"] += 50

        elif drawn_card == 6:
            state.player[state.player_turn]["jail passes"] += 1

        elif drawn_card == 7:
            state.player[state.player_turn]["last pos"] = state.player[state.player_turn]["pos"]
            state.player[state.player_turn]["pos"] -= 3
            state.player_action(state.player_turn)
            utils.update_player_position(state.player[state.player_turn]["pos"])
            utils.update_player_position(state.player[state.player_turn]["last pos"], "remove")

        elif drawn_card == 8:
            state.player_action.send_to_jail()
            
        elif drawn_card == 9:
            state.player[state.player_turn]["$$$"] -= ((state.player[state.player_turn]["house total"] * 25) + (state.player[state.player_turn]["hotel total"] * 100))
            if state.player[state.player_turn]["$$$"] < 0:
                state.player_is_broke(state.player_turn)

        elif drawn_card == 10:
            "Take a trip to Kings Cross Station. If you pass go, collect $200.",

            # updates position
            state.player[state.player_turn]["last pos"] = state.player[state.player_turn]["pos"]
            state.player[state.player_turn]["pos"] = 5

            # gives player + $200 for passing GO
            state.player[state.player_turn]["$$$"] += 200
            state.refresh_board.passed_go = True

            state.player_action(state.player_turn)
           
            # updates displayed_position
            utils.update_player_position(state.player[state.player_turn]["pos"])
            utils.update_player_position(state.player[state.player_turn]["last pos"], "remove")

        elif drawn_card == 11:
            state.player[state.player_turn]["last pos"] = state.player[state.player_turn]["pos"]
            state.player[state.player_turn]["pos"] = 39
            state.player_action(state.player_turn)
            utils.update_player_position(state.player[state.player_turn]["pos"])
            utils.update_player_position(state.player[state.player_turn]["last pos"], "remove")

        elif drawn_card == 12:
            for i in range(state.players_playing):
                if i + 1 != state.player_turn:
                    state.player[i + 1]["$$$"] += 50

            state.player[state.player_turn]["$$$"] -= 50 * (state.players_playing - 1)

            if state.player[state.player_turn]["$$$"] < 0:
                state.player_is_broke(state.player_turn)

        elif drawn_card == 13:
            state.player[state.player_turn]["$$$"] += 150

        elif drawn_card == 14:
            state.player[state.player_turn]["$$$"] -= 15
            if state.player[state.player_turn]["$$$"] < 0:
                state.player_is_broke(state.player_turn)

        state.refresh_board()


class community_chest_class(utils.parent_class):
    """contains all actions related to community chest card management"""

    def __init__(self):
        self.cards = [
                     "Advance to go (collect $200)",
                     "Bank error in your favour. Collect $200",
                     "Doctor's fees. Pay $50",
                     "From sale of stock you get $50",
                     "Get out of jail free. This card may be kept until needed or traded",
                     "Go directly to jail. Do not pass go, do not collect $200",
                     "Holiday fund matures. Collect $100",
                     "Income tax refund. Collect $20",
                     "It's your birthday. Collect $10 from every player",
                     "Life insurance matures. Collect $100",
                     "Hospital fees. Pay $100",
                     "You have won second prise in a beauty contest. Collect $10",
                     "You are assessed for street repairs: Pay $40 per house and $115 per hotel you own",
                     "School fees. Pay $50",
                     "Receive $25 consultancy fee.",
                     "You inherit $100",
]
        self.art = [
                    r"✨     /¯¯¯|  /¯¯\  |¯¯\/¯¯| |¯¯\/¯¯| |¯||¯| |¯¯\|¯| |¯¯¯| |¯¯¯¯¯| \¯\/¯/    /¯¯¯| |¯| |¯| |¯¯¯| /¯⁐⁐| |¯¯¯¯¯|   ✨  ",
                    r"   ✨ | (⁐⁐  | () | | \  / | | \  / | | || | | \ \ | _| |_  ¯| |¯   \  /    | (⁐⁐  | ¯¯¯ | | ⁐|_ \__ \  ¯| |¯  ✨    ",
                    r" ✨    \___|  \__/  |_|\/|_| |_|\/|_|  \__/  |_|\__| |___|   |_|    /_/      \___| |_|¯|_| |___| |___/   |_|       ✨",
]

        self.index = -1
        self.values = list(range(0, 16))
        shuffle(self.values)

    def __str__(self):
        return self.cards[self.values[self.index]]

    def draw_card(self):
        """returns the next shuffled card message"""

        # this draws the next chance card, if exceeded resets to zero
        self.index += 1
        try:
            return self.cards[self.values[self.index]]
        except IndexError:
            self.index = 0

    def perform_action(self):
        """
        performs action based on draw_card(). 
        Can be done multiple times per card but requires at least one draw_card() 
        """

        drawn_card = int(self.values[self.index])

        if drawn_card == 0:
            state.player[state.player_turn]["last pos"] = state.player[state.player_turn]["pos"]
            state.player[state.player_turn]["pos"] = 0
            state.player[state.player_turn]["$$$"] += 200
            utils.update_player_position(state.player[state.player_turn]["pos"])
            utils.update_player_position(state.player[state.player_turn]["last pos"], "remove")
           
        elif drawn_card == 1:
            state.player[state.player_turn]["$$$"] += 200

        elif drawn_card == 2:
            state.player[state.player_turn]["$$$"] -= 50
            if state.player[state.player_turn]["$$$"] < 0:
                state.player_is_broke(state.player_turn)

        elif drawn_card == 3:
            state.player[state.player_turn]["$$$"] += 50

        elif drawn_card == 4:
            state.player[state.player_turn]["jail passes"] += 1

        elif drawn_card == 5:
            state.player_action.send_to_jail()

        elif drawn_card == 6:
            state.player[state.player_turn]["$$$"] += 100

        elif drawn_card == 7:
            state.player[state.player_turn]["$$$"] += 20

        elif drawn_card == 8:
            state.player[state.player_turn]["$$$"] += 10 * (state.players_playing - 1)

            # all other players get deducted $10, checks if they're broke
            for i in range(1, state.players_playing + 1):
                if i != state.player_turn:
                    state.player[i]["$$$"] -= 10
                    if state.player[i]["$$$"] < 0 and state.player[i] == "playing":
                        state.player_is_broke(i)

        elif drawn_card == 9:
            state.player[state.player_turn]["$$$"] += 100
    
        elif drawn_card == 10:
            state.player[state.player_turn]["$$$"] -= 100

            if state.player[state.player_turn]["$$$"] < 0:
                state.player_is_broke(state.player_turn)
    
        elif drawn_card == 11:
            state.player[state.player_turn]["$$$"] += 10

        elif drawn_card == 12:
            state.player[state.player_turn]["$$$"] -= ((state.player[state.player_turn]["house total"] * 40) + (state.player[state.player_turn]["hotel total"] * 115))
            if state.player[state.player_turn]["$$$"] < 0:
                state.player_is_broke(state.player_turn)

        elif drawn_card == 13:
            state.player[state.player_turn]["$$$"] -= 50
            if state.player[state.player_turn]["$$$"] < 0:
                state.player_is_broke(state.player_turn)

        elif drawn_card == 14:
            state.player[state.player_turn]["$$$"] += 25

        elif drawn_card == 15:
            state.player[state.player_turn]["$$$"] += 100

        state.refresh_board()
