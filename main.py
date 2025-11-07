"""a game of monopoly playable in a terminal window"""

from time import time # type: ignore # used to determine total play time, for sleep() type
import wcwidth # used to determine if names is correct width
from better_iterator import better_iter # used for the player turn

import game
import online
import utils
from utils import create_prompts, clear_screen, update_player_position
import cards
import state

# most modules require functions from each other, to avoid circular imports,
# main creates instances for state and provides required functions as specified
state.chance = cards.chance_class()
state.community_chest = cards.community_chest_class()

state.refresh_board = game.refresh_board_class()
state.display_property = game.display_property_class()
state.display_property_list = game.display_property_list_class()
state.player_action = game.player_action_class()
state.player_is_broke = game.player_is_broke_class()
state.trade_screen = game.trade_screen_class()

state.online_config = online.online_config_class()

for module in [online, game, cards, utils]:

    # some modules don't require any functions
    if not "__required__" in module.__dict__.keys():
        continue
    for func in module.__required__:
        if "." in func: _, name = func.split(".")
        else: name = func

        module.__dict__.update({name: eval(func)})


# setting the terminal name
print("\033]1;💰 Text-Based Monopoly 💰\007")


class homescreen_class(utils.parent_class):
    def __init__(self):
        self.action = None

    def __call__(self):
        """displays the home screen"""
        clear_screen()

        state.current_screen = self.__name__

        print("")
        print(r"       ___  ___        _____     _____ ____     _____      _____      _____     ____     ___  ___"    )
        print(r"      ╱   ╲╱   ╲      ╱     ╲    │    ╲│  │    ╱     ╲    │  _  \    ╱     ╲    │  │     ╲  \/  ╱ │ coded by:")
        print(r"     ╱  /╲  ╱\  ╲    │  (_)  │   │  ╲  ╲  │   │  (_)  │   │  ___/   │  (_)  │   │  │__    ╲_  _╱  │ James E.")
        print(r"    ╱__/  ╲╱  \__╲    ╲_____╱    |__│╲____|    ╲_____╱    |__|       ╲_____╱    |_____|    |__|   │ 2024, 2025")
        print("")
        print("    ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────")
        print("")

        # checks if a save file exists
        saved_game = False
        try: x = open("save_file.james", encoding = "utf-8")
        except: pass
        else: x.close(); saved_game = True
        
        for i in create_prompts(["Start game", "Continue", "Online", "Exit"], [True, saved_game, True, True]):
            print(i)
        print("\n    ", end = "")

    def input_management(self, user_input):
        if user_input in ["devmode", "dev mode"]:
            state.dev_mode = True
            print("\n    === dev mode enabled ===\n\n    ", end = "")

        elif user_input in ["s", "S"]:
            state.new_game_select()

        elif user_input in ["c", "C"]:
              utils.read_save("save_file.james", "utf-8") 
              state.display_game_notice()

        elif user_input in ["o", "O"]: # ['l', 'L']
            state.online_config()

        elif "nick" in user_input.lower():

            # in dedication to Nick Tho, who always uses his phone with night-shift enabled at the maximum intensity
            # changes the background to yellow
            print("\x1b[43m")
            self()

            print("=== Nick Tho always uses night-shift on maximum intensity, I'm not trying to be racist ===\n")
            for i in create_prompts(["I'm offended", "Makes sense"]): print(i)
            print("\n    ", end = "")
            self.action = "nicktho"

        elif user_input in ["i", "I"] and self.action == "nicktho":
            self()
            print("\n    === get over it. ===\n\n    ", end = "")
            
        elif user_input in ["m", "M"] and self.action == "nicktho":
            self()
            print("\n    === wow thank you for understanding and not overreacting. ===\n\n    ", end = "")

        elif user_input in ["e", "E"]:
            print("\n    === bruh. Just close the window it's not that hard ===\n\n    ", end="")

        else:
            print("\n    === command not recognised ===\n\n    ", end = "")


state.homescreen = homescreen_class()


