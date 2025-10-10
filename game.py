"""most of game functionality: the board, trading, properties, bankruptcy"""

from random import randint
from time import time
from better_iterator import better_iter, tripple_affirmative

import utils
from utils import clear_screen, create_button_prompts, sleep, update_player_position, save_game_to_file
import state

__required__ = ["online.send_data"]
send_data = None

class player_is_broke_class(utils.parent_class):
    def __call__(self, _player: int, cause = None):
        """alerts the player that they are in debt/are bankrupt
        cause is passed on to bankruptcy if applicable. check requirements there"""
        state.current_screen = self.__name__

        clear_screen()

        player_has_properties = False

        # checks if the player could afford to pay off their debts,
        # if not, the prompt to declare bankruptcy appears.
        # even if that happens, the player is still shown their properties,
        # to attempt to trade their way out of bankruptcy
        available_funds = 0
        for i in range(28):

            # if the property is not owned by the player
            if state.property_data[i]["owner"] != _player:
                continue

            # if the property is already mortgaged
            if state.property_data[i]["upgrade state"] < 1:
                continue

            available_funds += (state.property_data[i]["street value"] / 2)

            # if the property doesn't have any upgrades
            if state.property_data[i]["upgrade state"] <= 2:
                continue

            number_of_upgrades = state.property_data[i]["upgrade state"] - 2
            available_funds += number_of_upgrades * (state.property_data[i]["house cost"] / 2)

            # ensures that the property list is brought up
            # instead of going directly to bankruptcy
            player_has_properties = True

        if player_has_properties == True:

            # this makes sure that the text is centered by adding extra space if the debt is a different length than 4 digits
            extra_space = ""
            for i in range(5 - len(str(abs(state.player[_player]["$$$"])))): extra_space += " "

            print()
            print("    ╔════════════════════════════════════════════════════════════════╗")
            print("    ║                                                                ║")
            print("    ║                             NOTICE:                            ║")
            print("    ║                                                                ║")
            print(f"    ║{extra_space}       state.player {state.player_turn}, You are ${abs(state.player[_player]['$$$'])} in debt! raise ${abs(state.player[_player]['$$$'])} by:       {extra_space}║")
            print("    ║                                                                ║")
            print("    ║       Mortgaging properties (for half of street vaule),        ║")
            print("    ║      Selling houses/hotels (for half build price), or by       ║")
            print("    ║          Trading with other players (without houses).          ║")
            print("    ║                                                                ║")
            if available_funds < abs(state.player[_player]["$$$"]):
                print("    ║           you have more debt than you can pay back,            ║")
                print("    ║       so you can declare bankruptcy, or attempt a trade.       ║")
                print("    ║                                                                ║")
            print("    ╚════════════════════════════════════════════════════════════════╝")

            state.state.display_property_list(_player, False, available_funds < abs(state.player[_player]["$$$"]))
 
        # if the player has no properties, they immediately get eliminated
        else:
            print()
            print("    ╔════════════════════════════════════════════════════════════════╗")
            print("    ║                                                                ║")
            print(f"    ║                     PLAYER {_player} ELIMINATED :(                     ║")
            print("    ║                                                                ║")
            print("    ║                  you cannot repay your debts,                  ║")
            print("    ║            so you are bankrupt and out of the game.            ║")
            print("    ║                                                                ║")
            print("    ║    Now's a great opportunity to go outside and touch grass!    ║")
            print("    ║                                                                ║")
            print("    ║                             [enter]                            ║")
            print("    ╚════════════════════════════════════════════════════════════════╝")
            print("\n    ", end = "")
            self.action = "whump whump"

            # actions on info after user notified
            self.bankruptcy_details = [_player, cause]

    def input_management(self, user_input):
        if self.action == "whump whump":
            
            # updates the player's status to "bankrupt" and removes them from play
            state.player[self.bankruptcy_details[0]]["status"] = "bankrupt"
            bankruptcy(*self.bankruptcy_details)