class display_game_notice_class(utils.parent_class):
    def __call__(self):
        state.current_screen = self.__name__

        clear_screen()

        print()
        print("    ╔════════════════════════════════════════════════════════════════╗")
        print("    ║                                                                ║")
        print("    ║                             NOTICE:                            ║")
        print("    ║                                                                ║")
        print("    ║                 To display the board properly,                 ║")
        print("    ║           you may need to resize text or the window            ║")
        print("    ║                                                                ║")
        print("    ║    TIP: you can skip certain animations by pressing [Enter]    ║")
        print("    ║                                                                ║")
        print("    ║                             [Enter]                            ║")
        print("    ╚════════════════════════════════════════════════════════════════╝")
        print()
        print("    |<──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────>|")
        print()
        print("    the board is the length of this line, adjust until the line doesn't wrap around your screen.\n    ", end = "")

    def input_management(self, user_input):
        update_player_position(0)
        state.start_time = time()
        state.refresh_board()


state.display_game_notice = display_game_notice_class()


class new_game_select_class(utils.parent_class):
    def __init__(self):
        self.action = None

    def __call__(self):
        clear_screen()

        state.current_screen = self.__name__

        print()
        if self.action == "name input":
            print("    === enter player icons ===")
        else:
            print("    === choose number of players ===")
        print()

        if state.players_playing == 0:
            button_states = [True, True, True, True]
        elif state.players_playing == 2:
            button_states = [True, False, False, True]
        elif state.players_playing == 3:
            button_states = [False, True, False, True]
        elif state.players_playing == 4:
            button_states = [False, False, True, True]

        for i in create_prompts(["2 players", "3 players", "4 players", "Back"], button_states, [4, 3, 3, 6]):
            print(i)
        print()

        # this is displaying each players's character
        if self.action != "name input":
            print("    ", end="")
            return
        print("    ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────")
        print("")

        if state.player_turn == 1:
            print("    Player 1: ", end="")
        elif state.player_turn == 2:
            print(f'    Player 1: {state.player[1]["char"]}')
            print("    Player 2: ", end="")
        elif state.player_turn == 3:
            print(f'    Player 1: {state.player[1]["char"]}')
            print(f'    Player 2: {state.player[2]["char"]}')
            print("    Player 3: ", end="")
        elif state.player_turn == 4:
            print(f'    Player 1: {state.player[1]["char"]}')
            print(f'    Player 2: {state.player[2]["char"]}')
            print(f'    Player 3: {state.player[3]["char"]}')
            print("    Player 4: ", end="")

    def input_management(self, user_input):

        if user_input in ["2", "3", "4"]:

            state.players_playing = int(user_input)
            state.player_turn = better_iter(range(1, state.players_playing + 1), True)

            self.action = "name input"
            state.player = {}

            for i in range(state.players_playing):

                # players start at 1, not 0
                state.player[i + 1] = {
                    "char": "",
                    "$$$": 1500,
                    "pos": 0,

                    # this is so that the player's icon can be removed from the board
                    "last pos": 0,
                    "jail passes": 0,
                    "jail time": 0,
                    "house total": 0,
                    "hotel total": 0,
                    "total properties": 0,
                    "status": "playing",
                }

            self()

        elif user_input in ["b", "B"]:
            self.action = None
            state.players_playing = 0
            state.homescreen()
            
        # recording entered names
        elif self.action == "name input":

            # enforces 2 characters width for name
            name_width = wcwidth.wcswidth(user_input)
            
            if user_input in ["  ", r"\\"]:
                print("\n    === nice try. ===\n\n    ", end = "")
                return
            
            elif name_width == -1:
                print("\n    === how have you even managed to get a string this wide?? try again. ===\n\n    ", end="")
                return
            elif name_width > 2:
                print("\n    === icon too large, try a different icon (eg: '😊' or 'JE') ===\n\n    ", end="")
                return

            elif name_width < 2:
                print("\n    === icon too small, try a different icon (eg: '😊' or 'JE') ===\n\n    ", end="")
                return

            # in theory better_iters should use a dunder method automatically,
            # but player_turn is feeling uncooperative today
            state.player[int(state.player_turn)]["char"] = user_input
            next(state.player_turn)

            if state.player_turn == 1:
                self.action = None

                state.display_game_notice()
            else:
                self()
        else:
            print("\n    === command not recognised ===\n\n    ", end = "")


state.new_game_select = new_game_select_class()


state.homescreen()
while True:
    try: state.__dict__[state.current_screen].input_management(input())
    except KeyboardInterrupt: pass # stupid keyboard interrupts