class refresh_board_class(utils.parent_class):
    """displays the game board"""
    def __init__(self):
        self.money_structure = better_iter(["outer", "top_info", "bottom_info"], True)
        self.action = None
        self.passed_go_art = [
            r"✨    \¯\/¯/ /¯¯\  |¯||¯|    |¯¯¯\  /¯\   /¯⁐⁐| /¯⁐⁐| |¯¯¯| |¯¯¯\      /¯¯¯|   /¯¯\    ✨  ",
            r"   ✨  \  / | () | | || |    | ⁐_/ / ^ \  \__ \ \__ \ | ⁐|_ | [) |    | (⁐¯¯| | () | ✨     ",
            r" ✨    /_/   \__/   \__/     |_|  /_/¯\_\ |___/ |___/ |___| |___/      \___/   \__/      ✨",
        ]
        self.passed_go = False
        self.player_turn_display = [[] for i in range(5)]
        self.prev_cash = [0, 0, 0, 0]

        # art displaying the current turn
        self.player_turn_display[1] = [" ___    ", "/__ |   ", " _| |_  ", "|_____| "]
        self.player_turn_display[2] = [" _----_ ", "/__/  / ", " /  /___", "|______|"]
        self.player_turn_display[3] = [" ______ ", "|____  \\", " |___ ⟨⁐", "|______/"]
        self.player_turn_display[4] = ["__  __  ", "| || |_ ", "|___  _|", "   |_|  "]

    def __call__(self):

        def display_money(position: int, alt_position: int | None = 0):
            """
            displays a player's money if one exists at the position.
            The player currently playing has a border around them.

            alt_position should always be the bigger number.
            """
            def top_info():

                # form the borders surrounding the player if it's their turn
                outer = " "
                if player_check == turn_spot: outer = "│"

                return f"{outer} player {turn_spot} | {state.player[turn_spot]['char']} {outer}"

            def bottom_info():
                outer = extra_space = extra_extra_space = output = ""

                if player_check == turn_spot: outer = "│"
                else: outer = " "

                if state.player[turn_spot]["status"] in ("playing", "jail"):
                    for i in range(12 - len(str(state.player[turn_spot]["$$$"]))):
                        extra_space += " "

                    output =  f"{outer} ${state.player[turn_spot]['$$$']}{extra_space} {outer}"

                # displays the player's status if not playing
                else:
                    for i in range((11 - len(state.player[turn_spot]["status"])) // 2):
                        extra_space += " "
                    if len(state.player[turn_spot]["status"]) % 2 == 1:
                        extra_extra_space = " "

                    output = f"{outer}{extra_space} = {state.player[turn_spot]["status"].upper()} ={extra_extra_space}{extra_space}{outer}"
                return output

            def outer():
                if   player_check == state.players_playing - (position - 1)    : return "┌───────────────┐"
                elif player_check == state.players_playing - (alt_position - 1): return "└───────────────┘"
                else                                                    : return "                 "

            # outlines playing player if online, as opposed to current player
            if state.online_config.game_strt_event.is_set():
                player_check = state.online_config.player_num
            else:
                player_check = state.player_turn

            output = "                 " # 17 spaces
            turn_spot = state.players_playing - (position - 1)

            # check if there is a player to display at this location
            if position <= state.players_playing: output = locals()[next(self.money_structure)]()
            return output

        def houses(i: int):
            """returns the number of houses the property has"""
            space = lambda: '' if state.property_data[i]["street value"] >= 100 else ' '

            match state.property_data[i]["upgrade state"] - 2:
                case 1: return "    🏠    "
                case 2: return "  🏠  🏠  "
                case 3: return "🏠  🏠  🏠"
                case 4: return "🏠 🏠🏠 🏠"
                case 5: return "    🏨    "
                case _: return f"   ${space()}{state.property_data[i]["street value"]}   "

        def money_change(position: int):
            if position > state.players_playing:
                return "       "

            output = ""
            change = state.player[state.players_playing - (position - 1)]["$$$"] \
                - self.prev_cash[state.players_playing - position]
            
            if change == 0: return "       " # no change = nothing to display
            elif change < 0: output += "\x1b[31m- " # red text
            else: output += "\x1b[32m+ " # green text
            
            for _ in range(4 - len(str(abs(change)))): output += " " # ensures 7 chars length
            
            output += f"${str(abs(change))}\x1b[0m" # adds value; clears colour change
            return output
            
        def online_name(position: int):
            if not state.online_config.game_strt_event.is_set() or position > state.players_playing:
                return "                    "

            if state.online_config.socket_type == "client":
                name = state.online_config.joined_clients[0][state.players_playing - position]
            else:
                clients = [item[0] for item in state.online_config.joined_clients]               
                clients.insert(0, state.online_config.display_name)
                name = clients[state.players_playing - position]
                
            
            extra_space = ""
            for i in range(20 - len(name)):
                extra_space += " "
            return f"{extra_space}{name}"

        # money structure otherwise starts at index 1 from previous use
        self.money_structure.index = -1

        # displays the player whom owns the property if exists
        icon = lambda i: state.player[state.property_data[i]["owner"]]["char"] if state.property_data[i]["owner"] else "  "

        state.current_screen = self.__name__
        clear_screen()

        # once player finishes roll, updates player turn player 
        if state.online_config.game_strt_event.is_set() and state.player_action.dice_rolled and state.refresh_board.action == None:
            _list = [item[1]["$$$"] for item in state.player.items()]

            send_data(f"turnfinished:{state.player[state.player_turn]['pos']}:{_list}")
            state.refresh_board.end_turn_logic()

        # It'll all display fine in terminal, don't worry
        print("")
        print("     ▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁")
        print(f"    \x1b[7m▊\x1b[0m▛               ▎{houses(14)}▎  __()_   ▎{houses(15)}▎{houses(16)}\x1b[0m▎   $200 __\x1b[7m▊\x1b[0m{houses(18)}\x1b[7m▊\x1b[0m{houses(19)}▎   $150   \x1b[7m▊\x1b[0m{houses(21)}\x1b[7m▊\x1b[0m   GO TO JAIL  ▜▎")
        print(f"    \x1b[7m▊\x1b[0m  FREE PARKING  ▎          ▎  \\__ \\   ▎          ▎          \x1b[0m▎_()_()_| /\x1b[7m▊\x1b[0m          \x1b[7m▊\x1b[0m          ▎{state.player_display[28][0]}\x1b[7m▊\x1b[0m          \x1b[7m▊\x1b[0m     {state.player_display[30][0]} ▎")
        print(f"    \x1b[7m▊\x1b[0m      ____      ▎{state.player_display[21][0]}▎{state.player_display[22][0]}▎{state.player_display[23][0]}▎{state.player_display[24][0]}\x1b[0m▎\\  ____ _)\x1b[7m▊\x1b[0m{state.player_display[26][0]}\x1b[7m▊\x1b[0m{state.player_display[27][0]}▎    /\\    \x1b[7m▊\x1b[0m{state.player_display[29][0]}\x1b[7m▊\x1b[0m  /¯¯¯¯\\        ▎")
        print("    \x1b[7m▊\x1b[0m     /[__]\\     ▎          ▎  / /  /\\ ▎          ▎          \x1b[0m▎/__)  /_\\ \x1b[7m▊\x1b[0m          \x1b[7m▊\x1b[0m          ▎   /  \\   \x1b[7m▊\x1b[0m          \x1b[7m▊\x1b[0m | (¯¯)/¯¯¯¯\\   ▎")
        print(f"    \x1b[7m▊\x1b[0m    |_ () _|    ▎          ▎  \\ ‾-‾ / ▎  Fleet   ▎Trafalgar ▎{state.player_display[25][0]}\x1b[7m▊\x1b[0mLeicester \x1b[7m▊\x1b[0m Coventry ▎  |    |  \x1b[7m▊\x1b[0m          \x1b[7m▊\x1b[0m  \\_¯¯| (¯¯) |  ▎")
        print("    \x1b[7m▊\x1b[0m     U----U     ▎  Strand  ▎   ‾---‾  ▎  Street  ▎  Square  \x1b[0m▎Fenchurch \x1b[7m▊\x1b[0m  Square  \x1b[7m▊\x1b[0m  Street  ▎   \\__/   \x1b[7m▊\x1b[0mPiccadilly\x1b[7m▊\x1b[0m    \\/ \\_¯¯_/   ▎")
        print(f"    \x1b[7m▊\x1b[0m   {state.player_display[20][0]}   \x1b[48;2;248;49;47m▎          \x1b[0m▎  CHANCE  \x1b[48;2;248;49;47m▎          ▎          \x1b[0m▎ Station  \x1b[7m▊\x1b[0m\x1b[48;2;255;176;46m          \x1b[30m\x1b[7m▊\x1b[0m\x1b[48;2;255;176;46m          \x1b[0m▎WaterWorks\x1b[7m▊\x1b[0m\x1b[48;2;255;176;46m          \x1b[7m▊\x1b[0m     O   \\/     ▎")
        print("    \x1b[7m▊\x1b[0m                \x1b[48;2;248;49;47m▎          \x1b[0m▎          \x1b[48;2;248;49;47m▎          ▎          \x1b[0m▎          \x1b[7m▊\x1b[0m\x1b[48;2;255;176;46m          \x1b[30m\x1b[7m▊\x1b[0m\x1b[48;2;255;176;46m          \x1b[0m▎          \x1b[7m▊\x1b[0m\x1b[48;2;255;176;46m          \x1b[7m▊\x1b[0m      O O       ▎")
        print("    \x1b[7m▊\x1b[0m▔▔▔▔▔▔▔▔▔▔▔▔\x1b[48;2;255;103;35m▔▔▔▔\x1b[0m▛▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▜\x1b[48;2;0;210;106m▔▔▔▔\x1b[0m▔▔▔▔▔▔▔▔▔▔▔▔▎")
        print(f"    \x1b[7m▊\x1b[0mVine Street \x1b[48;2;255;103;35m    \x1b[0m▎    {icon(14)}                    {icon(15)}         {icon(16)}         {icon(17)}         {icon(18)}         {icon(19)}         {icon(20)}         {icon(21)}    \x1b[7m▊\x1b[0m\x1b[48;2;0;210;106m    \x1b[0m Regent St. ▎")
        print(f"    \x1b[7m▊\x1b[0m {houses(13)} \x1b[48;2;255;103;35m    \x1b[0m▎ {icon(13)}  _____     __          ___    ___  ___   ______     ______       {self.player_turn_display[state.player_turn][0]}                  {icon(22)} \x1b[7m▊\x1b[0m\x1b[48;2;0;210;106m    \x1b[0m {houses(22)} ▎")
        print(f"    \x1b[7m▊\x1b[0m {state.player_display[19][0]} \x1b[48;2;255;103;35m    \x1b[0m▎    |  _  \\   |  |        /   \\   \\  \\/  /  |  ____|   |  __  \\      {self.player_turn_display[state.player_turn][1]}                     \x1b[7m▊\x1b[0m\x1b[48;2;0;210;106m    \x1b[0m {state.player_display[31][0]} ▎")
        print(f"    \x1b[7m▊\x1b[0m▁▁▁▁▁▁▁▁▁▁▁▁\x1b[48;2;255;103;35m▁▁▁▁\x1b[0m▎    |  ___/   |  |__     /  ^  \\   \\_  _/   |  __|_    |      /      {self.player_turn_display[state.player_turn][2]}                     \x1b[7m▊\x1b[0m\x1b[48;2;0;210;106m\x1b[30m▁▁▁▁\x1b[0m▁▁▁▁▁▁▁▁▁▁▁▁▎")
        print(f"    \x1b[7m▊\x1b[0mMarlborough \x1b[48;2;255;103;35m    \x1b[0m▎    |__|      |_____|   /__/¯\\__\\   |__|    |______|   |__|\\__\\      {self.player_turn_display[state.player_turn][3]}                     \x1b[7m▊\x1b[0m\x1b[48;2;0;210;106m    \x1b[0m            ▎")
        print("    \x1b[7m▊\x1b[0m   Street   \x1b[48;2;255;103;35m    \x1b[0m▎                                                                                                  \x1b[7m▊\x1b[0m\x1b[48;2;0;210;106m    \x1b[0m Oxford St. ▎")
        print(f"    \x1b[7m▊\x1b[0m {houses(12)} \x1b[48;2;255;103;35m    \x1b[0m▎ {icon(12)}   ____       _____      __                                                                 {icon(23)} \x1b[7m▊\x1b[0m\x1b[48;2;0;210;106m    \x1b[0m {houses(23)} ▎")
        print(f"    \x1b[7m▊\x1b[0m {state.player_display[18][0]} \x1b[48;2;255;103;35m    \x1b[0m▎     /  __|     /     \\    |  |                                                                   \x1b[7m▊\x1b[0m\x1b[48;2;0;210;106m    \x1b[0m {state.player_display[32][0]} ▎")
        print("    \x1b[7m▊\x1b[0m▁▁▁▁▁▁▁▁▁▁▁▁\x1b[48;2;255;103;35m▁▁▁▁\x1b[0m▎    |  |_  |   |  (_)  |   |__|                                                                   \x1b[7m▊\x1b[0m\x1b[48;2;0;210;106m▁▁▁▁\x1b[0m▁▁▁▁▁▁▁▁▁▁▁▁▎")
        print("    \x1b[7m▊\x1b[0m COMUNITY CHEST ▎     \\____/     \\_____/    (__)                                                                   \x1b[7m▊\x1b[0m COMUNITY CHEST ▎")
        print(f"    \x1b[7m▊\x1b[0m   {state.player_display[17][0]}   ▎                                                                                                  \x1b[7m▊\x1b[0m   {state.player_display[33][0]}   ▎")
    
        button_states = [False, True, False, True]

        # checks if the players owns any properties, button is 'trade' otherwise
        x = better_iter(state.property_data)
        prompt_2 = "Trade"
        while prompt_2 == "Trade":
            try:
                check_prop = next(x)

            # if all properties have been checked, loop is broken
            except tripple_affirmative:
                break

            # if player has properties, the prompt is changed and loop broken
            if check_prop["owner"] == state.player_turn: 
                prompt_2 = "Properties"
                break

        # additional logic is required for online
        online_check = lambda: True if (state.online_config.player_num == state.player_turn or not state.online_config.game_strt_event.is_set()) else False

        # similar checks are performed for the other prompts
        # if the player has spent 3 turns in jail, they MUST pay bail, regardless of conditions
        button_states[0] = (online_check() and state.player_action.dice_rolled == False \
            and self.action == None and state.player[state.player_turn]["jail time"] < 3)

        if (self.action == None and state.player_action.dice_rolled == True) or \
                (state.online_config.game_strt_event.is_set() and state.online_config.socket_type == "host"):
            button_states[2] = True

        if state.online_config.game_strt_event.is_set():
            if state.online_config.socket_type == "client":
                prompt_3 = ""
            else:
                prompt_3 = "kick user"
        else: prompt_3 = "End turn"

        button_list = create_button_prompts(["Roll dice", prompt_2, prompt_3, "Save & Exit"], button_states, [0, 3, 3, 6])

        print(f"    \x1b[7m▊\x1b[0m  💰  💵  🪙    ▎    {button_list[0]}          \x1b[7m▊\x1b[0m  💰  💵  🪙    ▎")
        print(f"    \x1b[7m▊\x1b[0m💵  🪙  💰  💵  ▎    {button_list[1]}          \x1b[7m▊\x1b[0m💵  🪙  💰  💵  ▎")
        print(f"    \x1b[7m▊\x1b[0m▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▎    {button_list[2]}          \x1b[7m▊\x1b[0m▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▎")
        print(f"    \x1b[7m▊\x1b[0m            \x1b[48;2;255;103;35m    \x1b[0m▎    {button_list[3]}          \x1b[7m▊\x1b[0m\x1b[48;2;0;210;106m    \x1b[0m            ▎")
        print("    \x1b[7m▊\x1b[0m Bow Street \x1b[48;2;255;103;35m    \x1b[0m▎                                                                                                  \x1b[7m▊\x1b[0m\x1b[48;2;0;210;106m    \x1b[0m  Bond St.  ▎")
    
        button_states = [["", ""],[True, True]]

        if self.action == "property":
            button_states[0] = ["Buy property", "Auction"]
            if state.player[state.player_turn]["$$$"] < state.property_data[state.prop_from_pos[state.player[state.player_turn]["pos"]]]["street value"]: button_states[1][1] = False

        elif state.player[state.player_turn]["status"] == "jail":
            button_states[0] = ["Give bail $", "Use card"]
         
            if state.player[state.player_turn]["$$$"] < 50        : button_states[1][0] = False
            if state.player[state.player_turn]["jail passes"] == 0: button_states[1][1] = False
        button_list = create_button_prompts(button_states[0], button_states[1], [0, 3])

        print(f"    \x1b[7m▊\x1b[0m {houses(11)} \x1b[48;2;255;103;35m    \x1b[0m▎ {icon(11)} {button_list[0]}                                                    {icon(24)} \x1b[7m▊\x1b[0m\x1b[48;2;0;210;106m    \x1b[0m {houses(24)} ▎")
        print(f"    \x1b[7m▊\x1b[0m {state.player_display[16][0]} \x1b[48;2;255;103;35m    \x1b[0m▎    {button_list[1]}                                                       \x1b[7m▊\x1b[0m\x1b[48;2;0;210;106m    \x1b[0m {state.player_display[34][0]} ▎")
        print(f"    \x1b[7m▊\x1b[0m▁▁▁▁▁▁▁▁▁▁▁▁\x1b[48;2;255;103;35m▁▁▁▁\x1b[0m▎    {button_list[2]}                                                       \x1b[7m▊\x1b[0m\x1b[48;2;0;210;106m▁▁▁▁\x1b[0m▁▁▁▁▁▁▁▁▁▁▁▁▎")
        print(f"    \x1b[7m▊\x1b[0m |\\⁔ Marylebone ▎    {button_list[3]}                                                       \x1b[7m▊\x1b[0m Liverpool|∖↙() ▎")
        print("    \x1b[7m▊\x1b[0m ¯| |◁ Station  ▎                                                                                                  \x1b[7m▊\x1b[0m Station  |‿ |  ▎")
        print(f"    \x1b[7m▊\x1b[0m () |  $200     ▎ {icon(10)}                                                                                            {icon(25)} \x1b[7m▊\x1b[0m $200      | () ▎")
        print(f"    \x1b[7m▊\x1b[0m  | ⁀|{state.player_display[15][0]}▎                                                                                                  \x1b[7m▊\x1b[0m{state.player_display[35][0]}▷|‿|_ ▎")
        print("    \x1b[7m▊\x1b[0m▁()↗∖|▁▁▁▁▁▁▁▁▁▁▎                                                                                                  \x1b[7m▊\x1b[0m▁▁▁▁▁▁▁▁▁▁▁▁▁\\|▁▎")
        print("    \x1b[7m▊\x1b[0mNorthumb'nd \x1b[48;2;245;47;171m    \x1b[0m▎                                                                                                  \x1b[7m▊\x1b[0m      _  CHANCE ▎")
        print("    \x1b[7m▊\x1b[0m   Avenue   \x1b[48;2;245;47;171m    \x1b[0m▎                                                                                                  \x1b[7m▊\x1b[0m    /‾_‾\\|‾|    ▎")
        print(f"    \x1b[7m▊\x1b[0m {houses(9)} \x1b[48;2;245;47;171m    \x1b[0m▎ {icon(9)}                                                                                               \x1b[7m▊\x1b[0m   | | \\_  | () ▎")
        print(f"    \x1b[7m▊\x1b[0m {state.player_display[14][0]} \x1b[48;2;245;47;171m    \x1b[0m▎                                                                                                  \x1b[7m▊\x1b[0m    \\_\\{state.player_display[36][0]}▎")
        print("    \x1b[7m▊\x1b[0m▁▁▁▁▁▁▁▁▁▁▁▁\x1b[48;2;245;47;171m▁▁▁▁\x1b[0m▎                                                                                                  \x1b[7m▊\x1b[0m▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▎")
  
        # ensures that floats aren't shown due to my bad code
        for player_ in state.player.items(): player_[1]["$$$"] = int(player_[1]["$$$"])
        
        print(f"    \x1b[7m▊\x1b[0m            \x1b[48;2;245;47;171m    \x1b[0m▎                                                                             {display_money(4)}    \x1b[7m▊\x1b[0m\x1b[48;2;28;89;255m    \x1b[0m            ▎")
        print(f"    \x1b[7m▊\x1b[0m Whitehall  \x1b[48;2;245;47;171m    \x1b[0m▎                                                        {online_name(4)} {display_money(4)}    \x1b[7m▊\x1b[0m\x1b[48;2;28;89;255m    \x1b[0m Park Lane  ▎")    
        print(f"    \x1b[7m▊\x1b[0m {houses(8)} \x1b[48;2;245;47;171m    \x1b[0m▎ {icon(8)}                                                                  {money_change(4)} {display_money(4)} {icon(26)} \x1b[7m▊\x1b[0m\x1b[48;2;28;89;255m    \x1b[0m {houses(26)} ▎")
        print(f"    \x1b[7m▊\x1b[0m {state.player_display[13][0]} \x1b[48;2;245;47;171m    \x1b[0m▎                                                                             {display_money(3, 4)}    \x1b[7m▊\x1b[0m\x1b[48;2;28;89;255m    \x1b[0m {state.player_display[37][0]} ▎")
        print(f"    \x1b[7m▊\x1b[0m▁▁▁▁▁▁▁▁▁▁▁▁\x1b[48;2;245;47;171m▁▁▁▁\x1b[0m▎                                                        {online_name(3)} {display_money(3)}    \x1b[7m▊\x1b[0m\x1b[48;2;28;89;255m▁▁▁▁\x1b[0m▁▁▁▁▁▁▁▁▁▁▁▁▎")
        print(f"    \x1b[7m▊\x1b[0m Electric Co.   ▎                                                                     {money_change(3)} {display_money(3)}    \x1b[7m▊\x1b[0m ∖  ⁄ SUPER TAX ▎")
        print(f"    \x1b[7m▊\x1b[0m $150       |\\  ▎                                                                             {display_money(2, 3)}    \x1b[7m▊\x1b[0m- 💎 -     $100 ▎")
        print(f"    \x1b[7m▊\x1b[0m          __| \\ ▎ {icon(7)}                                                     {online_name(2)} {display_money(2)}    \x1b[7m▊\x1b[0m/¯¯¯¯\\{state.player_display[38][0]}▎")
        print(f"    \x1b[7m▊\x1b[0m{state.player_display[12][0]}\\ |¯¯ ▎                                                                     {money_change(2)} {display_money(2)}    \x1b[7m▊\x1b[0m (⁐⁐) |         ▎")   
        print(f"    \x1b[7m▊\x1b[0m           \\|   ▎                                                                             {display_money(1, 2)}    \x1b[7m▊\x1b[0m\\____/\x1b[0m          ▎")
        print(f"    \x1b[7m▊\x1b[0m▔▔▔▔▔▔▔▔▔▔▔▔\x1b[48;2;245;47;171m▔▔▔▔\x1b[0m▎                                                        {online_name(1)} {display_money(1)}    \x1b[7m▊\x1b[0m\x1b[48;2;28;89;255m▔▔▔▔\x1b[0m▔▔▔▔▔▔▔▔▔▔▔▔▎")
        print(f"    \x1b[7m▊\x1b[0m Pall Mall  \x1b[48;2;245;47;171m    \x1b[0m▎                                                                     {money_change(1)} {display_money(1)}    \x1b[7m▊\x1b[0m\x1b[48;2;28;89;255m    \x1b[0m   Mayfair  ▎")
        print(f"    \x1b[7m▊\x1b[0m {houses(6)} \x1b[48;2;245;47;171m    \x1b[0m▎ {icon(6)}                                                                          {display_money(0, 1)} {icon(27)} \x1b[7m▊\x1b[0m\x1b[48;2;28;89;255m    \x1b[0m {houses(27)} ▎")
        print(f"    \x1b[7m▊\x1b[0m {state.player_display[11][0]} \x1b[48;2;245;47;171m    \x1b[0m▎    {icon(5)}         {icon(4)}                    {icon(3)}         {icon(2)}                    {icon(1)}                    {icon(0)}    \x1b[7m▊\x1b[0m\x1b[48;2;28;89;255m    \x1b[0m {state.player_display[39][0]} ▎")
        print("    \x1b[7m▊\x1b[0m▁▁▁▁▁▁▁▁▁▁▁▁\x1b[48;2;245;47;171m▁▁▁▁\x1b[0m▙▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▟\x1b[0m\x1b[48;2;28;89;255m▁▁▁▁\x1b[0m▁▁▁▁▁▁▁▁▁▁▁▁▎")
        print(f"    \x1b[7m▊\x1b[0m      │ ║ ║ ║ ║ \x1b[48;2;0;166;237m▎          \x1b[30m│          \x1b[0m▎  CHANCE  \x1b[48;2;0;166;237m▎          \x1b[0m▎  King's  ▎          \x1b[48;2;165;105;83m▎          \x1b[0m▎ COMUNITY \x1b[7m▊\x1b[0m\x1b[48;2;165;105;83m          \x1b[7m▊\x1b[0m  ____    ____  ▎")
        print(f"    \x1b[7m▊\x1b[0m   J  │ J A I L \x1b[48;2;0;166;237m▎          \x1b[30m│          \x1b[0m▎  _---_   \x1b[48;2;0;166;237m▎          \x1b[0m▎  Cross   ▎  INCOME  \x1b[48;2;165;105;83m▎          \x1b[0m▎   CHEST  \x1b[7m▊\x1b[0m\x1b[48;2;165;105;83m          \x1b[7m▊\x1b[0m /  __|  /    \\ ▎")
        print(f"    \x1b[7m▊\x1b[0m   U  │ ║ ║ ║ ║ ▎Pent'ville│  Euston  ▎ / _-_ \\  ▎The Angel ▎{state.player_display[5][0]}▎   TAX    ▎whitechp'l▎{state.player_display[2][0]}\x1b[7m▊\x1b[0m Old Kent \x1b[0m\x1b[7m▊\x1b[0m|  |_ ‾||  ()  |▎")
        print(f"    \x1b[7m▊\x1b[0m   S  │{state.player_display[40][0]}▎   Road   │   Road   ▎ \\/  / /  ▎Islington ▎ \\¯/___(¯/▎          ▎   Road   ▎          \x1b[7m▊\x1b[0m   Road   \x1b[7m▊\x1b[0m \\____/  \\____/ ▎")
        print(f"    \x1b[7m▊\x1b[0m   T  │_║_║_║_║_▎          │          ▎   / /_   ▎          ▎( _______\\▎    🔷    ▎          ▎🪙  💰  💵\x1b[7m▊\x1b[0m          \x1b[0m\x1b[7m▊\x1b[0m{state.player_display[0][0]}____  ▎")
        print(f"    \x1b[7m▊\x1b[0m   {state.player_display[10][0]}   ▎{state.player_display[9][0]}│{state.player_display[8][0]}▎   \\___\\  ▎{state.player_display[6][0]}▎/_| () () ▎{state.player_display[4][0]}▎{state.player_display[3][0]}▎  💵  💰  \x1b[7m▊\x1b[0m{state.player_display[1][0]}\x1b[7m▊\x1b[0m  /|-----/   /  ▎")
        print(f"    \x1b[7m▊\x1b[0m    VISITING    ▎{houses(5)}│{houses(4)}▎{state.player_display[7][0]}▎{houses(3)}▎{houses(2)}▎ PAY $200 ▎{houses(1)}▎💰  🪙  💵\x1b[7m▊\x1b[0m{houses(1)}\x1b[7m▊\x1b[0m  \\|-----\\___\\  ▎")
        print("    \x1b[7m▊\x1b[0m▙               ▎          │          ▎          ▎          ▎          ▎          ▎          ▎          \x1b[7m▊\x1b[0m          \x1b[0m\x1b[7m▊\x1b[0m               ▟▎")
        print("     ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔ ")

        # devmode commands are listed here
        if state.dev_mode == True:
            print("    === devmode commands ===")
            print()
            print("    \"setplayerpos\"")
            print("    \"editplayerdict\"")
            print("    \"showplayerdict\"")
            print("    \"setdiceroll\"")
            print("    \"bankruptcy\"")
            print("    \"propertybid\"")
            print("    \"showproplist\"")
            print("    \"showchangedprops\"")
            print("    \"setplayerprops\"")
            print("    \"forcechancecard\"")
            print("    \"forcecccard\"")
            print("    \"displayvar\"")
            print("    \"queuechance\"")
            print("    \"queuecc\"")
            print("    \"arbitrarycode\"")
            print("    \"setbidqueue\"")
            print("    \"dumpsave\"")
            print()
        
        if self.passed_go == True:
            for line in self.passed_go_art: print(f"    {line}")
            print()
            self.passed_go = False

        print("    ", end="")

        for item in state.player.items():
            self.prev_cash[item[0] - 1] = item[1]["$$$"]

        return
        print("    ┌─────────────────┬──────────┬──────────┬──────────┬──────────┬──────────┬──────────┬──────────┬──────────┬──────────┬─────────────────┐")
        print("    │                 │          │\x1b[38;2;255;103;35m    ()    \x1b[0m│          │          │   $200 __│          │          │\x1b[94m    /\\    \x1b[0m│          │   GO TO JAIL!   │")
        print("    │  FREE  PARKING  │          │\x1b[38;2;255;103;35m  /‾‾‾\\   \x1b[0m│          │          │_()_()_| /│          │          │\x1b[94m   /  \\   \x1b[0m│          │                 │")
        print("    │                 │          │\x1b[38;2;20;186;237m  ‾‾/ /   \x1b[0m│          │          │\\  ____ _)│          │          │\x1b[94m__/_ \\ \\  \x1b[0m│          │   /¯¯¯¯\\        │")
        print("    │      _____      │          │\x1b[38;2;20;186;237m  /‾ /    \x1b[0m│          │          │/__)  /_\\ │          │          │$150\x1b[94m| | | \x1b[0m│          │  | (¯¯)/¯¯¯¯\\   │")
        print("    │     /[___]\\     │          │\x1b[38;2;245;77;201m / /‾  /\\ \x1b[0m│          │Trafalgar │          │Leicester │ Coventry │\x1b[94m‾|‾‾  / | \x1b[0m│          │   \\_¯¯| (¯¯) |  │")
        print("    │    |_ (·) _|    │  Strand  │\x1b[38;2;245;77;201m \\ ‾--‾ / \x1b[0m│ Fleet St.│  Square  │Fenchurch │  Square  │  Street  │\x1b[94m  \\____/  \x1b[0m│Piccadilly│     \\/ \\_¯¯_/   │")
        print("    │     U-----U     \x1b[48;2;130;29;30m│\x1b[48;2;248;49;47m          \x1b[48;2;130;29;30m│\x1b[0m\x1b[38;2;245;77;201m  ‾----‾  \x1b[0m\x1b[48;2;130;29;30m│\x1b[48;2;248;49;47m          │          \x1b[48;2;130;29;30m│\x1b[0m Station  \x1b[48;2;134;94;29m│\x1b[48;2;255;176;46m          \x1b[30m│\x1b[48;2;255;176;46m          \x1b[39m\x1b[48;2;134;94;29m│\x1b[0m Water    \x1b[48;2;134;94;29m│\x1b[48;2;255;176;46m          \x1b[48;2;134;94;29m│\x1b[0m      O   \\/     │")
        print("    │                 \x1b[48;2;130;29;30m│\x1b[48;2;248;49;47m          \x1b[48;2;130;29;30m│\x1b[0m  CHANCE  \x1b[48;2;130;29;30m│\x1b[48;2;248;49;47m          │          \x1b[48;2;130;29;30m│\x1b[0m          \x1b[48;2;134;94;29m│\x1b[48;2;255;176;46m          \x1b[30m│\x1b[48;2;255;176;46m          \x1b[39m\x1b[48;2;134;94;29m│\x1b[0m    Works \x1b[48;2;134;94;29m│\x1b[48;2;255;176;46m          \x1b[48;2;134;94;29m│\x1b[0m       O O       │")
        print("    ├─────────────\x1b[48;2;134;58;14m────\x1b[0m┼\x1b[48;2;130;29;30m──────────\x1b[0m┴──────────┴\x1b[48;2;130;29;30m──────────\x1b[0m┴\x1b[48;2;130;29;30m──────────\x1b[0m┴──────────┴\x1b[48;2;134;94;29m──────────\x1b[0m┴\x1b[48;2;134;94;29m──────────\x1b[0m┴──────────┴\x1b[48;2;134;94;29m──────────\x1b[0m┼\x1b[48;2;6;111;59m────\x1b[0m─────────────┤")
        print("    │ Vine Street \x1b[48;2;255;103;35m    \x1b[48;2;134;58;14m│ \x1b[0m                                                                                                \x1b[48;2;6;111;59m │\x1b[48;2;0;210;106m    \x1b[0m Regent St.  │")
        print("    │             \x1b[48;2;255;103;35m    \x1b[48;2;134;58;14m│ \x1b[0m                                                                                                \x1b[48;2;6;111;59m │\x1b[48;2;0;210;106m    \x1b[0m             │")
        print("    │             \x1b[48;2;255;103;35m    \x1b[48;2;134;58;14m│ \x1b[0m                                                                                                \x1b[48;2;6;111;59m │\x1b[48;2;0;210;106m    \x1b[0m             │")
        print("    │             \x1b[48;2;255;103;35m    \x1b[48;2;134;58;14m│ \x1b[0m                                                                                                \x1b[48;2;6;111;59m │\x1b[48;2;0;210;106m    \x1b[0m             │")
        print("    ├─────────────\x1b[48;2;255;103;35m────\x1b[0m┤                                                                                                  ├\x1b[48;2;0;210;106m────\x1b[0m─────────────┤")
        print("    │ Marlborough \x1b[48;2;255;103;35m    \x1b[48;2;134;58;14m│ \x1b[0m                                                                                                \x1b[48;2;6;111;59m │\x1b[48;2;0;210;106m    \x1b[0m Oxford St.  │")
        print("    │ Street      \x1b[48;2;255;103;35m    \x1b[48;2;134;58;14m│ \x1b[0m                                                                                                \x1b[48;2;6;111;59m │\x1b[48;2;0;210;106m    \x1b[0m             │")
        print("    │             \x1b[48;2;255;103;35m    \x1b[48;2;134;58;14m│ \x1b[0m                                                                                                \x1b[48;2;6;111;59m │\x1b[48;2;0;210;106m    \x1b[0m             │")
        print("    │             \x1b[48;2;255;103;35m    \x1b[48;2;134;58;14m│ \x1b[0m                                                                                                \x1b[48;2;6;111;59m │\x1b[48;2;0;210;106m    \x1b[0m             │")
        print("    ├───\x1b[33m┌┐\x1b[0m────────\x1b[48;2;134;58;14m────\x1b[0m┤                                                                                                  ├\x1b[48;2;6;111;59m────\x1b[0m────────\x1b[33m┌┐\x1b[0m───┤")
        print("    │/‾⁐\x1b[33m││\x1b[0m‾‾|COMMUNITY│                                                                                                  │COMMUNITY/‾⁐\x1b[33m││\x1b[0m‾‾|│")
        print("    │\\__\x1b[33m││\x1b[0m‾‾    CHEST │                                                                                                  │ CHEST   \\__\x1b[33m││\x1b[0m‾‾ │")
        print("    │ __\x1b[33m││\x1b[0m⁐‾\\         │                                                                                                  │          __\x1b[33m││\x1b[0m⁐‾\\│")
        print("    │|__\x1b[33m││\x1b[0m__/         │                                                                                                  │         |__\x1b[33m││\x1b[0m__/│")
        print("    ├───\x1b[33m└┘\x1b[0m────────\x1b[48;2;134;58;14m────\x1b[0m┤                                                                                                  ├\x1b[48;2;6;111;59m────\x1b[0m────────\x1b[33m└┘\x1b[0m───┤")
        print("    │ Bow Street  \x1b[48;2;255;103;35m    \x1b[48;2;134;58;14m│ \x1b[0m                                                                                                \x1b[48;2;6;111;59m │\x1b[48;2;0;210;106m    \x1b[0m Bond St.    │")
        print("    │             \x1b[48;2;255;103;35m    \x1b[48;2;134;58;14m│ \x1b[0m                                                                                                \x1b[48;2;6;111;59m │\x1b[48;2;0;210;106m    \x1b[0m             │")
        print("    │             \x1b[48;2;255;103;35m    \x1b[48;2;134;58;14m│ \x1b[0m                                                                                                \x1b[48;2;6;111;59m │\x1b[48;2;0;210;106m    \x1b[0m             │")
        print("    │             \x1b[48;2;255;103;35m    \x1b[48;2;134;58;14m│ \x1b[0m                                                                                                \x1b[48;2;6;111;59m │\x1b[48;2;0;210;106m    \x1b[0m             │")
        print("    ├─────────────\x1b[48;2;134;58;14m────\x1b[0m┤                                                                                                  ├\x1b[48;2;6;111;59m────\x1b[0m─────────────┤")
        print("    │ |\\⁔  Marylebone │                                                                                                  │ Liverpool |∖↙() │")
        print("    │ ¯| |◁   Station │                                                                                                  │ Station   |‿ |  │")
        print("    │ () |       $200 │                                                                                                  │ $200       | () │")
        print("    │  | ⁀|           │                                                                                                  │           ▷|‿|_ │")
        print("    ├─()↗∖|───────\x1b[48;2;129;30;92m────\x1b[0m┤                                                                                                  ├──────────────\\|─┤")
        print("    │ Northumb'nd \x1b[48;2;245;47;171m    \x1b[48;2;129;30;92m│ \x1b[0m                                                                                                 │\x1b[38;2;245;77;201m    __\x1b[0m    CHANCE │")
        print("    │ Avenue      \x1b[48;2;245;47;171m    \x1b[48;2;129;30;92m│ \x1b[0m                                                                                                 │\x1b[38;2;245;77;201m  /‾  ‾\x1b[38;2;20;186;237m\\  \x1b[38;2;255;103;35m┌─┐    \x1b[0m│")
        print("    │             \x1b[48;2;245;47;171m    \x1b[48;2;129;30;92m│ \x1b[0m                                                                                                 │\x1b[38;2;245;77;201m | (‾‾\x1b[38;2;20;186;237m\\ \\_\x1b[38;2;255;103;35m/ | () \x1b[0m│")
        print("    │             \x1b[48;2;245;47;171m    \x1b[48;2;129;30;92m│ \x1b[0m                                                                                                 │\x1b[38;2;245;77;201m  \\_\\\x1b[38;2;20;186;237m  \\__\x1b[38;2;255;103;35m_/     \x1b[0m│")
        print("    ├─────────────\x1b[48;2;245;47;171m────\x1b[0m┤                                                                                                  ├\x1b[48;2;20;51;134m────\x1b[0m─────────────┤")
        print("    │ Whitehall   \x1b[48;2;245;47;171m    \x1b[48;2;129;30;92m│ \x1b[0m                                                                                                \x1b[48;2;20;51;134m │\x1b[48;2;28;89;255m    \x1b[0m Park Lane   │")
        print("    │             \x1b[48;2;245;47;171m    \x1b[48;2;129;30;92m│ \x1b[0m                                                                                                \x1b[48;2;20;51;134m │\x1b[48;2;28;89;255m    \x1b[0m             │")    
        print("    │             \x1b[48;2;245;47;171m    \x1b[48;2;129;30;92m│ \x1b[0m                                                                                                \x1b[48;2;20;51;134m │\x1b[48;2;28;89;255m    \x1b[0m             │")
        print("    │             \x1b[48;2;245;47;171m    \x1b[48;2;129;30;92m│ \x1b[0m                                                                                                \x1b[48;2;20;51;134m │\x1b[48;2;28;89;255m    \x1b[0m             │")
        print("    ├─────────────\x1b[48;2;129;30;92m────\x1b[0m┤                                                                                                  ├\x1b[48;2;20;51;134m────\x1b[0m────────∖──⁄─┤")
        print("    │ Electric Co. │╲ │                                                                                                  │ SUPER TAX - 💎 -│") # ∖  ⁄
        print("    │ $150       __╵ ╲│                                                                                                  │ $100      /¯¯¯¯\\│")
        print("    │            ╲ ╷¯¯│                                                                                                  │          | (⁐⁐) |")
        print("    │             ╲│  │                                                                                                  │           \\____/│")
        print("    ├─────────────\x1b[48;2;129;30;92m────\x1b[0m┤                                                                                                  ├\x1b[48;2;20;51;134m────\x1b[0m─────────────┤")
        print("    │ Pall Mall   \x1b[48;2;245;47;171m    \x1b[48;2;129;30;92m│ \x1b[0m                                                                                                \x1b[48;2;20;51;134m │\x1b[48;2;28;89;255m    \x1b[0m Mayfair     │")
        print("    │             \x1b[48;2;245;47;171m    \x1b[48;2;129;30;92m│ \x1b[0m                                                                                                \x1b[48;2;20;51;134m │\x1b[48;2;28;89;255m    \x1b[0m             │")
        print("    │             \x1b[48;2;245;47;171m    \x1b[48;2;129;30;92m│ \x1b[0m                                                                                                \x1b[48;2;20;51;134m │\x1b[48;2;28;89;255m    \x1b[0m             │")
        print("    │             \x1b[48;2;245;47;171m    \x1b[48;2;129;30;92m│ \x1b[0m                                                                                                \x1b[48;2;20;51;134m │\x1b[48;2;28;89;255m    \x1b[0m             │")
        print("    ├───────┬─╥─╥─\x1b[48;2;129;30;92m╥─╥─\x1b[0m┼\x1b[48;2;6;89;125m──────────\x1b[0m┬\x1b[48;2;6;89;125m──────────\x1b[0m┬──────────┬\x1b[48;2;6;89;125m──────────\x1b[0m┬──────────┬──────────┬\x1b[48;2;89;59;48m──────────\x1b[0m┬──────────┬\x1b[48;2;89;59;48m──────────\x1b[0m┼\x1b[48;2;20;51;134m────\x1b[0m─────────────┤")
        print("    │       │ ║ ║ ║ ║ \x1b[48;2;6;89;125m│\x1b[48;2;0;166;237m          │          \x1b[48;2;6;89;125m│\x1b[0m  CHANCE  \x1b[48;2;6;89;125m│\x1b[48;2;0;166;237m          \x1b[48;2;6;89;125m│\x1b[0m  King's  │INCOME TAX\x1b[48;2;89;59;48m│\x1b[48;2;165;105;83m          \x1b[48;2;89;59;48m│\x1b[0mCOMMUNITY \x1b[48;2;89;59;48m│\x1b[48;2;165;105;83m          \x1b[48;2;89;59;48m│\x1b[0m  ____     ____  │")
        print("    │   J   │ J A I L \x1b[48;2;6;89;125m│\x1b[48;2;0;166;237m          │          \x1b[48;2;6;89;125m│\x1b[0m\x1b[38;2;245;77;201m  _----_  \x1b[0m\x1b[48;2;6;89;125m│\x1b[48;2;0;166;237m          \x1b[48;2;6;89;125m│\x1b[0m  Cross   │          \x1b[48;2;89;59;48m│\x1b[48;2;165;105;83m          \x1b[48;2;89;59;48m│\x1b[0m     CHEST\x1b[48;2;89;59;48m│\x1b[48;2;165;105;83m          \x1b[48;2;89;59;48m│\x1b[0m /  __|   /    \\ │")
        print("    │   U   │ ║ ║ ║ ║ │Pent'ville│  Euston  │\x1b[38;2;245;77;201m / _--_ \\ \x1b[0m│The Angel │          │          │whitechp'l│  __\x1b[33m┌┐\x1b[0m__  │ Old Kent \x1b[0m│|  |_ ‾| |  ()  |│")
        print("    │   S   │ ║ ║ ║ ║ │   Road   │   Road   │\x1b[38;2;245;77;201m \\/  _/ / \x1b[0m│Islington │ \\¯/___(¯/│    :(    │   Road   │ / _\x1b[33m││\x1b[0m__| │   Road   │ \\____/   \\____/ │")
        print("    │   T   └─╨─╨─╨─╨─┤          │          │\x1b[38;2;20;186;237m    / _/  \x1b[0m│          │( _______\\│          │          │ \\__\x1b[33m││\x1b[0m__  │          \x1b[0m│                 │")
        print("    │                 │          │          │\x1b[38;2;20;186;237m   / /__  \x1b[0m│          │/_| () () │          │          │  __\x1b[33m││\x1b[0m_ \\ │          │   ╷       ____  │")
        print("    │    VISITING     │          │          │\x1b[38;2;255;103;35m   \\___/  \x1b[0m│          │          │          │          │ |__\x1b[33m││\x1b[0m__/ │          │  ╱└──────/   /  │")
        print("    │                 │          │          │\x1b[38;2;255;103;35m    ()    \x1b[0m│          │          │ PAY $200 │          │    \x1b[33m└┘\x1b[0m    │          │  ╲┌──────\\___\\  │")
        print("    └─────────────────┴──────────┴──────────┴──────────┴──────────┴──────────┴──────────┴──────────┴──────────┴──────────┴───╵─────────────┘")

    def input_management(self, user_input):

        if self.action == "trade query" and user_input in ["y", "Y"]:
            state.trade_screen(state.player_turn)

        elif self.action == "trade query":
            self.action = None

        elif self.action == "dice_roll_accept":
            self.action = None
            # moves the cursor above the dice ('ESC[11F') and clears everything below ('ESC[0J')
            print("\x1b[11F\x1b[0J")

            state.player_action.move()

        elif self.action == "chance notice":
            self.action = None
            state.chance.perform_action()

        elif self.action == "community chest notice":
            self.action = None
            state.community_chest.perform_action()

        elif self.action == "save notice":
            self.action = None
            state.homescreen()

        elif self.action == "kick user" and user_input in ["c", "C"]:
            self.action = None
            self()

        elif self.action == "kick user":
            for item in state.online_config.joined_clients:
                if item[3] == user_input:
                    item[1].sendall(b"booted")
                    self.disconnect_management(item[3])
                    break
            else:
                print("\n    === invalid user ID ===\n\n    ", end = "")

        elif user_input in ["r", "R"]:
            if (state.player_action.dice_rolled == False and self.action == None \
                and state.player[state.player_turn]["jail time"] < 3):
                
                # additional logic is required for online
                if state.online_config.game_strt_event.is_set() and state.online_config.player_num != state.player_turn:
                    print("\n    === it's not your turn ===\n\n    ", end="")
                    return

                state.refresh_board()
                state.player_action.start_roll()
            elif state.dev_mode:
                input("\n    === skipped with devmode [Enter] ===\n\n    ", end="")

                state.refresh_board()
                state.player_action.start_roll()

            elif self.action != None:
                print("\n    === complete space-dependent action first ===\n\n    ", end="")
            else:
                print("\n    === you've already rolled ===\n\n    ", end = "")

        elif user_input in ["p", "P"]:
            has_properties = False
            for i in range(28):
                if state.property_data[i]["owner"] == state.player_turn:
                    has_properties = True
                    break

            if has_properties == False:
                print("\n    === you don't own any properties ===\n\n    ", end = "")
            else:
                state.display_property_list(state.player_turn)

        elif user_input in ["t", "T"]:
            state.trade_screen(state.player_turn)

        elif user_input in ["e", "E"] and not state.online_config.game_strt_event.is_set():
            if (state.player_action.dice_rolled == True and self.action == None) or state.dev_mode == True:
                next(state.player_turn)
                state.player_action.dice_rolled = False
                state.player_action.doubles_rolled = 0

                # when a player goes bankrupt, players alive are checked,
                # so there will be at least 2 people when this code is active.
                while state.player[state.player_turn]["status"] in ("bankrupt", "disconnected"): next(state.player_turn)
                
                # forcibly moves the player out of jail if they've been in for 3 turns,
                # and they don't have a card
                if state.player[state.player_turn]["jail time"] >= 3 and state.player[state.player_turn]["jail passes"] == 0:
                    state.player_action.remove_from_jail(state.player_turn)
                    state.player[state.player_turn]["$$$"] -= 50

                    if state.player[state.player_turn]["$$$"] < 0: state.player_is_broke(state.player_turn)
                    
                state.refresh_board()
                
            else: 
                print("\n    === roll dice first and complete space-dependent action first ===\n\n    ", end = "")
                
        elif user_input in ["s", "S"]:
            if state.online_config.game_strt_event.is_set():
                print("\n    === are we deadass? ===\n\n    ", end="")
                return


            if state.online_config.game_strt_event.is_set():
                send_data("clientquit")

            save_game_to_file(
                "state.game_version", "state.players_playing", "state.player_turn", "state.player_action.doubles_count",
                "state.dev_mode", "state.player_action.dice_rolled", "state.refresh_board.action", "state.player", "state.chance.values",
                "state.chance.index", "state.community_chest.values", "state.community_chest.index"
            )
            self.action = "save notice"
            self.prev_cash = [0, 0, 0, 0]
            self.passed_go = False
            
            # forcibly resets all variables in case user 
            # starts new game without restarting program
            state.players_playing = 0
            state.dev_mode = False
            state.house_total = 32
            state.hotel_total = 12
            state.time_played = 0
            state.game_version = 0.7
            state.player_turn = None

            for prop in state.property_data:
                prop["owner"] = None
                prop["upgrade state"] = 0

            # resets all attribute for my custom classes  
            for item in globals():
                if isinstance(item, utils.parent_class):
                    item.__init__()

            print("\n    === game saved. [Enter] to return to the main menu ===\n\n    ", end = "")

        elif user_input in ["b", "B"] and self.action == "property":
            _prop = state.property_data[state.prop_from_pos[state.player[state.player_turn]["pos"]]]

            # the property isn't purchased if the player cannot afford it
            if state.player[state.player_turn]["$$$"] < _prop["street value"]:
                print("\n    === you can't afford this property ===\n\n    ", end="")
                return
            
            _prop["owner"] = int(state.player_turn)
            _prop["upgrade state"] = 1
            state.player[state.player_turn]["total properties"] += 1
            state.player[state.player_turn]["$$$"] -= _prop["street value"]

            colour_set = []
            for prop in state.property_data:
                if not ("colour set" in prop.keys() and "colour set" in _prop.keys()):
                    continue

                if prop["colour set"] == _prop["colour set"] and prop["owner"] == _prop["owner"]:
                    colour_set.append(prop)
                         
            # brown and dark blue (sets 0 and 7) only have two properties in their set
            if (len(colour_set) == 3 and _prop["colour set"] not in [0, 7]) \
                or (len(colour_set) == 2 and _prop["colour set"] in [0, 7]):

                for _prop in colour_set: _prop["upgrade state"] = 2

            self.action = None

            if state.online_config.game_strt_event.is_set():
                send_data(f"propertyupdate:{state.prop_from_pos[state.player[state.player_turn]['pos']]}:{state.online_config.player_num}:{_prop['upgrade state']}")

            state.refresh_board()

        elif user_input in ["a", "A"] and self.action == "property":
            auctioned_property = state.prop_from_pos[state.player[state.player_turn]["pos"]]
            if state.online_config.game_strt_event.is_set():
                send_data(f"auctionstart:{auctioned_property}")
            state.display_property(auctioned_property, bid = True)

        elif user_input in ["g", "G"] and state.player[state.player_turn]["status"] == "jail":
            
            # moving the player to just visiting
            if state.player[state.player_turn]["$$$"] >= 50:
                state.player[state.player_turn]["$$$"] -= 50
                state.player_action.remove_from_jail(state.player_turn)
            else:
                print("\n    === you cannot afford bail ===\n\n    ", end = "")

        elif user_input in ["u", "U"] and state.player[state.player_turn]["status"] == "jail":
            if state.player[state.player_turn]["jail passes"] > 0:
                state.player[state.player_turn]["jail passes"] -= 1
                state.player_action.remove_from_jail(state.player_turn)
            else:
                print("\n    === you don't have any get out of jail free cards to use ===\n\n    ", end = "")

        elif user_input in ["k", "K"] and state.online_config.game_strt_event.is_set() \
                and state.online_config.socket_type == "host":
            self.action = "kick user"
            print("\n    === enter ID of player you wish to kick ([C]ancel) ===\n")

            for item in state.online_config.joined_clients:
                print(f"    [{item[3]}] {item[0]}")
            print("\n    ", end="")

        elif user_input == "devmode":
            state.dev_mode = True
            state.refresh_board()

        elif state.dev_mode == False:
            print("\n    === command not recognised ===\n\n    ", end = "")

        # devmode commands
        # certainly all of these input()s won't cause online issues
        elif user_input == "setplayerpos":
            x = input("    === which player: ")
            xx = input("    === set pos: ")
            state.player[int(x)]["last pos"] = state.player[int(x)]["pos"]
            state.player[int(x)]["pos"] = int(xx)
            update_player_position(int(xx))
            update_player_position(state.player[int(x)]["last pos"], "remove")
            if state.player[int(x)]["pos"] == 40: state.player[int(x)]["status"] = "jail"
            state.refresh_board()
            state.player_action(int(x))

        elif user_input == "showplayerdict":
            for i in state.player:
                print(f"{i}: {state.player[i]}")

        elif user_input == "setdiceroll":
            state.player_action.dice_value[1] = int(input("    === first dice value: "))
            state.player_action.dice_value[2] = int(input("    === second dice value: "))
            state.player_action.move()
           
        elif user_input == "bankruptcy":
            x = input("    === which player: ")
            state.player_is_broke(int(x))

        elif user_input ==  "editplayerdict":
            print("    === Please edit position using the 'setplayerpos' command ===")
            x = input("    === which player: ")
            xx = input("    === which key: ")
            xxx = input("    === what value: ")
            try   : state.player[int(x)][xx] = int(xxx)
            except ValueError: state.player[int(x)][xx] = xxx

        elif user_input == "propertybid":
            auctioned_property = int(input("    === enter property number: "))

            # since bidding will require 'state.player_turn' to change, this stores the proper player turn
            state.display_property.true_player_turn = state.player_turn.index
            state.display_property.action = "auction"
            state.display_property(auctioned_property)

        elif user_input == "showproplist":
            for i in state.property_data:
                print(i)

        elif user_input == "showchangedprops":
            for i in state.property_data:
                if i["owner"] != None:
                    print(i)

        elif user_input == "setplayerprops":
            x = int(input("    === what player: "))
            xx = input("    === what property (commands: 'all', 'done'): ")
            while xx != "done":
                if xx == "all":
                    for i in range(28): state.property_data[i]["owner"] = x; state.property_data[i]["upgrade state"] = 1
                    xx = "done"
                else:
                    try:
                        int(xx)
                    except ValueError:
                        print("=== invalid number ===")
                        xx = input("    === what property (commands: 'all', 'done'): ") 
                        continue
                    state.property_data[int(xx)]["owner"] = x
                    state.property_data[int(xx)]["upgrade state"] = 1

                    # checks if the player now owns all the properties in a colour set
                    colour_set = []
                    for prop in state.property_data:
                        if not ("colour set" in prop.keys() and "colour set" in state.property_data[int(xx)].keys()):
                            continue

                        if prop["colour set"] == state.property_data[int(xx)]["colour set"] and prop["owner"] == state.property_data[int(xx)]["owner"]:
                            colour_set.append(prop)
                         
                    # brown and dark blue (sets 0 and 7) only have two properties in their set
                    if ((len(colour_set) == 3 and state.property_data[int(xx)]["colour set"] not in [0, 7])
                        or (len(colour_set) == 2 and state.property_data[int(xx)]["colour set"] in [0, 7])):

                        for _prop in colour_set: _prop["upgrade state"] = 2
                    xx = input("    === what property (commands: 'all', 'done'): ") 
            state.refresh_board()

        elif user_input == "forcechancecard":
            x = int(input("    === what player: "))
            xx = input("    === what card value: ")
            if len(xx) == 1: xx = xx + " "

            for i in range(len(state.chance.cards_value)):
                if state.chance.cards_value[i] == xx:
                    state.chance.index = i

            state.chance.perform_action()

        elif user_input == "forcecccard":
            x = int(input("    === what player: "))
            xx = input("    === what card value: ")

            if len(xx) == 1: xx = xx + " "

            for i in range(len(state.community_chest.cards_value)):
                if state.community_chest.cards_value[i] == xx:
                    state.community_chest.index = i

            state.chance.perform_action()

        elif user_input == "displayvar":
            x = input("enter var:")
            if x in globals():
                print(globals()[x])
            else:
                print("    === variable not found ===\n\n    ", end = "")

        elif user_input == "queuechance":
            card = int(input("    === enter num: "))
            state.chance.values.remove(card)
            state.chance.values.insert(state.chance.index + 1, card)

        elif user_input == "queuecc":
            card = int(input("    === enter num: "))
            state.community_chest.values.remove(card)
            state.community_chest.values.insert(state.community_chest.index + 1, card)

        elif user_input == "arbitrarycode":
            exec(input())

        elif user_input == "setbidqueue":
            u_input = ''
            queue = []
            while u_input != "done":
                u_input = input("enter property (commands: 'done'): ")

                try: queue.append(int(u_input))
                except ValueError: pass

            input(f"confirm: {queue}")
            state.display_property(*queue, bid = True)

        elif user_input == "dumpsave":
            try:
                save = open("save_file.james", encoding = "utf-8")
            except:
                print("\n    === save not found ===\n\n    ", end = "", flush = True)
            else:
                print("===")
                for line in save: print(line.rsplit("\n")[0])
                print("===")

                save.close()

        else:
            print("\n    === command not recognised ===\n\n    ", end = "")

    def disconnect_management(self, quitter):
        super().disconnect_management(quitter)
        self()

        if state.online_config.socket_type == "client":
            index = state.online_config.joined_clients[2].index(quitter)
            name = state.online_config.joined_clients[0][index]
        else:
            for item in state.online_config.joined_clients:
                if item[3] == quitter:
                    name = item[0]
                    break

        print(f"=== {name} lost connection to game ===\n\n    ", end="")

    def end_turn_logic(self):
        """increments the player turn, handles edge cases"""

        next(state.player_turn)
        state.player_action.dice_rolled = False
        state.player_action.doubles_rolled = 0

        # when a player goes bankrupt, players alive are checked,
        # so there will be at least 2 people when this code is active.
        while state.player[state.player_turn]["status"] in ("bankrupt", "disconnected"): next(state.player_turn)
                
        # forcibly moves the player out of jail if they've been in for 3 turns,
        # and they don't have a card
        if state.player[state.player_turn]["jail time"] >= 3 and state.player[state.player_turn]["jail passes"] == 0:
            state.player_action.remove_from_jail(state.player_turn)
            state.player[state.player_turn]["$$$"] -= 50

            if state.player[state.player_turn]["$$$"] < 0: state.player_is_broke(state.player_turn)


class display_property_list_class(utils.parent_class):
    def __init__(self):
        self.player = None
        self.allow_bankruptcy = False
        
    def __call__(self, _player, clear = True, allow_bankruptcy = False):
        state.current_screen = self.__name__

        self.player = _player
        self.allow_bankruptcy = allow_bankruptcy

        if clear == True: clear_screen()

        print()
        print("    ╔════════════════════════════════════════════════════════════════╗")
        print("    ║                                                                ║")
        print("    ║                       LIST OF PROPERTIES:                      ║")
        print("    ║                                                                ║")
        
        # this prints out all the properties that the player owns in a fancy table (sorted by stations, utilities, properties)

        _count = 0

        # since "_count" is separate from the property data, this dictionary will store the conversions
        self.conversion_dictionary = {}

        stations_displayed = False
        utilities_displayed = False

        # this checks what stations the player owns and displays them first
        for i in [2, 10, 17, 25]:
            if state.property_data[i]["owner"] == _player:
                sleep(150)
                _count += 1
                print(f"    ║   [{_count}]  │ {state.property_data[i]['name']}", end = "")
                
                self.conversion_dictionary[_count] = i

                for ii in range(22 - len(state.property_data[i]['name'])):
                    print(" ", end = "")

                print(f"│ ${state.property_data[i]['street value']} │", end = "")
            
                if state.property_data[i]["upgrade state"] == -1:
                    print(" Mortgaged              ║")
                else:
                    print("                        ║")

                stations_displayed = True

        # displays an extra blank line to separate the stations from the other cards
        if stations_displayed == True:
            print("    ║                                                                ║")   

        for i in [7, 20]:
            if state.property_data[i]["owner"] == _player:
                sleep(150)
                _count += 1
                print(f"    ║   [{_count}]  │ {state.property_data[i]['name']}", end = "")
                
                self.conversion_dictionary[_count] = i

                for ii in range(22 - len(state.property_data[i]["name"])):
                    print(" ", end = "")
                print(f"│ ${state.property_data[i]['street value']} │", end="")

                if state.property_data[i]["upgrade state"] == -1:
                    print(" Mortgaged              ║")
                else:
                    print("                        ║")

                utilities_displayed = True

        if utilities_displayed == True:
            print("    ║                                                                ║")

        for i in range(28):
            if state.property_data[i]["owner"] != _player or state.property_data[i]["type"] != "property":
                continue

            sleep(150)
            _count += 1
            self.conversion_dictionary[_count] = i
            if _count >= 10:
                print(f"    ║   [{_count}] │ {state.property_data[i]['name']}", end = "")
            else:
                print(f"    ║   [{_count}]  │ {state.property_data[i]['name']}", end = "")

            for ii in range(22 - len(state.property_data[i]["name"])): print(" ", end = "")

            print(f"│ ${state.property_data[i]['street value']} ", end = "")
            if state.property_data[i]["street value"] < 100: print(" ", end = "")

            if state.property_data[i]["upgrade state"] != -1:
                print(f"│ ${state.property_data[i]['house cost']}", end = "")
                
                if state.property_data[i]["house cost"] < 100:
                    print(" ", end = "")
                    
                print(" × ", end = "")

                if state.property_data[i]["upgrade state"] == 7:
                    print("🏠🏠🏠🏠 🏨     ║")

                else:

                    # prints the number of houses on the property
                    x = ""
                    for ii in range(state.property_data[i]["upgrade state"] - 2): x += "🏠"

                    print(f"{x}", end = "")
                    for ii in range(16 - (2 * len(x))): print(" ", end = "")
                    print("║")
            elif state.property_data[i]["upgrade state"] == -1: print("│ Mortgaged              ║")

        print("    ║                                                                ║")
        print("    ╚════════════════════════════════════════════════════════════════╝")
        print()

        can_leave = True
        if state.player[state.player_turn]["$$$"] < 0:
            can_leave = False

        prompt = [["Trade", "#"],[True, True], [4, 3]]

        # inserts the bankruptcy prompt if given through state.player_is_broke()
        if allow_bankruptcy != False:
            prompt[0].append("Go bankrupt")
            prompt[1].append(True)
            prompt[2].append(3)
        prompt[0].append("Back")
        prompt[1].append(can_leave)
        prompt[2].append(6)
        for i in create_button_prompts(prompt[0], prompt[1], prompt[2]):
            print(i)

        if state.dev_mode != False: print(self.conversion_dictionary)
        print("\n    ", end="")

    def input_management(self, user_input):
        if user_input in ["b", "B"]:

            # checks that the player doesn't have negative cash,
            # and that no other players have negative cash
            if state.player[state.player_turn]["$$$"] < 0:
                print("\n    === you must clear your debts before returning to the game ===\n\n    ", end = "")
            else:
                lock = False
                for i in range(1, state.players_playing + 1):
                    if state.player[i]["$$$"] < 0 and state.player[i]["status"] == "playing":
                        state.player_is_broke(i)
                        lock = True
                        break
                if lock == False: state.refresh_board()
                
        elif user_input in ["t", "T"]:
            if state.trade_screen.is_trade == True:
                state.trade_screen.display_trade_window()
            else:
                state.trade_screen(state.player_turn)

        elif user_input in ["g", "G"] and self.allow_bankruptcy == True:
            bankruptcy(self.player, "bank") # Note to self: fix
        
        elif user_input == "#":
            print("\n   === no, # just means a number, like enter a number from the list ===\n\n    ",end="")
            
        else:
            try:
                int(user_input)                
            except ValueError:
                print("\n    === command not recognised ===\n\n    ", end = "")
            else:
                if int(user_input) in self.conversion_dictionary:
                   state.display_property(self.conversion_dictionary[int(user_input)])
                else:
                    print("\n    === command not recognised ===\n\n    ", end = "")


class display_property_class(utils.parent_class):
    def __init__(self):
        self.property = None
        self.skipped_bids = 0
        self.bid_number = 0
        self.property_queue = []
        self.action = None
        self.action_2 = None
        self.player_bid_turn = None

        self.player_bids = better_iter([
            {"player": 1, "$$$": 0},
            {"player": 2, "$$$": 0},
            {"player": 3, "$$$": 0},
            {"player": 4, "$$$": 0}
        ])
        self.notice = better_iter([
            "      ╔════════════════════════════════════════════════════════════════╗",
            "      ║                                                                ║",
            "      ║                             NOTICE:                            ║",
            "      ║                                                                ║",
            "      ║   you can bid more than your current cash, and go into debt.   ║",
            "      ║  however, at the end you will still have to find enough money  ║",
            "      ║                                                                ║",
            "      ╚════════════════════════════════════════════════════════════════╝"
        ])
        self.bid_struc = better_iter(
            [
                "      ╔═════════════════════╗",

                # not a function string as bids() in call() properly assembles the output
                "      ║ Player @@@ bid: $### &&&║",
                "      ╚═════════════════════╝"
            ],
            True
        )

    def __call__(self, *_prop_num: int, bid = False):
        """
        displays the property art for a given property,
        if multiple numbers are given, all are auctioned,
        regardless of 'bid' value
        """

        # arbitrary args allows prop_num to be blank,
        # but that causes errors later, and so it caught
        if len(_prop_num) == 0:
            raise TypeError("at least one property has to be provided")

        # if multiple properties are given or bid is enabled
        if len(_prop_num) > 1 or bid:
            self.property_queue = list(_prop_num)

            # ensures that it isn't resent halfway through an auction
            if not self.player_bid_turn:
                self.player_bid_turn = state.player_turn.copy()

                # ensures that only playing players can play
                while state.player[self.player_bid_turn]["status"] in ("bankrupt", "disconnected"):
                    next(self.player_bid_turn)

                # checks how many players are participating
                self.players_bidding = 0
                for _player in state.player.items():
                    if _player[1]["status"] not in ("bankrupt", "disconnected"):
                        self.players_bidding += 1

        if len(_prop_num) > 1:
            print("    === auction queue ===\n")
            for prop in self.property_queue:

                # isn't this cool, and inline if statement WITHIN a string:
                print(f"    {state.state.property_data[prop]['name']} {(lambda: '(mortgaged)' if state.state.property_data[prop]['upgrade state'] == -1 else '')()}")
            print()

        if bid: self.action = "auction"

        # even if one number is given, python creates a one item tuple,
        # which cannot be used as an index, and so is fixed
        self.property = _prop_num[0]

        state.current_screen = self.__name__

        # resets the iterators each time, as a precaution
        self.notice.index = -1
        self.player_bids.index = -1
        self.bid_struc.index = -1

        printed_bids = 0

        extra_space = ["", "", "", ""]

        self.colour_set = []
        for prop in state.state.property_data:
            if not ("colour set" in prop.keys() and "colour set" in state.property_data[self.property].keys()):
                continue

            if prop["colour set"] == state.property_data[self.property]["colour set"]:
                self.colour_set.append(prop)

        clear_screen()
        print()
        
        def bidding_notice() -> str:
            if self.action in ["auction", "finished"]: return next(self.notice)
            else: return ""

        def display_bids() -> str:
            """displays the players bids alongside the property"""
            nonlocal printed_bids

            output = ""

            # ensures that only when there are bids yet to be displayed is the code called
            if self.action in ["auction", "finished"] and printed_bids < self.bid_number:
                
                output = next(self.bid_struc)
                
                # these symbols are only in the middle line, which need to be replaced with actual information
                if "@" in output:

                    # makes sure that there is the correct amount of spaces
                    extra_space = ""

                    bid = next(self.player_bids)
                    for i in range(4 - len(str(bid["$$$"]))): extra_space += " "

                    output = output.replace("@@@", str(bid["player"]))
                    output = output.replace("###", str(bid["$$$"]))
                    output = output.replace("&&&", extra_space)

                    # if this is the first bid displayed, they in will be the highest
                    if printed_bids == 0: output += " ✨ TOP BID ✨"

                if output == "      ╚═════════════════════╝": printed_bids += 1

            return output

        if state.property_data[self.property]["upgrade state"] == -1:

            # this class allows the mortgaged property to have a gradient background
            # by changing the outside stripe from lighter to darker and the inside vice versa
            def gradient(i, go_darker: bool | None = False, background_or_text: int | None = 4):
                """3rd arg: 4 = background, 3 = text, anything else won't work"""

                if go_darker == True: return f"\x1b[{background_or_text}8;2;255;{95 - int((28 / 21) * i)};{59 - int((36 / 21) * i)}m"
                else                : return f"\x1b[{background_or_text}8;2;255;{67 + int((28 / 21) * i)};{23 + int((36 / 21) * i)}m"

            # using a for loop means the text is inserted using the index as a guide
            def extra_text(line: int):
                """returns appropriate text for the mortgaged property art"""
                output = "                        "
                if   line == 1 : output = f"{extra_space[0]}{extra_space[1]} {state.property_data[self.property]['name'].upper()}{extra_space[0]}  "
                elif line == 8 : output = "     MORTGAGE VALUE:    "
                elif line == 9 : output = f"          $ {int(m_val)}{extra_space[2]}         "
                elif line == 12: output = "     TO UNMORTGAGE:     "
                elif line == 13: output = f"          $ {int(m_val * 1.1)}{extra_space[3]}         "
                return output

            # see above ^
            def side_info(line: int):
                output = ""
                if line < 6: output = bidding_notice()
                elif 6 < line < 19: output = display_bids()
                return output

            m_val = int(state.property_data[self.property]["street value"] / 2)
            if len(str(m_val)) == 2           : extra_space[2] = " "
            if len(str(int(m_val * 1.1))) == 2: extra_space[3] = " "

            for i in range((21 - len(state.property_data[self.property]["name"])) // 2): extra_space[0] += " "
            if len(state.property_data[self.property]["name"]) % 2 == 0: extra_space[1] = " "

            # do not be afraid of the virtual terminal sequences
            print(f"    \x1b[38;2;255;255;255m▗▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▖\x1b[0m{bidding_notice()}")
            print(f"    \x1b[38;2;12;12;12m\x1b[48;2;255;255;255m▌  \x1b[38;2;255;95;59m▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃  \x1b[0m\x1b[38;2;255;255;255m▌\x1b[0m{bidding_notice()}")
            
            for i in range(21):
                print(f"    \x1b[38;2;12;12;12m\x1b[48;2;255;255;255m▌  {gradient(i, True, 3)}{gradient(i)}▊\x1b[38;2;255;255;255m{extra_text(i)}{gradient(i, False, 3)}{gradient(i, True)}▎\x1b[48;2;255;255;255m  \x1b[0m\x1b[38;2;255;255;255m▌\x1b[0m{side_info(i)}")

            print("    \x1b[38;2;12;12;12m\x1b[48;2;255;255;255m▌\x1b[0m\x1b[48;2;255;255;255m  \x1b[48;2;255;67;23m\x1b[38;2;255;255;255m▅▅▅▅▅▅▅▅▅▅▅▅▅▅▅▅▅▅▅▅▅▅▅▅▅▅\x1b[0m\x1b[48;2;255;255;255m  \x1b[0m\x1b[38;2;255;255;255m▌\x1b[0m")
            print("    \x1b[38;2;255;255;255m▝\x1b[38;2;12;12;12m\x1b[48;2;255;255;255m▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄\x1b[0m\x1b[38;2;255;255;255m▘\x1b[0m")

        # station cards
        elif self.property in [2, 10, 17, 25]:

            print(f"    ┌──────────────────────────────┐{bidding_notice()}")
            print(f"    │                              │{bidding_notice()}")
            print(f"    │    /¯¯¯¯¯\\           _______ │{bidding_notice()}")
            print(f"    │    \\     /          /      / │{bidding_notice()}")
            print(f"    │     \\   /          |      /  │{bidding_notice()}")
            print(f"    │     |   |___________\\    |   │{bidding_notice()}")
            print(f"    │  /¯¯¯                    |   │{bidding_notice()}")
            print(f"    │ |                         \\  │{bidding_notice()}")
            print("    │  \\__  _____  __________  __\\ │")
            print(f"    │    /  |  /    \\      /    \\  │{display_bids()}")
            print(f"    │   /   | |      |    |      | │{display_bids()}")
            print(f"    │  /___/   \\____/      \\____/  │{display_bids()}")

            # This centers the station name by adding extra whitespace 
            # for every character less than the maximum possible length (21)
            for ii in range((21 - len(state.property_data[self.property]["name"])) // 2): extra_space[0] += " "
            
            # since the upper code can only add two spaces, if the difference
            # between the maximum length and actual length is odd (so the value is even)...
            # ...an extra space is added to the left of the name to center it properly
            if len(state.property_data[self.property]["name"]) % 2 == 0: extra_space[1] = " "

            print(f"    │                              │{display_bids()}")
            print(f"    │{extra_space[0]}{extra_space[1]}    {state.property_data[self.property]['name']}     {extra_space[0]}│{display_bids()}")
            print(f"    │                              │{display_bids()}")
            print(f"    │ RENT                    $25  │{display_bids()}")
            print(f"    │                              │{display_bids()}")
            print(f"    │ If 2 stations are owned $50  │{display_bids()}")
            print(f"    │                              │{display_bids()}")
            print(f"    │ If 3 stations are owned $100 │{display_bids()}")
            print(f"    │                              │{display_bids()}")
            print("    │ If 4 stations are owned $200 │")
            print("    │                              │")
            print("    │                              │")
            print("    └──────────────────────────────┘")

        # electric company
        elif self.property == 7:

            # because electric company and water works are so different from the other cards, they have their own art
            print(f"    ┌──────────────────────────────┐{bidding_notice()}")
            print(f"    │             ____             │{bidding_notice()}")
            print(f"    │ __       /¯¯    ¯¯\\       __ │{bidding_notice()}")
            print(f"    │   ¯¯--  /  _    _  \\  --¯¯   │{bidding_notice()}")
            print(f"    │        |   \\\\  //   |        │{bidding_notice()}")
            print(f"    │  ----  |    \\\\//    |  ----  │{bidding_notice()}")
            print(f"    │         \\    \\/    /         │{bidding_notice()}")
            print(f"    │   __--   |   ||   |   --__   │{bidding_notice()}")
            print(f"    │ ¯        \\   ||   /       ¯  │")
            print(f"    │        /  \\======/  \\        │{display_bids()}")
            print(f"    │     /     |======|     \\     │{display_bids()}")
            print(f"    │           |======|           │{display_bids()}")
            print(f"    │            ¯¯¯¯¯¯            │{display_bids()}")
            print(f"    │       Electric Company       │{display_bids()}")
            print(f"    │                              │{display_bids()}")
            print(f"    │   If one utility is owned,   │{display_bids()}")
            print(f"    │    rent is 2 times amount    │{display_bids()}")
            print(f"    │        shown on dice         │{display_bids()}")
            print(f"    │                              │{display_bids()}")
            print(f"    │                              │{display_bids()}")
            print(f"    │ If both utilities are owned, │{display_bids()}")
            print("    │    rent is 4 times amount    │")
            print("    │        shown on dice         │")
            print("    │                              │")
            print("    └──────────────────────────────┘")

        # waterworks
        elif self.property == 20:
            print(f"    ┌──────────────────────────────┐{bidding_notice()}")
            print(f"    │                              │{bidding_notice()}")
            print(f"    │           ()━╤╤━()           │{bidding_notice()}")
            print(f"    │      /¯\\     /\\              │{bidding_notice()}")
            print(f"    │     | ( —————┴┴————————╮     │{bidding_notice()}")
            print(f"    │      \\_/—————————————╮ │     │{bidding_notice()}")
            print(f"    │                      │ │     │{bidding_notice()}")
            print(f"    │                      |_|     │{bidding_notice()}")
            print("    │                              │")
            print(f"    │                              │{display_bids()}")
            print(f"    │         Water Works          │{display_bids()}")
            print(f"    │                              │{display_bids()}")
            print(f"    │                              │{display_bids()}")
            print(f"    │   If one utility is owned,   │{display_bids()}")
            print(f"    │    rent is 2 times amount    │{display_bids()}")
            print(f"    │        shown on dice         │{display_bids()}")
            print(f"    │                              │{display_bids()}")
            print(f"    │                              │{display_bids()}")
            print(f"    │ If both utilities are owned, │{display_bids()}")
            print(f"    │    rent is 4 times amount    │{display_bids()}")
            print(f"    │        shown on dice         │{display_bids()}")
            print("    │                              │")
            print("    │                              │")
            print("    │                              │")
            print("    └──────────────────────────────┘")

        # all streets
        else:
            arrow = lambda i: '>' if state.property_data[self.property]["upgrade state"] == i else ' '

            print(f"    ┌──────────────────────────────┐{bidding_notice()}")

            # this checks what colour set the property is in and adjusts the colour of the printed title deed
            if state.property_data[self.property]["colour set"] == 0:
                colour = "🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫" # brown

            # light blue (set 1) and dark blue (set 7) use the same colour
            elif state.property_data[self.property]["colour set"] in [1, 7]:
                colour = "🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦"
        
            elif state.property_data[self.property]["colour set"] == 2:
                colour = "🟪🟪🟪🟪🟪🟪🟪🟪🟪🟪🟪🟪🟪🟪" # purple (there's no pink square emoji)

            elif state.property_data[self.property]["colour set"] == 3:
                colour = "🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧" # orange

            elif state.property_data[self.property]["colour set"] == 4:
                colour = "🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥" # red

            elif state.property_data[self.property]["colour set"] == 5:
                colour = "🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨" # yellow

            else:
                colour = "🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩" # green

            for i in range(4): print(f"    │ {colour} │{bidding_notice()}")

            print(f"    │                              │{bidding_notice()}")

            # see the same code for the stations
            extra_space[0] = ""
            for ii in range((21 - len(state.property_data[self.property]["name"])) // 2): extra_space[0] += " "

            extra_space[1] = ""
            if len(state.property_data[self.property]["name"]) % 2 == 0: extra_space[1] = " "

            print(f"    │{extra_space[0]}{extra_space[1]}    {state.property_data[self.property]['name']}     {extra_space[0]}│{bidding_notice()}")
            print(f"    │                              │{bidding_notice()}")

            # these just add an extra 1-2 spaces if depending on the length, for rent, colour set rent and all the other stats
            extra_space[0] = ""
            for ii in range(2 - len(str(state.property_data[self.property]["rent"]))): extra_space[0] += " "

            print(f"    │ Rent                 {arrow(1)} ${state.property_data[self.property]['rent']}{extra_space[0]}   │")


            extra_space[0] = ""
            for ii in range(3 - len(str(state.property_data[self.property]["rent"] * 2))): extra_space[0] += " "

            extra_space[1] = ""
            for ii in range(3 - len(str(state.property_data[self.property]["h1 rent"]))): extra_space[1] += " "

            print(f"    │ Rent with colour set {arrow(2)} ${(state.property_data[self.property]['rent'] * 2)}{extra_space[0]}  │{display_bids()}")
            print(f"    │                              │{display_bids()}")
            print(f"    │ Rent with 🏠         {arrow(3)} ${state.property_data[self.property]['h1 rent']}{extra_space[1]}  │{display_bids()}")

            extra_space[0] = ""
            for ii in range(3 - len(str(state.property_data[self.property]["h2 rent"]))): extra_space[0] += " "

            extra_space[1] = ""
            for ii in range(4 - len(str(state.property_data[self.property]["h3 rent"]))): extra_space[1] += " "

            extra_space[2] = ""
            for ii in range(4 - len(str(state.property_data[self.property]["h4 rent"]))): extra_space[2] += " "

            print(f"    │ Rent with 🏠🏠       {arrow(4)} ${state.property_data[self.property]['h2 rent']}{extra_space[0]}  │{display_bids()}")
            print(f"    │ Rent with 🏠🏠🏠     {arrow(5)} ${state.property_data[self.property]['h3 rent']}{extra_space[1]} │{display_bids()}")
            print(f"    │ Rent with 🏠🏠🏠🏠   {arrow(6)} ${state.property_data[self.property]['h4 rent']}{extra_space[2]} │{display_bids()}")

            extra_space[0] = ""
            for ii in range(4 - len(str(state.property_data[self.property]["h5 rent"]))): extra_space[0] += " "

            print(f"    │                              │{display_bids()}")
            print(f"    │ Rent with 🏠🏠🏠🏠 🏨{arrow(7)} ${state.property_data[self.property]['h5 rent']}{extra_space[0]} │{display_bids()}")
            print(f"    │                              │{display_bids()}")

            extra_space[0] = ""
            for ii in range(4 - len(str(state.property_data[self.property]["house cost"]))): extra_space[0] += " "

            print(f"    │ ---------------------------- │{display_bids()}")        
            print(f"    │ House/hotel cost       ${state.property_data[self.property]['house cost']}{extra_space[0]} │{display_bids()}")
            print(f"    │                              │{display_bids()}")

            extra_space[0] = ""
            for ii in range(4 - len(str(state.property_data[self.property]["street value"]))): extra_space[0] += " "

            print(f"    │ Street value           ${state.property_data[self.property]['street value']}{extra_space[0]} │")

            extra_space[0] = ""
            for ii in range(3 - len(str(int(state.property_data[self.property]["street value"] / 2)))): extra_space[0] += " "   
        
            if state.property_data[self.property]["upgrade state"] != -1:
                print(f"    │ mortgage value         ${int(state.property_data[self.property]['street value'] / 2)}{extra_space[0]}  │")
            else:
                print(f"    │ unmortgage value       ${int((state.property_data[self.property]['street value'] / 2) * 1.1)}{extra_space[0]}  │")

            print("    └──────────────────────────────┘")

        if self.action_2 == "finished":
            print(f"\n    === player {self.player_bids[0]['player']} has won the bid, press [Enter] to continue ===\n\n    ", end = "")

        elif self.action == "auction" and self.player_bids.list[self.player_bid_turn] != 0:
            if self.action_2 == "final state.chance":
                print(f"\n    === player {self.player_bid_turn}, now's your final state.chance to place a bid, or [S]kip ===\n\n    ", end = "")
            else:
                print(f"\n    === player {self.player_bid_turn}, place a bid or [S]kip ===\n\n    ", end = "")

        elif self.action == "auction":
            if self.action_2 == "final state.chance":
                print(f"\n    === player {self.player_bid_turn}, now's your final state.chance to raise your bid, or [S]kip ===\n\n    ", end = "")
            else:
                print(f"\n    === player {self.player_bid_turn}, either raise your bid or [S]kip ===\n\n    ", end = "")

        else:
            print()
            print(f"    === your money: {state.player[state.player_turn]['$$$']} ===\n")
            actions = [[], [], [4]]

            # if the property has no upgrades, can be mortgaged
            if state.property_data[self.property]["upgrade state"] in [0, 1, 2]:
                actions[0].append("Mortgage")
                actions[1].append(True)

            # if the property has upgrades, cannot be mortgaged
            elif state.property_data[self.property]["upgrade state"] > 2:
                actions[0].append("Mortgage")
                actions[1].append(False)

            # if the property is mortgaged, checks if the player can afford to unmortgage
            elif state.property_data[self.property]["upgrade state"] == -1:
                actions[0].append("Unmortgage")
                if state.player[state.property_data[self.property]["owner"]]["$$$"] \
                        > round((state.property_data[self.property]["street value"] / 2) * 1.1):

                    actions[1].append(True)
                else:
                    actions[1].append(False)
            
            if state.property_data[self.property]["type"] == "property":
                actions[0].append("Add houses")
                actions[0].append("Sell houses")
                actions[2].append(3)
                actions[2].append(3)
                if 2 <= state.property_data[self.property]["upgrade state"] < 7 and \
                        state.player[state.property_data[self.property]["owner"]]["$$$"] >= state.property_data[self.property]["house cost"]:
                    actions[1].append(True)
                else:
                    actions[1].append(False)
                
                if state.property_data[self.property]["upgrade state"] > 2: actions[1].append(True)
                else                                            : actions[1].append(False)

            actions[2].append(3)

            # if the player is trading, and wants to remove a property
            if state.trade_screen.is_trade == True and \
            self.property in (state.trade_screen.player_1["props"] or state.trade_screen.player_2["props"]):
                actions[0].append("Remove Trade")
                actions[1].append(True)
            else:
                actions[0].append("Trade")
                actions[1].append(True)
        
            actions[0].append("Back")
            actions[1].append(True)
            actions[2].append(6)
            for i in create_button_prompts(actions[0], actions[1], actions[2]): print(i)

        print("\n    ", end = "")

    def input_management(self, user_input):

        def exit_bid(self):
            """resets bid variables, auctions next property if exists"""

            self.action = None
            self.action_2 = None
            self.bid_number = 0
            self.skipped_bids = 0
            self.player_bids = better_iter([
                {"player": 1, "$$$": None},
                {"player": 2, "$$$": None},
                {"player": 3, "$$$": None},
                {"player": 4, "$$$": None}
            ])

            # removes property from queue
            self.property_queue.pop(0)

            # clears the turn counter to ensure a new copy is made next call
            self.player_bid_turn = None

            # checks if there are any items within the list
            if self.property_queue:

                # if there are more properties in the queue,
                # the next one is auctioned
                self.property = self.property_queue[0]
                self.action = "auction"

                # since there could only be one extra property,
                # bid is explicitly set
                self(*self.property_queue, bid = True)
                return # ensures program doesn't return to board

            state.refresh_board()

        if self.action_2 == "finished":
            exit_bid(self)

            state.refresh_board.action = None
            broke_alert = False
            for i in range(1, state.players_playing + 1):
                if state.player[i]["$$$"] < 0 and state.player[i]["status"] == "playing":
                    state.player_is_broke(i)
                    broke_alert = True
                    break

            if broke_alert == False: state.refresh_board()

        elif self.action == "auction":
            try:
                int(user_input)

            except ValueError:

                # 's' is the only valid input
                if user_input not in ["s", "S"]:
                    print("\n    === command not recognised. Please enter a number or [S]kip ===\n\n    ", end = "")
                    return

                self.skipped_bids += 1
                next(self.player_bid_turn)
                     
                 # ensures that only playing players can play
                while state.player[self.player_bid_turn]["status"] == "bankrupt":
                    next(self.player_bid_turn)

                # provides a state.chance for players change their minds
                if self.skipped_bids == self.players_bidding:
                    self.action_2 = "final state.chance"

                # if no players want to buy the property
                elif self.skipped_bids == self.players_bidding * 2:
                    exit_bid(self)
                    return
                
                # if someone has won the bid
                elif self.skipped_bids == self.players_bidding - 1 and self.bid_number > 0:
                    self.player_bids.list = sorted(
                        self.player_bids.list,
                        key = lambda item: item["$$$"],
                        reverse = True
                    )

                    state.player[self.player_bids[0]["player"]]["$$$"] -= self.player_bids[0]["$$$"]
                    state.property_data[self.property]["owner"] = self.player_bids[0]["player"]
                                   
                    # signifies that the auction is over
                    self.action_2 = "finished"

                self(*self.property_queue, bid = True)
                    
            else:

                # checks that the player has entered an higher bid
                valid_bid = True
                for bid in self.player_bids:
                    if int(user_input) <= bid["$$$"]: valid_bid = False

                if not valid_bid:
                    print(f"\n    === player {self.player_bid_turn} either raise your bid or [S]kip ===\n\n    ", end = "")
                    return

                # finds relevant player and updates bid
                for bid in self.player_bids:
                    if bid["player"] == self.player_bid_turn:
                        bid["$$$"] = int(user_input)

                next(self.player_bid_turn)

                # ensures that only playing players can play
                while state.player[self.player_bid_turn]["status"] == "bankrupt":
                    next(self.player_bid_turn)

                if self.bid_number < self.players_bidding: self.bid_number += 1

                self.skipped_bids = 0

                self.player_bids.list = sorted(
                    self.player_bids.list,
                    key = lambda item: item["$$$"],
                    reverse = True
                )

                self(*self.property_queue, bid = True)

        else:
            if user_input in ["b", "B"]:

                # ensures most recently displayed player is shown
                state.display_property_list(state.display_property_list.state.player)
  
            elif user_input in ["t", "T"]:
                if state.property_data[self.property]["upgrade state"] > 0:
                    print("\n    === you cannot trade upgraded properties ===\n\n    ", end="")
                    return

                if state.trade_screen.is_trade:
                    state.trade_screen.add_prop_offer(state.display_property.property)
                    self(self.property)
                    print("=== added to offer===\n\n    ", end="")
                else:
                    state.trade_screen(state.player_turn, self.property)

            elif user_input in ["m", "M"]:
                if state.property_data[self.property]["upgrade state"] in [1, 2]:
                    state.property_data[self.property]["upgrade state"] = -1
                    state.player[state.player_turn]["$$$"] += int(state.property_data[self.property]["street value"] / 2)
                    
                    if state.online_config.game_strt_event.is_set():
                        send_data(f"propertyupdate:{self.property}:{state.property_data[self.property]['owner']}:{state.property_data[self.property]['upgrade state']}")

                    state.display_property(self.property)

                elif state.property_data[self.property]["upgrade state"] == -1:
                    print("\n    === property already mortgaged ===\n\n    ", end = "")

                elif state.property_data[self.property]["upgrade state"] > 2:
                    print("\n    === you cannot mortgage an upgraded property. sell all houses first ===\n\n    ", end = "")

            elif user_input in ["u", "U"]:

                # unmortgaged properties trigger the exit conditon
                if state.property_data[self.property]["upgrade state"] != -1:
                    print("\n    === property not mortgaged ===\n\n    ", end = "")
                    return

                cost = (state.property_data[self.property]["street value"] / 2) * 1.1
                    
                # unmortgages the property if the player can afford it
                if state.player[state.player_turn]["$$$"] < cost:
                    print("\n    === you cannot afford to unmortgage this property ===\n\n    ", end="")
                    return

                state.player[state.player_turn]["$$$"] -= cost
                state.player[state.player_turn]["$$$"] = int(state.player[state.player_turn]["$$$"])
                state.property_data[self.property]["upgrade state"] = 1

                if state.online_config.game_strt_event.is_set():
                    send_data(f"propertyupdate:{self.property}:{state.property_data[self.property]['owner']}:{state.property_data[self.property]['upgrade state']}")
                self(self.property)

            elif user_input in ["a", "A"] and state.property_data[self.property]["type"] == "property":

                # if property is not eligible for upgrading
                if not (2 <= state.property_data[self.property]["upgrade state"] < 8):
                    print("\n    === you cannot upgrade this property ===\n\n    ", end = "")
                    return

                # if player cannot afford to upgrade
                if state.player[state.property_data[self.property]["owner"]]["$$$"] < state.property_data[self.property]["house cost"]:
                    print("\n    === you cannot afford to buy an upgrade ===\n\n    ", end = "")
                    return

                # if other properties in the colour set aren't upgraded at the same level
                for prop in self.colour_set:
                    if prop["upgrade state"] < state.property_data[self.property]["upgrade state"]:
                        print("\n    === other properties in this colour set have not been upgraded equally ===\n\n    ", end="")
                        return
                
                # determines whether a house or hotel is needed and available
                if state.property_data[self.property]["upgrade state"] < 7:
                    if state.house_total < 0:
                        print("\n    === there are no more houses left. all 32 have been purchased ===\n\n    ", end="")
                        return
                    state.house_total -= 1
                    var_change = "house" # so online sends update command for correct var
                else:
                    if state.hotel_total < 0:
                        print("\n    === there are no more hotels left. all 16 have been purchased ===\n\n    ", end="")
                        return
                    state.hotel_total -= 1
                    var_change = "hotel"

                # if exit conditions are passed, then the player can upgrade
                state.player[state.property_data[self.property]["owner"]]["$$$"] -= state.property_data[self.property]["house cost"]
                state.property_data[self.property]["upgrade state"] += 1

                if state.online_config.game_strt_event.is_set():
                    send_data(f"propertyupdate:{self.property}:{state.property_data[self.property]['owner']}:{state.property_data[self.property]['upgrade state']}")
                    if var_change == "house":
                        send_data(f"varupdate:house_total:{state.house_total}")
                    else:
                        send_data(f"varupdate:hotel_total:{state.hotel_total}")
                del var_change
                self(self.property)

            elif user_input in ["s", "S"] and state.property_data[self.property]["type"] == "property":

                # if the property cannot be downgraded
                if state.property_data[self.property]["upgrade state"] <= 2:
                    print("\n    === you cannot downgrade this property ===\n\n    ", end = "")
                    return

                # ensures equal upgrades through the colour set
                for prop in self.colour_set:
                    if prop["upgrade state"] > state.property_data[self.property]["upgrade state"]:
                        print("\n    === other properties in this colour set have not been downgraded equally ===\n\n    ", end="")
                        return

                # adds the house/hotel back into the pool
                if state.property_data[self.property]["upgrade state"] == 8:
                    state.hotel_total += 1
                    var_change = "hotel"
                else:
                    state.house_total += 1
                    var_change = "house"

                state.player[state.property_data[self.property]["owner"]]["$$$"] += state.property_data[self.property]["house cost"] / 2
                state.property_data[self.property]["upgrade state"] -= 1

                if state.online_config.game_strt_event.is_set():
                    send_data(f"propertyupdate:{self.property}:{state.property_data[self.property]['owner']}:{state.property_data[self.property]['upgrade state']}")
                    if var_change == "house":
                        send_data(f"varupdate:house_total:{state.house_total}")
                    else:
                        send_data(f"varupdate:hotel_total:{state.hotel_total}")
                del var_change

                self(self.property)

            elif user_input in ["r", "R"] and state.trade_screen.is_trade:
                
                if not (self.property in state.trade_screen.player_1["props"] or self.property in state.trade_screen.player_2["props"]):
                    print("\n    === command not recognised ===\n\n    ", end="")
                    return

                # removes the property from the appropriate player's trade
                if self.property in state.trade_screen.player_1["props"]:
                    state.trade_screen.player_1["props"].remove(self.property)

                elif self.property in state.trade_screen.player_2["props"]:
                    state.trade_screen.player_2["props"].remove(self.property)
               
                # alerts the user of the change
                self(self.property)
                print("=== removed from offer ===\n\n    ", end="")

            else:
                print("\n    === command not recognised ===\n\n    ", end="")

    def disconnect_management(self, quitter):
        super().disconnect_management(quitter) # ignore I said to do last

        if self.action == "auction":

            # checks how many players are participating
            self.players_bidding = 0
            for _player in state.player.items():
                if _player[1]["status"] not in ("bankrupt", "disconnected"):
                    self.players_bidding += 1


def bankruptcy(_player: int | None = state.player_turn, cause = "bank" or "disconnected" or 1/2/3/4):
    """
    determines how to handle a player's bankruptcy, based on cause,
    and displays win/game finished screen if applicable
    """

    # ensures no key errors
    _player = int(_player)

    if cause == "disconnected":
        state.player[_player]["status"] = "disconnected"
        cause = "bank"
    else:
        state.player[_player]["status"] = "bankrupt"
    
    # this is checking how many players remain after a bankruptcy
    remaining_players = 0
    for i in state.player.items():
        if i[1]["status"] in ("playing", "jail"): remaining_players += 1

    # if only one player remains, then the game finished screen is displayed
    # otherwise, the rest of the function is performed
    if remaining_players == 1:

        # total amount of seconds played
        _total = round(time() - state.start_time)

        # bit of simple math that converts seconds played into Xh Ym Zs
        _hours = _total // 3600
        _remainder = _total % 3600
        _minutes = _remainder // 60
        _seconds = _remainder % 60

        _length = len(str(_hours)) + len(str(_minutes)) + len(str(_seconds))

        extra_space = ""
        for ii in range((6 - _length) // 2): extra_space += " "

        extra_extra_space = ""
        if _length % 2 == 1: extra_extra_space = " "

        # finds the last player
        for item in state.player.items():
            if item[1]["status"] == "playing":
                last_player = item[0]
        clear_screen()
        print()
        print("    ╔════════════════════════════════════════════════════════════════╗")
        print("    ║                                                                ║")
        print(f"    ║                  CONGRATULATIONS, PLAYER {last_player} :)                  ║")
        print("    ║                                                                ║")
        print("    ║                     You have won the game!                     ║")
        print(f"    ║{extra_space}                 you spent {_hours}h {_minutes}m {_seconds}s to do it                 {extra_extra_space}{extra_space}║")
        print("    ║                                                                ║")
        print("    ║           was this really the best use of your time?           ║")
        print("    ║                                                                ║")
        print("    ╚════════════════════════════════════════════════════════════════╝")
        print("\n    ", end = "")

        if state.online_config.game_strt_event.is_set():
            state.online_config.quit_async()

    # finds next competing player, if player turn is bankrupt player
    while state.player[state.player_turn]["status"] in ("bankrupt", "disconnected"):
        next(state.player_turn)

    # adds houses and hotels back as available
    for _property in state.property_data:
        if _property["owner"] != _player:
            continue

        if _property["upgrade state"] == 8:
            state.hotel_total += 1
            state.house_total += 4
        elif _property["upgrade state"] > 2:
            state.house_total += _property["upgrade state"] - 2

    # state.player_is_broke passes on None as cause
    if cause == None: cause = "bank"

    # if the player is in debt to the bank,
    # all properties are returned then auctioned
    if cause == "bank":
        auction_queue = []
        for i in range(len(state.property_data)):
            if state.property_data[i]["owner"] != _player:
                continue

            # properties remained mortgaged, but don't keep any upgrades
            if state.property_data[i]["upgrade state"] != -1:
                state.property_data[i]["upgrade state"] == 0
            state.property_data[i]["owner"] = None
            auction_queue.append(i)

        # auctions properties if any exist
        if len(auction_queue) > 0:
             
            # when online, a bid could be called while one is already happening,
            # in that case the properties are just added on
            if state.online_config.game_strt_event.is_set() and state.display_property.action == "auction":
                state.display_property.property_queue.extend(auction_queue)
                state.display_property(*state.display_property.property_queue, bid = True)
            
            elif state.online_config.game_strt_event.is_set() and state.trade_screen.is_trade:
                pass
            else:
                state.display_property(*auction_queue, bid = True)
        else:
            state.refresh_board()

    # for some stupid reason, upgrades on properties are not transferred,
    # but are sold and the money is given to the owed player instead.
    # (monopoly's stupid rules not mine)
    else:
        owed_player = int(cause)
        for _property in state.property_data:
            if _property["owner"] != _player:
                continue

            _property["owner"] = owed_player
            upgrades = _property["upgrade state"] - 2
             
            # houses are sold back to bank for half price
            if upgrades > 0:
                state.player[owed_player]["$$$"] += upgrades * (_property["house cost"] / 2)

            # upgraded properties have to be part of a colour set,
            # and so are reset to state 2, while un-upgraded properties remain as is
            if _property["upgrade state"] > 2:
                _property["upgrade state"] = 2

        # transfers any escape jail cards to the other player
        state.player[owed_player]["jail passes"] += state.player[_player]["jail passes"]
        state.player[owed_player]["$$$"] += state.player[_player]["$$$"]

        # makes sure players are aware of changes
        if state.online_config.game_strt_event.is_set() and owed_player == state.online_config.player_num:
            print("=== you gained the properties of the bankrupt player! ===\n\n    ", end="")
        else:
            print(f"=== player {cause} gained the properties of the bankrupt player ===\n\n    ", end="")

    if state.online_config.game_strt_event.is_set():
        send_data(f"varupdate:house_total:{state.house_total}")
        send_data(f"varupdate:hotel_total:{state.hotel_total}")


class player_action_class(utils.parent_class):
    """allows players to move on the dice roll"""
    def __init__(self):

        # all of the art for the dice rolling animation
        self.dice_image_frame = [[] for i in range(7)]

        self.dice_image_frame[0] = ["│           │", "│           │", "│           │"]
        self.dice_image_frame[1] = ["│           │", "│     o     │", "│           │"]
        self.dice_image_frame[2] = ["│   o       │", "│           │", "│       o   │"]
        self.dice_image_frame[3] = ["│        o  │", "│     o     │", "│  o        │"]
        self.dice_image_frame[4] = ["│  o     o  │", "│           │", "│  o     o  │"]
        self.dice_image_frame[5] = ["│  o     o  │", "│     o     │", "│  o     o  │"]
        self.dice_image_frame[6] = ["│  o  o  o  │", "│           │", "│  o  o  o  │"]

        self.dice_rolling_state = "off"

        # so I can index die 1 as [1] and die 2 as [2]
        self.dice_value = [None, 0, 0]
        self.dice_countdown = 0
        self.doubles_count = 0
        self.dice_rolled = False

        self.doubles_art = [
            r"✨    |¯¯¯\   /¯¯\  |¯||¯| |¯⁐¯\ |¯|   |¯¯¯| /¯¯¯|   ✨   ",
            r"   ✨ | [) | | () | | || | | --⟨ | |__ | ⁐|_ \ ¯¯\ ✨     ",
            r" ✨   |___/   \__/   \__/  |_⁐_/ |___| |___| |⁐⁐_/     ✨",
        ]
        self.escaped_go_art = [
            '✨    \\¯\\/¯/ /¯¯\\  |¯||¯|    |¯¯¯| /¯⁐⁐|  /¯¯¯|   /‾\\   |¯¯¯\\ |¯¯¯| |¯¯¯\\     |⁐‾‾‾⁐| /‾\\   |¯¯¯| |‾|     ✨  ',
            '   ✨  \\  / | () | | || |    | ⁐|_ \\__ \\ | (⁐⁐   / ^ \\  | ⁐_/ | ⁐|_ | [) |    __| |  / ^ \\  ⁐| |⁐ | |_  ✨    ',
            ' ✨    /_/   \\__/   \\__/     |___| |___/  \\___| /_/‾\\_\\ |_|   |___| |___/     \\___| /_/‾\\_\\ |___| |___|     ✨'
            ]
    
    def __call__(self, _player: int | None = state.player_turn):
        """updates actions based on given player's position"""

        # state.chance + C.C card actions
        if state.player[_player]["pos"] in [7, 22, 36]:
            state.refresh_board.action = "chance notice"

            print(state.chance.art[0])
            print(f"    {state.chance.art[1]}")
            print(f"    {state.chance.art[2]}")
            print()
            print(f"    === {state.chance.draw_card()} ===\n\n    ", end="")

            if state.online_config.game_strt_event.is_set():
                send_data("carddrawn:state.chance")

        elif state.player[_player]["pos"] in [2, 17, 33]:
            state.refresh_board.action = "community chest notice"

            print(state.community_chest.art[0])
            print(f"    {state.community_chest.art[1]}")
            print(f"    {state.community_chest.art[2]}")
            print()
            print(f"    === {state.community_chest.draw_card()} ===\n\n    ", end="")

            if state.online_config.game_strt_event.is_set():
                send_data("carddrawn:cc")

        # income & super tax
        elif state.player[_player]["pos"] == 4:
            state.player[state.player_turn]["$$$"] -= 200

        elif state.player[_player]["pos"] == 38:
            state.player[state.player_turn]["$$$"] -= 100

        # go to jail space
        elif state.player[_player]["pos"] == 30:
            self.send_to_jail()

        # properties
        elif state.player[_player]["pos"] not in [0, 10, 20, 40]:
            self.rent_mgmt(_player)

    def rent_mgmt(
            self, _player: int, 
            rent_multi: int | None = 1,
            rent_fixed: int | None = None):
        """
        determines rent owed, or if the property can be bought.

        rent_fixed is applied equally to upgraded properties 
        (except mortgaged), and is applied alongside rent_multi.

        rent_multi overrides utility multiplier
        """

        _prop = state.prop_from_pos[state.player[_player]["pos"]]
        _owner = state.property_data[_prop]["owner"]
        if _owner == None:
            state.refresh_board.action = "property"
            return

        elif state.property_data[_prop]["upgrade state"] == -1:
            return

        elif rent_fixed != None:
            state.player[_player]["$$$"] -= rent_fixed * rent_multi
            state.player[_owner]["$$$"] += rent_fixed * rent_multi
                 
        elif state.property_data[_prop]["type"] == "utility":

            # if the player ownes both utilities (rent = 10x dice roll)
            if state.property_data[7]["owner"] == _owner and state.property_data[10]["owner"] == _owner:
                    
                # if the multiplier is default (1), it is changed to 10
                if rent_multi == 1: rent_multi = 10
                state.player[_player]["$$$"] -= (self.dice_value[1] + self.dice_value[2]) * rent_multi
                state.player[_owner]["$$$"] += (self.dice_value[1] + self.dice_value[2]) * rent_multi
            else:
                if rent_multi == 1: rent_multi = 10
                state.player[_player]["$$$"] -= (self.dice_value[1] + self.dice_value[2]) * rent_multi
                state.player[_owner]["$$$"] += (self.dice_value[1] + self.dice_value[2]) * rent_multi

        elif state.property_data[_prop]["type"] == "station":

            # counts how many stations owned to determine rent
            num = 0
            for i in [2, 10, 17, 25]:
                if state.property_data[i]["owner"] == _owner: num += 1
            state.player[_player]["$$$"] -= state.station_rent[num] * rent_multi
            state.player[_owner]["$$$"] += state.station_rent[num] * rent_multi
                
        # properties with houses or hotels
        elif state.property_data[_prop]["upgrade state"] > 2:

            # eg: if upgrade_state = 3; key would be "h1"
            key = f"h{state.property_data[_prop]['upgrade state'] - 2}"
            state.player[_player]["$$$"] -= state.property_data[_prop][key] * rent_multi
            state.player[_owner]["$$$"] += state.property_data[_prop][key] * rent_multi

        # properties in a colour set
        elif state.property_data[_prop]["upgrade state"] == 2:
            state.player[_player]["$$$"] -= state.property_data[_prop]["rent"] * 2 * rent_multi
            state.player[_owner]["$$$"] += state.property_data[_prop]["rent"] * 2 * rent_multi

        elif state.property_data[_prop]["upgrade state"] == 1:
            state.player[_player]["$$$"] -= state.property_data[_prop]["rent"] * rent_multi
            state.player[_owner]["$$$"] += state.property_data[_prop]["rent"] * rent_multi

        if state.player[_player]["$$$"] < 0:
            state.player_is_broke(_player, _owner)

    def remove_from_jail(self, _player: int | None = state.player_turn):
        """moves player from jail to just visiting"""

        state.player[_player]["pos"] = 10
        state.player[_player]["jail time"] = 0
        state.player[_player]["status"] = "playing"

        # updates the board
        update_player_position(10)
        update_player_position(40, "remove")

        state.refresh_board()

    def send_to_jail(self, _player: int | None = state.player_turn):
        """sends given player to jail, doesn't refresh board"""
        state.player[state.player_turn]["last pos"] = state.player[state.player_turn]["pos"]
        state.player[state.player_turn]["pos"] = 40
        state.player[state.player_turn]["status"] = "jail"
        
        self.dice_rolled = True

        update_player_position(40)
        update_player_position(state.player[state.player_turn]["last pos"], "remove")

    def start_roll(self):
        """main entry to start dice roll animation"""
        self.dice_rolling_state = 1 # starts first dice roll
        self.dice_countdown = 10

        self.dice_value[1] = randint(1, 6)
        print("┌───────────┐")
        print("    │           │")
        print(f"    {self.dice_image_frame[self.dice_value[1]][0]}")
        print(f"    {self.dice_image_frame[self.dice_value[1]][1]}")
        print(f"    {self.dice_image_frame[self.dice_value[1]][2]}")
        print("    │           │")
        print("    └───────────┘")

        # moves the cursor (text output location) to the middle of the die
        print("\x1b[6F")

        while self.dice_rolling_state != "off":
            sleep(150)
            self.dice_countdown -= 1

            if self.dice_rolling_state == 1:

                # generates random dice value, different to the last number
                x = randint(1, 6)
                while self.dice_value[1] == x: x = randint(1, 6)
                self.dice_value[1] = x

                # changes displayed value
                for i in range(3): print(f"    {self.dice_image_frame[self.dice_value[1]][i]}")
        
                # moves the cursor back to the middle of the die
                print("\x1b[4F")

            elif self.dice_rolling_state == 2:

                x = randint(1, 6)
                while self.dice_value[2] == x: x = randint(1, 6)
                self.dice_value[2] = x

                # since the 'doubles' text is next to the dice and not under them,
                # the calculations need to be performed while the lines are getting printed
                # different text appears if doubles are rolled to escape jail
                if self.dice_value[2] == self.dice_value[1] and self.dice_countdown == 0:
                    for i in range(3):
                        print(f"    {self.dice_image_frame[self.dice_value[1]][i]}   {self.dice_image_frame[self.dice_value[2]][i]}", end="", )
                    
                        if state.player[state.player_turn]["pos"] != 40: print(f"      {self.doubles_art[i]}")
                        else: print(f"      {self.escaped_go_art[i]}")

                else:
                    for i in range(3):
                        print(f"    {self.dice_image_frame[self.dice_value[1]][i]}   {self.dice_image_frame[self.dice_value[2]][i]}")
                
                # moves the cursor back to the middle of the die
                print("\x1b[4F")

            if self.dice_countdown == 0 and self.dice_rolling_state == 1:
                self.dice_value[2] = randint(1, 6)

                print("\x1b[3F")
                print("    ┌───────────┐   ┌───────────┐")
                print("    │           │   │           │")
                for i in range(3):
                    print(f"    {self.dice_image_frame[self.dice_value[1]][i]}   {self.dice_image_frame[self.dice_value[2]][i]}")
                print("    │           │   │           │")
                print("    └───────────┘   └───────────┘")
                print("\x1b[6F")

                self.dice_rolling_state = 2
                self.dice_countdown = 10

            elif self.dice_countdown == 0:
                self.dice_rolling_state = "off"

        # gives player time to check roll (after next logic)
        print("\x1b[5E")
        print("    === [Enter] to continue ===\n\n    ", end = "")

        state.refresh_board.action = "dice_roll_accept"

    def move(self):
        """start player movement around board, performs movement logic"""

        # this is updating the player's last position, so that the player's icon can be removed from the board
        state.player[state.player_turn]["last pos"] = state.player[state.player_turn]["pos"]

        # increases the doubles streak the player has, or resets it to 0
        if self.dice_value[1] == self.dice_value[2]:
            self.doubles_count += 1
        else:
            self.doubles_count = 0

        # if player rolls 3 doubles in a row, they're sent to jail
        if self.doubles_count == 3:
            state.player_action.send_to_jail()
            state.refresh_board()
            return

        # determines player movement length
        self.player_roll_itr = iter(range(self.dice_value[1] + self.dice_value[2]))

        if state.player[state.player_turn]["status"] == "jail":
            if self.doubles_count == 0:
                state.player[state.player_turn]["jail time"] += 1

                # cancels the player movement
                self.dice_rolled = True
        
            # the player escapes jail if they roll doubles
            else:
                self.remove_from_jail(state.player_turn)
                
                # a player that escapes jail gets to go again
                self.doubles_count = 0
                self.dice_rolled = False
            
            state.refresh_board()
            return # stops movement and position change

        # this is adding the dice roll's value to the player's position
        state.player[state.player_turn]["pos"] = (state.player[state.player_turn]["pos"] + self.dice_value[1] + self.dice_value[2])

        # makes sure that the player's position is valid
        if state.player[state.player_turn]["pos"] >= 40:
            state.player[state.player_turn]["pos"] -= 40

        while True:
            try:
                # determines what space the player is added to
                space = next(self.player_roll_itr) + state.player[state.player_turn]["last pos"] - 39

            # once the iterator has ran out the player is at the 
            # correct spot and the board will stop being refreshed
            except StopIteration:

                # only happens once the player passes go and their position is reset
                # extra check if the player leaves jail to stop passed go text
                if state.player[state.player_turn]["pos"] < state.player[state.player_turn]["last pos"] and state.player[state.player_turn]["last pos"] != 40:
                    state.player[state.player_turn]["$$$"] += 200
                    state.refresh_board.passed_go = True

                state.player_action(state.player_turn)
                   
                self.dice_rolling_state = "off"
                if self.doubles_count in [0, 3]:
                    self.dice_rolled = True

                # board isn't displayed if state.chance/community chest displays message
                if not (state.refresh_board.action in ("chance notice", "community chest notice")): state.refresh_board()
                return

            else:
                if space < 0: space += 40
                update_player_position(space)

                # removes player from previous space, but if space is negative, add 40,
                # for when the player passes go (eg: currently at space 0, remove from 39)
                space -= 1
                if space < 0: space += 40
                update_player_position(space, "remove")

                sleep(500)
                state.refresh_board()


class trade_screen_class(utils.parent_class):
    """stores all necessary functions for trading"""
    def __init__(self):
        self.player_1 = {"player": None, "$$$": 0, "props": [], "accepted?": False}
        self.player_2 = {"player": None, "$$$": 0, "props": [], "accepted?": False}

        self.nothing_art = r"""

                                                ╱─────────╮
                                                ╲──────╮  │
                                                       │  │
                                                       │  │
                                                       │  │
                                                       └──┘
















                    ┌──┐       
                    │  │       
                    │  │       
                    │  │       
                    │  ╰──────╲
                    ╰─────────╱"""
        self.prop_prop_money_art = r"""
            ┌──────────────────────────────┐
            │ 🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦 │
            │ 🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦 │    ╱─────────╮
            │ 🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦 │    ╲──────╮  │
            │ 🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦 │           │  │
            │                              │           │  │
            │                              │           │  │
            │                              │           └──┘
            │                              │
            │                              │───────────────────┐
            │                              │🟦🟦🟦🟦🟦🟦🟦🟦🟦 │
            │                              │🟦🟦🟦🟦🟦🟦🟦🟦🟦 │
            │                              │🟦🟦🟦🟦🟦🟦🟦🟦🟦 │
            │                              │🟦🟦🟦🟦🟦🟦🟦🟦🟦 │
            │                              │                   │
            │                              │                   │
            │                              │                   │
            │                              │    ┌──────────────────────────────────────────────┐
            │                              │   ┌──────────────────────────────────────────────┐│
            │                              │  ┌──────────────────────────────────────────────┐││
            │                              │  │ |---------------| MONOPOLY |---------------| │││
            │                              │  │ | ┌───┐         ‾‾╱‾‾‾‾‾‾╲‾‾        ┌─V─_┐ | │││
            └──────────────────────────────┘  │ | │100│      __╱‾‾        ‾‾╲__     │(¯¯❬│ | │││
                                │             │ | └───┘     ╱ ____   __    __  ╲    └◿°°─┘ | │││
                 ┌──┐           │             │ |          | /_| |  /  \  /  \  |          | │││
                 │  │           │             │ |          |  _| |_| () || () | |          | │││
                 │  │           │             │ | ┌_/\_┐    \_|___| \__/  \__/_╱     ┌───┐ | │││
                 │  │           │             │ | │|__|│       ╲__        __╱        │100│ | │││
                 │  ╰──────╲    │             │ | └────┘          ╲______╱           └───┘ | ││┘
                 ╰─────────╱    │             │ |------------------------------------------| │┘
                                │             └──────────────────────────────────────────────┘
                                └──────────────────────────────┘"""

        self.action = None
        self.is_trade = False
        self.queued_prop = None
        self.curr_player = self.player_1

    def __call__(self, player_: int | None = state.player_turn, queued_prop: int | None = None):
        """
        adds the given player as player 1 of the bid,
        and prompts the player who they would like to trade with.
        
        If there isn't first player, then the current player is chosen

        If a property is given, it will be added to player one's offer,
        after other trading player has been selected
        """

        try: self.player_1["player"] = int(player_)
        except ValueError: self.player_1["player"] = int(state.player_turn)
    
        if queued_prop:
            self.player_1["props"].append(queued_prop)

        clear_screen()
        self.action = "player select"

        state.current_screen = self.__name__

        self.other_players = []
        self.spacing = []

        print("    ╔════════════════════════════════════════════════════════════════╗")
        print("    ║                                                                ║")
        print("    ║                  CHOOSE PLAYER TO TRADE WITH:                  ║")
        print("    ║                                                                ║")
        print("    ╚════════════════════════════════════════════════════════════════╝")
        print()

        # gets the other players, adds them as available options
        for player_ in state.player.keys():
            if player_ != self.player_1["player"]: 
                self.other_players.append(str(player_))
                self.spacing.append(3)

        self.other_players.append("Back")
        self.spacing.append(6)
        self.spacing[0] = 4

        for i in create_button_prompts(self.other_players, spacing = self.spacing): print(i)
        print("\n    ", end = "")

    def display_trade_window(self):
        """displays the current player offers"""

        state.current_screen = self.__name__

        # wow an actually valid use for a lambda expression :O
        tick = lambda p: '✅' if self.__getattribute__(f"player_{p}")['accepted?'] else '  '

        self.action = "offer screen"
        clear_screen()
        print()
        print("    ╔═══════════════════════════════╗ ╔═══════════════════════════════╗")
        print("    ║                               ║ ║                               ║")
        print(f"    ║     {tick("1")} PLAYER {self.player_1['player']} OFFER:        ║ ║     {tick("2")} PLAYER {self.player_2['player']} OFFER:        ║")
        print("    ║                               ║ ║                               ║")

        extra_space = ["", ""]
        for i in range(28 - len(str(self.player_1["$$$"]))):
            extra_space[0] += " "

        for i in range(28 - len(str(self.player_2["$$$"]))):
            extra_space[1] += " "

        print(f"    ║ ${self.player_1['$$$']}{extra_space[0]} ║ ║ ${self.player_2['$$$']}{extra_space[1]} ║")
        print("    ║                               ║ ║                               ║")
               
        # ands extra space between the properties and the border
        add_bottom_line = False

        # prints offered properties, space is left blank if run out
        for i in range(max(len(self.player_1["props"]), len(self.player_2["props"]))):

            # see previous comment
            add_bottom_line = True

            extra_space = ["", ""]
            is_mortgaged = [" ", " "]
            property_ = ["", ""]
            seperator = ["│","│"]

            # attempts to display a new line with the players' properties.
            # if one has more than another, the space is blank
            try:
                prop_ = state.property_data[self.player_1["props"][i]]
            except IndexError:
                extra_space[0] = "                     "
                property_[0] = ""
                seperator[0] = " "
            else:
                property_[0] = prop_["name"]
                for ii in range(21 - len(prop_["name"])):
                    extra_space[0] += " "

                if prop_["upgrade state"] == -1:
                    is_mortgaged[0] = "M"

            # performed for player 2 now
            try:
                prop_ = state.property_data[self.player_2["props"][i]]             
            except IndexError:
                extra_space[1] = "                     "
                property_[1] = ""
                seperator[1] = " "
            else:
                property_[1] = prop_["name"]
                for ii in range(21 - len(prop_["name"])):
                    extra_space[1] += " "

                if prop_["upgrade state"] == -1:
                    is_mortgaged[1] = "M"
                
            print(f"    ║ {property_[0]}{extra_space[0]} {seperator[0]} {is_mortgaged[0]}     ║ ║ {property_[1]}{extra_space[1]} {seperator[1]} {is_mortgaged[1]}     ║")

            if add_bottom_line:
                print("    ║                               ║ ║                               ║")

        print("    ╚═══════════════════════════════╝ ╚═══════════════════════════════╝")
        print()
        
        props = False
        for i in state.property_data:
            if i["owner"] == self.curr_player["player"]: props = True

        if self.curr_player == self.player_1:
            _prompt = f"Swap to P{self.player_2['player']}"
        else:
            _prompt = f"Swap to P{self.player_1['player']}"

        for i in create_button_prompts(
                ["Offer money", "Properties", _prompt, "Accept trade", "Cancel"],
                [True, props, True, True, True],
                [4, 3, 3, 3, 6]
            ):
            print(i)
        print("\n    ", end = "")

    def add_prop_offer(self, _property):
        """
        adds the property to a player's offer dependent on ownership.
        if the owner isn't one of the players trading, nothing happens.
        """
        if state.property_data[_property]["owner"] == self.player_1["player"]:
            self.player_1["props"].append(_property)
        elif state.property_data[_property]["owner"] == self.player_2["player"]:
            self.player_2["props"].append(_property) 

    def trade_completed(self):
        """displays trade confirmation and handles transferring logic"""
        clear_screen()

        # displays trade successful art
        # if players trade nothing, this variant appears
        if not self.player_1["props"] and not self.player_2["props"] and \
           self.player_1["$$$"] == self.player_2["$$$"] == 0:
            print(self.nothing_art)
        else:
            print(self.prop_prop_money_art)
        print("\n    === trade completed [Enter] ===\n\n    ", end = "")
        self.action = "trade complete"

        # adds the players offers to the opposite player
        state.player[self.player_1["player"]]["$$$"] += self.player_2["$$$"]
        state.player[self.player_2["player"]]["$$$"] += self.player_1["$$$"]

        # subtracts the players offers from their own money
        state.player[self.player_1["player"]]["$$$"] -= self.player_1["$$$"]
        state.player[self.player_2["player"]]["$$$"] -= self.player_2["$$$"]

        # updates the properties
        # (I know this is disgustingly long and poorly coded)
        for player_prop in self.player_1["props"]:
            state.property_data[player_prop]["owner"] = self.player_2["player"]  
            if state.property_data[player_prop]["type"] == "station":
                continue

            colour_set = []

            for sub_prop in self.player_1["props"]:
                if not ("colour set" in state.property_data[sub_prop].keys() and "colour set" in state.property_data[player_prop].keys()):
                    continue

                if state.property_data[sub_prop]["colour set"] == state.property_data[player_prop]["colour set"]:
                    colour_set.append(sub_prop)
                         
            # ensures that if all properties in a colour set are traded,
            # they keep relevant upgrade state, otherwise return to default
            if (len(colour_set) == 3 and state.property_data[player_prop]["colour set"] not in [0, 7]) \
                or (len(colour_set) == 2 and state.property_data[player_prop]["colour set"] in [0, 7]):

                for _prop in colour_set:
                    if _prop["upgrade state"] != -1:
                        _prop["upgrade state"] = 2
            else:
                for _prop in colour_set:
                    if _prop["upgrade state"] == 2:
                        _prop["upgrade state"] = 1
       
        for player_prop in self.player_2["props"]:
            state.property_data[player_prop]["owner"] = self.player_1["player"]  
            if state.property_data[player_prop]["type"] == "station":
                continue

            colour_set = []

            for sub_prop in self.player_1["props"]:
                if not ("colour set" in state.property_data[sub_prop].keys() and "colour set" in state.property_data[player_prop].keys()):
                    continue

                if state.property_data[sub_prop]["colour set"] == state.property_data[player_prop]["colour set"]:
                    colour_set.append(sub_prop)
                         
            if (len(colour_set) == 3 and state.property_data[player_prop]["colour set"] not in [0, 7]) \
                or (len(colour_set) == 2 and state.property_data[player_prop]["colour set"] in [0, 7]):

                for _prop in colour_set:
                    if _prop["upgrade state"] != -1:
                        _prop["upgrade state"] = 2
            else:
                for _prop in colour_set:
                    if _prop["upgrade state"] == 2:
                        _prop["upgrade state"] = 1
        
        self.is_trade = False

        # (debt checks happen after user accept,
        # hence player_1/2 isn't cleared yet)

    def input_management(self, user_input):
        if user_input in ["c", "C"]:

            # clears player offers
            self.player_1 = {"player": None, "$$$": 0, "props": [], "accepted?": False}
            self.player_2 = {"player": None, "$$$": 0, "props": [], "accepted?": False}
            self.is_trade = False
            self.action = None

            state.refresh_board()

        elif self.action == "player select":
            try:
                int(user_input)
            except ValueError:
                
                if user_input in ["b", "B"]:
                    self.player_1 = {"player": None, "$$$": 0, "props": [], "accepted?": False}
                    self.player_2 = {"player": None, "$$$": 0, "props": [], "accepted?": False}
        
                    self.is_trade = False
                    self.action = None
                    state.refresh_board()

                if self.action2 != "message":
                    return

                # if the action is 'message' (player wants to trade with themselves)                
                if user_input in ["p", "P"]:
                    self.player_2 = self.player_1
                    self.action2 = None
                    self.display_trade_window()

                    print("=== if you insist... ===\n\n    ", end="")

                elif user_input in ["o", "O"]:

                    # clears the conversation and recreates prompts
                    self(self.player_1["player"], self.queued_prop)
                    self.action2 = None
            else:
                if user_input in self.other_players:
                    if state.online_config.game_strt_event.is_set():
                        send_data(f"traderequest:{user_input}")
                        self.action = "await online accept"
                        return
                    self.player_2["player"] = int(user_input)
                    self.action = None
                    self.is_trade = True

                    self.curr_player = self.player_1
                    self.display_trade_window()

                elif int(user_input) == self.player_1["player"]: 
                    print("\n    === you can't trade with yourself! ===\n\n")
                    for i in create_button_prompts(["Pleeeeeeease", "Ok"]): print(i)
                    print("\n    ", end="")
                    self.action2 = "message"

                else:
                    print("\n    === that player does not exist ===\n\n    ", end = "")
         
        elif self.action == "offer screen":
            if user_input in ["o", "O"]:
                self.action = "money"
                print(f"\n    === player {self.curr_player["player"]}, enter cash offer (you can exchange more money than you currently have) ===\n\n    ", end = "")

            elif user_input in ["p","P"]:
                
                has_properties = False
                for i in state.property_data:
                        if i["owner"] == self.curr_player["player"]:
                            has_properties = True
                            break
                if has_properties == True:
                    state.display_property_list(self.curr_player["player"])
                else:
                    print("\n    === you have no properties to view ===\n\n    ", end = "")

            elif user_input in ["s", "S"]:
                if self.curr_player == self.player_1:
                    self.curr_player = self.player_2
                else:
                    self.curr_player = self.player_1
                self.display_trade_window()

            elif user_input in ["a", "A"]:
                # marks the user as having accepted, switches to other player
                if self.curr_player == self.player_1:
                    self.player_1["accepted?"] = True
                    self.curr_player = self.player_2
                else: 
                    self.player_2["accepted?"] = True                    
                    self.curr_player = self.player_1

                if self.curr_player["accepted?"] == True:
                    self.trade_completed()
                else:
                    self.display_trade_window()

            else:
                print("\n    === command not recognised ===\n\n    ", end = "")
                    
        elif self.action == "money":
            try:
                if self.curr_player == self.player_1:
                    self.player_1["$$$"] = int(user_input)
                else:
                    self.player_2["$$$"] = int(user_input)
                self.display_trade_window()
             
            except ValueError:
                print("\n    === command not recognised. please enter a number (you can enter [0]) ===\n\n   ", end = "")

        elif self.action == "trade complete":
            self.action = None

            broke_alert = False
            # ensures that if a player is in debt,
            # the appropriate screen is raised.
            if state.player[self.player_1["player"]]["$$$"] < 0:
                broke_alert = True
                state.player_is_broke(self.player_1["player"], self.player_2["player"])

            elif state.player[self.player_2["player"]]["$$$"] < 0:
                broke_alert = True
                state.player_is_broke(self.player_2["player"], self.player_1["player"])
     
            # clears player offers
            self.player_1 = {"player": None, "$$$": 0, "props": [], "accepted?": False}
            self.player_2 = {"player": None, "$$$": 0, "props": [], "accepted?": False}

            # board isn't shown if a player has fallen into debt
            if broke_alert == False:
                state.refresh_board()
        else:
            print("\n    === command not recognised ===\n\n    ", end = "")