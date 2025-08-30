"""
a game of monopoly playable in a text window.
can be executed as main program or imported
"""

import asyncio # needed for online (to get input and data at the same time)
from os import system, name # used for clearing the screen
from random import randint, shuffle # used for dice rolling, chance/CC card shuffling
from sys import exit # used to end the program
import socket # online communication
from time import time # used to determine total play time, for sleep()
from unicodedata import east_asian_width as width # used to determine if names is correct width
from better_iterator import better_iter, tripple_affirmative # used for the player turn

# setting the terminal name
print("\033]1;💰 Text-Based Monopoly 💰\007")

# initialising variables
players_playing = 0
dev_mode = False
house_total = 32
hotel_total = 12
time_played = 0
game_version = 0.9
player_turn = None

globals().update({"skibidi skibidi hawk tuah": 67}) # this variable serves no purpose

# player icons can only appear in certain points here
# default space is blank but some special cases specified individually
player_display_location = [["          ", True] for i in range(41)]

player_display_location[7] = ["    ()    ", False] # False = irregular
player_display_location[22] = ["    / /   ", False]
player_display_location[36] = [ "  \\_|    ", False]
player_display_location[40] = [" ║ ║ ║ ║ ", False]

property_data = [{} for i in range(28)]

# (note: colour set rent is double normal rent, isn't recorded.
#  mortgage/unmortgage value based on street value, isn't recorded)
property_data[0]  = {"name": "Old Kent Road"        , "type": "property", "street value": 60 , "owner": None, "upgrade state": 0, "colour set": 0, "rent": 2 , "h1 rent": 10 , "h2 rent": 30 , "h3 rent": 90  , "h4 rent": 160 , "h5 rent": 250 , "house cost": 50 }
property_data[1]  = {"name": "Whitechapel"          , "type": "property", "street value": 60 , "owner": None, "upgrade state": 0, "colour set": 0, "rent": 4 , "h1 rent": 20 , "h2 rent": 60 , "h3 rent": 180 , "h4 rent": 320 , "h5 rent": 450 , "house cost": 50 }
property_data[2]  = {"name": "Kings Cross Station"  , "type": "station" , "street value": 200, "owner": None, "upgrade state": 0}
property_data[3]  = {"name": "The Angel Islington"  , "type": "property", "street value": 100, "owner": None, "upgrade state": 0, "colour set": 1, "rent": 6 , "h1 rent": 30 , "h2 rent": 90 , "h3 rent": 270 , "h4 rent": 400 , "h5 rent": 550 , "house cost": 50 }
property_data[4]  = {"name": "Euston Road"          , "type": "property", "street value": 100, "owner": None, "upgrade state": 0, "colour set": 1, "rent": 6 , "h1 rent": 30 , "h2 rent": 90 , "h3 rent": 270 , "h4 rent": 400 , "h5 rent": 550 , "house cost": 50 }
property_data[5]  = {"name": "Pentonville Road"     , "type": "property", "street value": 120, "owner": None, "upgrade state": 0, "colour set": 1, "rent": 8 , "h1 rent": 40 , "h2 rent": 100, "h3 rent": 300 , "h4 rent": 450 , "h5 rent": 600 , "house cost": 50 }
property_data[6]  = {"name": "Pall Mall"            , "type": "property", "street value": 140, "owner": None, "upgrade state": 0, "colour set": 2, "rent": 10, "h1 rent": 50 , "h2 rent": 150, "h3 rent": 450 , "h4 rent": 625 , "h5 rent": 750 , "house cost": 100}
property_data[7]  = {"name": "Electric Company"     , "type": "utility" , "street value": 150, "owner": None, "upgrade state": 0}
property_data[8]  = {"name": "Whitehall"            , "type": "property", "street value": 140, "owner": None, "upgrade state": 0, "colour set": 2, "rent": 10, "h1 rent": 50 , "h2 rent": 150, "h3 rent": 450 , "h4 rent": 625 , "h5 rent": 750 , "house cost": 100}
property_data[9]  = {"name": "Northumberland Avenue", "type": "property", "street value": 160, "owner": None, "upgrade state": 0, "colour set": 2, "rent": 12, "h1 rent": 60 , "h2 rent": 180, "h3 rent": 500 , "h4 rent": 700 , "h5 rent": 900 , "house cost": 100}
property_data[10] = {"name": "Marylebone Station"   , "type": "station" , "street value": 200, "owner": None, "upgrade state": 0}
property_data[11] = {"name": "Bow Street"           , "type": "property", "street value": 180, "owner": None, "upgrade state": 0, "colour set": 3, "rent": 14, "h1 rent": 70 , "h2 rent": 200, "h3 rent": 550 , "h4 rent": 750 , "h5 rent": 950 , "house cost": 100}
property_data[12] = {"name": "Marlborough Street"   , "type": "property", "street value": 180, "owner": None, "upgrade state": 0, "colour set": 3, "rent": 14, "h1 rent": 70 , "h2 rent": 200, "h3 rent": 550 , "h4 rent": 750 , "h5 rent": 950 , "house cost": 100}
property_data[13] = {"name": "Vine Street"          , "type": "property", "street value": 200, "owner": None, "upgrade state": 0, "colour set": 3, "rent": 16, "h1 rent": 80 , "h2 rent": 220, "h3 rent": 600 , "h4 rent": 800 , "h5 rent": 1000, "house cost": 100}
property_data[14] = {"name": "Strand"               , "type": "property", "street value": 220, "owner": None, "upgrade state": 0, "colour set": 4, "rent": 18, "h1 rent": 90 , "h2 rent": 250, "h3 rent": 700 , "h4 rent": 875 , "h5 rent": 1050, "house cost": 150}
property_data[15] = {"name": "Fleet Street"         , "type": "property", "street value": 220, "owner": None, "upgrade state": 0, "colour set": 4, "rent": 18, "h1 rent": 90 , "h2 rent": 250, "h3 rent": 700 , "h4 rent": 875 , "h5 rent": 1050, "house cost": 150}
property_data[16] = {"name": "Trafalgar Square"     , "type": "property", "street value": 240, "owner": None, "upgrade state": 0, "colour set": 4, "rent": 18, "h1 rent": 90 , "h2 rent": 250, "h3 rent": 700 , "h4 rent": 875 , "h5 rent": 1050, "house cost": 150}
property_data[17] = {"name": "Fenchurch St. Station", "type": "station" , "street value": 200, "owner": None, "upgrade state": 0}
property_data[18] = {"name": "Leicester Square"     , "type": "property", "street value": 260, "owner": None, "upgrade state": 0, "colour set": 5, "rent": 22, "h1 rent": 110, "h2 rent": 330, "h3 rent": 800 , "h4 rent": 975 , "h5 rent": 1150, "house cost": 150}
property_data[19] = {"name": "Coventry Street"      , "type": "property", "street value": 260, "owner": None, "upgrade state": 0, "colour set": 5, "rent": 22, "h1 rent": 110, "h2 rent": 330, "h3 rent": 800 , "h4 rent": 975 , "h5 rent": 1150, "house cost": 150}
property_data[20] = {"name": "Water Works"          , "type": "utility" , "street value": 150, "owner": None, "upgrade state": 0}
property_data[21] = {"name": "Piccadilly"           , "type": "property", "street value": 280, "owner": None, "upgrade state": 0, "colour set": 5, "rent": 24, "h1 rent": 120, "h2 rent": 360, "h3 rent": 850 , "h4 rent": 1025, "h5 rent": 1200, "house cost": 150}
property_data[22] = {"name": "Regent Street"        , "type": "property", "street value": 300, "owner": None, "upgrade state": 0, "colour set": 6, "rent": 26, "h1 rent": 130, "h2 rent": 390, "h3 rent": 900 , "h4 rent": 1100, "h5 rent": 1275, "house cost": 200}
property_data[23] = {"name": "Oxford Street"        , "type": "property", "street value": 300, "owner": None, "upgrade state": 0, "colour set": 6, "rent": 26, "h1 rent": 130, "h2 rent": 390, "h3 rent": 900 , "h4 rent": 1100, "h5 rent": 1275, "house cost": 200}
property_data[24] = {"name": "Bond Street"          , "type": "property", "street value": 320, "owner": None, "upgrade state": 0, "colour set": 6, "rent": 28, "h1 rent": 150, "h2 rent": 450, "h3 rent": 1000, "h4 rent": 1200, "h5 rent": 1400, "house cost": 200}
property_data[25] = {"name": "Liverpool St. Station", "type": "station" , "street value": 200, "owner": None, "upgrade state": 0}
property_data[26] = {"name": "Park Lane"            , "type": "property", "street value": 350, "owner": None, "upgrade state": 0, "colour set": 7, "rent": 35, "h1 rent": 175, "h2 rent": 500, "h3 rent": 1100, "h4 rent": 1300, "h5 rent": 1500, "house cost": 200}
property_data[27] = {"name": "Mayfair"              , "type": "property", "street value": 400, "owner": None, "upgrade state": 0, "colour set": 7, "rent": 50, "h1 rent": 200, "h2 rent": 600, "h3 rent": 1400, "h4 rent": 1700, "h5 rent": 2000, "house cost": 200}

# the amount of rent to number of stations dictionary
station_rent = {1: 25, 2: 50, 3: 100, 4: 200}

# this converts the player's position into the corresponding property
prop_from_pos = {1:0, 3:1, 5:2, 6:3, 8:4, 9:5, 11:6, 12:7, 13:8, 14:9,
    15:10, 16:11, 18:12, 19:13, 21:14, 23:15, 24:16, 25:17, 26:18, 27:19, 
    28:20, 29:21, 31:22, 32:23, 34:24, 35:25, 37:26, 39:27
}

def sleep(_time: int):
    """delays thread for inputted milliseconds"""
    start = time()
    _time = _time / 1000
    while time() - start < _time: pass


def clear_screen(sys: str | None = name):
    """do you really need a docstring for this?"""

    # developer mode disables screen clearing
    if dev_mode:  return

    if   sys == "nt"   : system("cls")
    elif sys == "posix": system("clear")
    else: raise Exception("bro what are you running this on??!!")


# I'm very proud of this use of typing hints
def create_button_prompts(
        prompts: list[str],
        prompt_state: list[bool] | None =  "default",
        spacing: list[int] | None = "default"
    ):
    """
    creates a list of ascii art that displays button-looking prompts.
    words should be a maximum of 12 characters long per button.

    prompt_state defaults to True, but buttons can have dashed outlines with False
    the default spacing is 4 spaces front, then 3 between buttons

     ________________
    |                | note that brackets and capitalisation are  
    |   [E]xample    | automatically applied to the first character.
    |________________| (designed for monospace fonts)

    """
    # creating the output list for the art
    button_list = ["", "", "", ""]
    extra_space = ["", ""]
    num = len(prompts)

    # if "prompt_state" or "spacing" is left to default,
    # its size is dependent on the amount of prompts
    if prompt_state == "default":
        prompt_state = []
        for i in range(num):
            prompt_state.append(True)

    if spacing == "default":
        spacing = [4]
        for i in range(num - 1):
            spacing.append(3)

    # cycles through the amount of prompts for the each layer 
    for i in range(num):
        for ii in range(spacing[i]): button_list[0] += " "
        if prompts[i] == "":
            button_list[0] += "                  "
        elif prompt_state[i] == True:
            button_list[0] += " ________________ "
        else:
            button_list[0] += "   __  __  __  __ "

    for i in range(num):
        for ii in range(spacing[i]): button_list[1] += " " 
        if prompts[i] == "":
            button_list[1] += "                  "
        elif prompt_state[i] == True:
            button_list[1] += "|                |"
        else:
            button_list[1] += "|                 "

    for i in range(num):

        extra_space = ["", ""]

        # this adds an extra space to each side for every two characters the prompt is from the maximum, rounded down
        for ii in range((12 - len(prompts[i])) // 2): extra_space[0] += " "

        # if an additional space is needed (instead of an extra 1 on each side) it is added to the right
        if len(prompts[i]) % 2 == 1:
            extra_space[1] = " "

        for ii in range(spacing[i]): button_list[2] += " "

        # tries to capitalise the first character,
        # but if the string is blank, is skipped
        try: x = prompts[i][0].upper()
        except IndexError: pass

        if prompts[i] == "":
            button_list[2] += "                  "

        elif prompt_state[i] == True:

            # centering the text with the extra space
            button_list[2] += f"|{extra_space[0]} [{x}]{prompts[i][1:]}{extra_space[1]} {extra_space[0]}|"
        else:
            button_list[2] += f" {extra_space[0]} [{prompts[i][0]}]{prompts[i][1:]}{extra_space[1]} {extra_space[0]}|"

    for i in range(num):
        for ii in range(spacing[i]): button_list[3] += " "

        if prompts[i] == "":
            button_list[3] += "                  "
        elif prompt_state[i] == True:
            button_list[3] += "|________________|"
        else:
            button_list[3] += "|  __  __  __  __ "

    return(button_list)


def update_player_position(_pos: int, _action = "add"):
    """
    updates the displayed segments where player is shown.
    action is either 'add' or 'remove', and the positions are 0-27
    """
    global player_display_location

    player_itr = better_iter(range(players_playing), start_index=-1)

    # records current player locations
    players_pos = []
    for item in player.items():
        players_pos.append(item[1]["pos"])

    # overrides player space with current space,
    # to ensure player is displayed spaces before actual location
    if _action == "add": players_pos[player_turn - 1] = _pos

    layout = {
        "_":{0: "          ", 1: "    p    ", 2: "  p  p  ", 3: " p p p ", 4: "p pp p"},
        7 : {0: "    ()    ", 1: " p ()    ", 2: " p () p ", 3: "pp() p ", 4: "pp()pp"},
        22: {0: "    / /   ", 1: " p / /   ", 2: " p / /p ", 3: "pp/ /p ", 4: "pp/ pp"},
        36: {0: "  \\_|    ", 1: r"  \_| p ", 2: r"p\_| p ", 3: r"p\_|pp", 4: "ppp|p" },
        40: {0: " ║ ║ ║ ║ " , 1: " ║ p║ ║ " , 2: " p║ ║p " , 3: " pp║p " , 4: "pp pp" }
    }

    # determines what layout to retrieve
    if player_display_location[_pos][1] == True:
        order = layout["_"][players_pos.count(_pos)]
    else:
        order =layout[_pos][players_pos.count(_pos)]

    string = ""

    # assembles string
    for char in order:
        if char != "p":
            string += char
        else:
            x = next(player_itr)
                
            # seeks the next player at that location
            while players_pos[x] != _pos: x = next(player_itr)

            string += player[x + 1]["char"]

    # updates display
    player_display_location[_pos][0] = string
 

type decorator = function
def coro_protection(coro) -> decorator:
    """decorator. suppresses CancelledError once coroutine canceled"""
    async def sub(*args, **kwards):
        try:
            await coro(*args, **kwards)
        except asyncio.CancelledError:
            return
        except exit_async:
            online_config.quit_async()

    sub.__name__ = coro.__name__
    return sub


class exit_async(BaseException):
    """raise to start canceling asynchronous functions"""
    pass


# used for reseting variables (see: refresh_board.input_mgmt > 's')
class parent_class:
    def disconnect_management(self, quitter):
        """handles an online player leaving mid-game"""
        if online_config.game_strt_event.is_set():
            bankruptcy(quitter, "disconnect")
            if online_config.socket_type != "host":
                return
            
            for item in online_config.joined_clients:
                if item[3] == quitter:
                    _return = item[1]
                    online_config.joined_clients.remove(item)

    def input_management(self, user_input):
        """determines what action to perform with user input"""
    
    def online_management(self, command):
        """executes relevant logic for an online command"""

    def __call__(self): pass 
    def __init_subclass__(self): self.__name = None
    def __eq__(self, value): return self.__name__ == value

    @property
    def __name__(self):
        # if name does not exist, it is found through globals
        if not self.__name:
            for item in globals().items():
                if id(item[1]) == id(self):
                    self.__name = item[0]
                    break
                
        return self.__name


class player_is_broke_class(parent_class):
    def __call__(self, _player: int, cause = None):
        """alerts the player that they are in debt/are bankrupt
        cause is passed on to bankruptcy if applicable. check requirements there"""

        global current_screen
        current_screen = self.__name__

        clear_screen()

        player_has_properties = False

        # checks if the player could afford to pay off their debts,
        # if not, the prompt to declare bankruptcy appears.
        # even if that happens, the player is still shown their properties,
        # to attempt to trade their way out of bankruptcy
        available_funds = 0
        for i in range(28):

            # if the property is not owned by the player
            if property_data[i]["owner"] != _player:
                continue

            # if the property is already mortgaged
            if property_data[i]["upgrade state"] < 1:
                continue

            available_funds += (property_data[i]["street value"] / 2)

            # if the property doesn't have any upgrades
            if property_data[i]["upgrade state"] <= 2:
                continue

            number_of_upgrades = property_data[i]["upgrade state"] - 2
            available_funds += number_of_upgrades * (property_data[i]["house cost"] / 2)

            # ensures that the property list is brought up
            # instead of going directly to bankruptcy
            player_has_properties = True

        if player_has_properties == True:

            # this makes sure that the text is centered by adding extra space if the debt is a different length than 4 digits
            extra_space = ""
            for i in range(5 - len(str(abs(player[_player]["$$$"])))): extra_space += " "

            print()
            print("    ╔════════════════════════════════════════════════════════════════╗")
            print("    ║                                                                ║")
            print("    ║                             NOTICE:                            ║")
            print("    ║                                                                ║")
            print(f"    ║{extra_space}       Player {player_turn}, You are ${abs(player[_player]['$$$'])} in debt! raise ${abs(player[_player]['$$$'])} by:       {extra_space}║")
            print("    ║                                                                ║")
            print("    ║       Mortgaging properties (for half of street vaule),        ║")
            print("    ║      Selling houses/hotels (for half build price), or by       ║")
            print("    ║          Trading with other players (without houses).          ║")
            print("    ║                                                                ║")
            if available_funds < abs(player[_player]["$$$"]):
                print("    ║           you have more debt than you can pay back,            ║")
                print("    ║       so you can declare bankruptcy, or attempt a trade.       ║")
                print("    ║                                                                ║")
            print("    ╚════════════════════════════════════════════════════════════════╝")

            display_property_list(_player, False, available_funds < abs(player[_player]["$$$"]))
 
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
            player[self.bankruptcy_details[0]]["status"] = "bankrupt"
            bankruptcy(*self.bankruptcy_details)


player_is_broke = player_is_broke_class()


class display_property_list_class(parent_class):
    def __init__(self):
        self.player = None
        self.allow_bankruptcy = False
        
    def __call__(self, _player, clear = True, allow_bankruptcy = False):
        global conversion_dictionary
        global current_screen
        current_screen = self.__name__

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
        conversion_dictionary = {}

        stations_displayed = False
        utilities_displayed = False

        # this checks what stations the player owns and displays them first
        for i in [2, 10, 17, 25]:
            if property_data[i]["owner"] == _player:
                sleep(150)
                _count += 1
                print(f"    ║   [{_count}]  │ {property_data[i]['name']}", end = "")
                
                conversion_dictionary[_count] = i

                for ii in range(22 - len(property_data[i]['name'])):
                    print(" ", end = "")

                print(f"│ ${property_data[i]['street value']} │", end = "")
            
                if property_data[i]["upgrade state"] == -1:
                    print(" Mortgaged              ║")
                else:
                    print("                        ║")

                stations_displayed = True

        # displays an extra blank line to separate the stations from the other cards
        if stations_displayed == True:
            print("    ║                                                                ║")   

        for i in [7, 20]:
            if property_data[i]["owner"] == _player:
                sleep(150)
                _count += 1
                print(f"    ║   [{_count}]  │ {property_data[i]['name']}", end = "")
                
                conversion_dictionary[_count] = i

                for ii in range(22 - len(property_data[i]["name"])):
                    print(" ", end = "")
                print(f"│ ${property_data[i]['street value']} │", end="")

                if property_data[i]["upgrade state"] == -1:
                    print(" Mortgaged              ║")
                else:
                    print("                        ║")

                utilities_displayed = True

        if utilities_displayed == True:
            print("    ║                                                                ║")

        for i in range(28):
            if property_data[i]["owner"] != _player or property_data[i]["type"] != "property":
                continue

            sleep(150)
            _count += 1
            conversion_dictionary[_count] = i
            if _count >= 10:
                print(f"    ║   [{_count}] │ {property_data[i]['name']}", end = "")
            else:
                print(f"    ║   [{_count}]  │ {property_data[i]['name']}", end = "")

            for ii in range(22 - len(property_data[i]["name"])): print(" ", end = "")

            print(f"│ ${property_data[i]['street value']} ", end = "")
            if property_data[i]["street value"] < 100: print(" ", end = "")

            if property_data[i]["upgrade state"] != -1:
                print(f"│ ${property_data[i]['house cost']}", end = "")
                
                if property_data[i]["house cost"] < 100:
                    print(" ", end = "")
                    
                print(" × ", end = "")

                if property_data[i]["upgrade state"] == 7:
                    print("🏠🏠🏠🏠 🏨     ║")

                else:

                    # prints the number of houses on the property
                    x = ""
                    for ii in range(property_data[i]["upgrade state"] - 2): x += "🏠"

                    print(f"{x}", end = "")
                    for ii in range(16 - (2 * len(x))): print(" ", end = "")
                    print("║")
            elif property_data[i]["upgrade state"] == -1: print("│ Mortgaged              ║")

        print("    ║                                                                ║")
        print("    ╚════════════════════════════════════════════════════════════════╝")
        print()

        can_leave = True
        if player[player_turn]["$$$"] < 0:
            can_leave = False

        prompt = [["Trade", "#"],[True, True], [4, 3]]

        # inserts the bankruptcy prompt if given through player_is_broke()
        if allow_bankruptcy != False:
            prompt[0].append("Go bankrupt")
            prompt[1].append(True)
            prompt[2].append(3)
        prompt[0].append("Back")
        prompt[1].append(can_leave)
        prompt[2].append(6)
        for i in create_button_prompts(prompt[0], prompt[1], prompt[2]):
            print(i)

        if dev_mode != False: print(conversion_dictionary)
        print("\n    ", end="")

    def input_management(self, user_input):
        if user_input in ["b", "B"]:

            # checks that the player doesn't have negative cash,
            # and that no other players have negative cash
            if player[player_turn]["$$$"] < 0:
                print("\n    === you must clear your debts before returning to the game ===\n\n    ", end = "")
            else:
                lock = False
                for i in range(1, players_playing + 1):
                    if player[i]["$$$"] < 0 and player[i]["status"] == "playing":
                        player_is_broke(i)
                        lock = True
                        break
                if lock == False: refresh_board()
                
        elif user_input in ["t", "T"]:
            if trade_screen.is_trade == True:
                trade_screen.display_trade_window()
            else:
                trade_screen(player_turn)

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
                if int(user_input) in conversion_dictionary:
                   display_property(conversion_dictionary[int(user_input)])
                else:
                    print("\n    === command not recognised ===\n\n    ", end = "")


display_property_list = display_property_list_class()


class display_property_class(parent_class):
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

            # ensures that a copy isn't made halfway through an auction
            if not self.player_bid_turn:
                self.player_bid_turn = player_turn.copy()

                # ensures that only playing players can play
                while player[self.player_bid_turn]["status"] in ("bankrupt", "disconnected"):
                    next(self.player_bid_turn)

                # checks how many players are participating
                self.players_bidding = 0
                for _player in player.items():
                    if _player[1]["status"] not in ("bankrupt", "disconnected"):
                        self.players_bidding += 1

        if len(_prop_num) > 1:
            print("    === auction queue ===\n")
            for prop in self.property_queue:

                # isn't this cool, and inline if statement WITHIN a string:
                print(f"    {property_data[prop]['name']} {(lambda: '(mortgaged)' if property_data[prop]['upgrade state'] == -1 else '')()}")
            print()

        if bid: self.action = "auction"

        # even if one number is given, python creates a one item tuple,
        # which cannot be used as an index, and so is fixed
        self.property = _prop_num[0]
        global current_screen

        current_screen = self.__name__

        # resets the iterators each time, as a precaution
        self.notice.index = -1
        self.player_bids.index = -1
        self.bid_struc.index = -1

        printed_bids = 0

        extra_space = ["", "", "", ""]

        self.colour_set = []
        for prop in property_data:
            if not ("colour set" in prop.keys() and "colour set" in property_data[self.property].keys()):
                continue

            if prop["colour set"] == property_data[self.property]["colour set"]:
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

        if property_data[self.property]["upgrade state"] == -1:

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
                if   line == 1 : output = f"{extra_space[0]}{extra_space[1]} {property_data[self.property]['name'].upper()}{extra_space[0]}  "
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

            m_val = int(property_data[self.property]["street value"] / 2)
            if len(str(m_val)) == 2           : extra_space[2] = " "
            if len(str(int(m_val * 1.1))) == 2: extra_space[3] = " "

            for i in range((21 - len(property_data[self.property]["name"])) // 2): extra_space[0] += " "
            if len(property_data[self.property]["name"]) % 2 == 0: extra_space[1] = " "

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
            for ii in range((21 - len(property_data[self.property]["name"])) // 2): extra_space[0] += " "
            
            # since the upper code can only add two spaces, if the difference
            # between the maximum length and actual length is odd (so the value is even)...
            # ...an extra space is added to the left of the name to center it properly
            if len(property_data[self.property]["name"]) % 2 == 0: extra_space[1] = " "

            print(f"    │                              │{display_bids()}")
            print(f"    │{extra_space[0]}{extra_space[1]}    {property_data[self.property]['name']}     {extra_space[0]}│{display_bids()}")
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
            arrow = lambda i: '>' if property_data[self.property]["upgrade state"] == i else ' '

            print(f"    ┌──────────────────────────────┐{bidding_notice()}")

            # this checks what colour set the property is in and adjusts the colour of the printed title deed
            if property_data[self.property]["colour set"] == 0:
                colour = "🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫" # brown

            # light blue (set 1) and dark blue (set 7) use the same colour
            elif property_data[self.property]["colour set"] in [1, 7]:
                colour = "🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦"
        
            elif property_data[self.property]["colour set"] == 2:
                colour = "🟪🟪🟪🟪🟪🟪🟪🟪🟪🟪🟪🟪🟪🟪" # purple (there's no pink square emoji)

            elif property_data[self.property]["colour set"] == 3:
                colour = "🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧" # orange

            elif property_data[self.property]["colour set"] == 4:
                colour = "🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥" # red

            elif property_data[self.property]["colour set"] == 5:
                colour = "🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨" # yellow

            else:
                colour = "🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩" # green

            for i in range(4): print(f"    │ {colour} │{bidding_notice()}")

            print(f"    │                              │{bidding_notice()}")

            # see the same code for the stations
            extra_space[0] = ""
            for ii in range((21 - len(property_data[self.property]["name"])) // 2): extra_space[0] += " "

            extra_space[1] = ""
            if len(property_data[self.property]["name"]) % 2 == 0: extra_space[1] = " "

            print(f"    │{extra_space[0]}{extra_space[1]}    {property_data[self.property]['name']}     {extra_space[0]}│{bidding_notice()}")
            print(f"    │                              │{bidding_notice()}")

            # these just add an extra 1-2 spaces if depending on the length, for rent, colour set rent and all the other stats
            extra_space[0] = ""
            for ii in range(2 - len(str(property_data[self.property]["rent"]))): extra_space[0] += " "

            print(f"    │ Rent                 {arrow(1)} ${property_data[self.property]['rent']}{extra_space[0]}   │")


            extra_space[0] = ""
            for ii in range(3 - len(str(property_data[self.property]["rent"] * 2))): extra_space[0] += " "

            extra_space[1] = ""
            for ii in range(3 - len(str(property_data[self.property]["h1 rent"]))): extra_space[1] += " "

            print(f"    │ Rent with colour set {arrow(2)} ${(property_data[self.property]['rent'] * 2)}{extra_space[0]}  │{display_bids()}")
            print(f"    │                              │{display_bids()}")
            print(f"    │ Rent with 🏠         {arrow(3)} ${property_data[self.property]['h1 rent']}{extra_space[1]}  │{display_bids()}")

            extra_space[0] = ""
            for ii in range(3 - len(str(property_data[self.property]["h2 rent"]))): extra_space[0] += " "

            extra_space[1] = ""
            for ii in range(4 - len(str(property_data[self.property]["h3 rent"]))): extra_space[1] += " "

            extra_space[2] = ""
            for ii in range(4 - len(str(property_data[self.property]["h4 rent"]))): extra_space[2] += " "

            print(f"    │ Rent with 🏠🏠       {arrow(4)} ${property_data[self.property]['h2 rent']}{extra_space[0]}  │{display_bids()}")
            print(f"    │ Rent with 🏠🏠🏠     {arrow(5)} ${property_data[self.property]['h3 rent']}{extra_space[1]} │{display_bids()}")
            print(f"    │ Rent with 🏠🏠🏠🏠   {arrow(6)} ${property_data[self.property]['h4 rent']}{extra_space[2]} │{display_bids()}")

            extra_space[0] = ""
            for ii in range(4 - len(str(property_data[self.property]["h5 rent"]))): extra_space[0] += " "

            print(f"    │                              │{display_bids()}")
            print(f"    │ Rent with 🏠🏠🏠🏠 🏨{arrow(7)} ${property_data[self.property]['h5 rent']}{extra_space[0]} │{display_bids()}")
            print(f"    │                              │{display_bids()}")

            extra_space[0] = ""
            for ii in range(4 - len(str(property_data[self.property]["house cost"]))): extra_space[0] += " "

            print(f"    │ ---------------------------- │{display_bids()}")        
            print(f"    │ House/hotel cost       ${property_data[self.property]['house cost']}{extra_space[0]} │{display_bids()}")
            print(f"    │                              │{display_bids()}")

            extra_space[0] = ""
            for ii in range(4 - len(str(property_data[self.property]["street value"]))): extra_space[0] += " "

            print(f"    │ Street value           ${property_data[self.property]['street value']}{extra_space[0]} │")

            extra_space[0] = ""
            for ii in range(3 - len(str(int(property_data[self.property]["street value"] / 2)))): extra_space[0] += " "   
        
            if property_data[self.property]["upgrade state"] != -1:
                print(f"    │ mortgage value         ${int(property_data[self.property]['street value'] / 2)}{extra_space[0]}  │")
            else:
                print(f"    │ unmortgage value       ${int((property_data[self.property]['street value'] / 2) * 1.1)}{extra_space[0]}  │")

            print("    └──────────────────────────────┘")

        if self.action_2 == "finished":
            print(f"\n    === player {self.player_bids[0]['player']} has won the bid, press [Enter] to continue ===\n\n    ", end = "")

        elif self.action == "auction" and self.player_bids.list[self.player_bid_turn] != 0:
            if self.action_2 == "final chance":
                print(f"\n    === player {self.player_bid_turn}, now's your final chance to place a bid, or [S]kip ===\n\n    ", end = "")
            else:
                print(f"\n    === player {self.player_bid_turn}, place a bid or [S]kip ===\n\n    ", end = "")

        elif self.action == "auction":
            if self.action_2 == "final chance":
                print(f"\n    === player {self.player_bid_turn}, now's your final chance to raise your bid, or [S]kip ===\n\n    ", end = "")
            else:
                print(f"\n    === player {self.player_bid_turn}, either raise your bid or [S]kip ===\n\n    ", end = "")

        else:
            print()
            print(f"    === your money: {player[player_turn]['$$$']} ===\n")
            actions = [[], [], [4]]

            # if the property has no upgrades, can be mortgaged
            if property_data[self.property]["upgrade state"] in [0, 1, 2]:
                actions[0].append("Mortgage")
                actions[1].append(True)

            # if the property has upgrades, cannot be mortgaged
            elif property_data[self.property]["upgrade state"] > 2:
                actions[0].append("Mortgage")
                actions[1].append(False)

            # if the property is mortgaged, checks if the player can afford to unmortgage
            elif property_data[self.property]["upgrade state"] == -1:
                actions[0].append("Unmortgage")
                if player[property_data[self.property]["owner"]]["$$$"] \
                        > round((property_data[self.property]["street value"] / 2) * 1.1):

                    actions[1].append(True)
                else:
                    actions[1].append(False)
            
            if property_data[self.property]["type"] == "property":
                actions[0].append("Add houses")
                actions[0].append("Sell houses")
                actions[2].append(3)
                actions[2].append(3)
                if 2 <= property_data[self.property]["upgrade state"] < 7 and \
                        player[property_data[self.property]["owner"]]["$$$"] >= property_data[self.property]["house cost"]:
                    actions[1].append(True)
                else:
                    actions[1].append(False)
                
                if property_data[self.property]["upgrade state"] > 2: actions[1].append(True)
                else                                            : actions[1].append(False)

            actions[2].append(3)

            # if the player is trading, and wants to remove a property
            if trade_screen.is_trade == True and \
            self.property in (trade_screen.player_1["props"] or trade_screen.player_2["props"]):
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
        global house_total
        global hotel_total

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

            refresh_board()

        if self.action_2 == "finished":
            exit_bid(self)

            refresh_board.action = None
            broke_alert = False
            for i in range(1, players_playing + 1):
                if player[i]["$$$"] < 0 and player[i]["status"] == "playing":
                    player_is_broke(i)
                    broke_alert = True
                    break

            if broke_alert == False: refresh_board()

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
                while player[self.player_bid_turn]["status"] == "bankrupt":
                    next(self.player_bid_turn)

                # provides a chance for players change their minds
                if self.skipped_bids == self.players_bidding:
                    self.action_2 = "final chance"

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

                    player[self.player_bids[0]["player"]]["$$$"] -= self.player_bids[0]["$$$"]
                    property_data[self.property]["owner"] = self.player_bids[0]["player"]
                                   
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
                while player[self.player_bid_turn]["status"] == "bankrupt":
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
                display_property_list(display_property_list.player)
  
            elif user_input in ["t", "T"]:
                if property_data[self.property]["upgrade state"] > 0:
                    print("\n    === you cannot trade upgraded properties ===\n\n    ", end="")
                    return

                if trade_screen.is_trade:
                    trade_screen.add_prop_offer(display_property.property)
                    self(self.property)
                    print("=== added to offer===\n\n    ", end="")
                else:
                    trade_screen(player_turn, self.property)

            elif user_input in ["m", "M"]:
                if property_data[self.property]["upgrade state"] in [1, 2]:
                    property_data[self.property]["upgrade state"] = -1
                    player[player_turn]["$$$"] += int(property_data[self.property]["street value"] / 2)
                    display_property(self.property)

                elif property_data[self.property]["upgrade state"] == -1:
                    print("\n    === property already mortgaged ===\n\n    ", end = "")

                elif property_data[self.property]["upgrade state"] > 2:
                    print("\n    === you cannot mortgage an upgraded property. sell all houses first ===\n\n    ", end = "")

            elif user_input in ["u", "U"]:

                # unmortgaged properties trigger the exit conditon
                if property_data[self.property]["upgrade state"] != -1:
                    print("\n    === property not mortgaged ===\n\n    ", end = "")
                    return

                cost = (property_data[self.property]["street value"] / 2) * 1.1
                    
                # unmortgages the property if the player can afford it
                if player[player_turn]["$$$"] < cost:
                    print("\n    === you cannot afford to unmortgage this property ===\n\n    ", end="")
                    return

                player[player_turn]["$$$"] -= cost
                player[player_turn]["$$$"] = int(player[player_turn]["$$$"])
                property_data[self.property]["upgrade state"] = 1
                self(self.property)

            elif user_input in ["a", "A"] and property_data[self.property]["type"] == "property":

                # if property is not eligible for upgrading
                if not (2 <= property_data[self.property]["upgrade state"] < 8):
                    print("\n    === you cannot upgrade this property ===\n\n    ", end = "")
                    return

                # if player cannot afford to upgrade
                if player[property_data[self.property]["owner"]]["$$$"] < property_data[self.property]["house cost"]:
                    print("\n    === you cannot afford to buy an upgrade ===\n\n    ", end = "")
                    return

                # if other properties in the colour set aren't upgraded at the same level
                for prop in self.colour_set:
                    if prop["upgrade state"] < property_data[self.property]["upgrade state"]:
                        print("\n    === other properties in this colour set have not been upgraded equally ===\n\n    ", end="")
                        return
                
                # determines whether a house or hotel is needed and available
                if property_data[self.property]["upgrade state"] < 7:
                    if house_total < 0:
                        print("\n    === there are no more houses left. all 32 have been purchased ===\n\n    ", end="")
                        return
                    house_total -= 1
                else:
                    if hotel_total < 0:
                        print("\n    === there are no more hotels left. all 16 have been purchased ===\n\n    ", end="")
                        return
                    hotel_total -= 1

                # if exit conditions are passed, then the player can upgrade
                player[property_data[self.property]["owner"]]["$$$"] -= property_data[self.property]["house cost"]
                property_data[self.property]["upgrade state"] += 1
                self(self.property)

            elif user_input in ["s", "S"] and property_data[self.property]["type"] == "property":

                # if the property cannot be downgraded
                if property_data[self.property]["upgrade state"] <= 2:
                    print("\n    === you cannot downgrade this property ===\n\n    ", end = "")
                    return

                # ensures equal upgrades through the colour set
                for prop in self.colour_set:
                    if prop["upgrade state"] > property_data[self.property]["upgrade state"]:
                        print("\n    === other properties in this colour set have not been downgraded equally ===\n\n    ", end="")
                        return

                # adds the house/hotel back into the pool
                if property_data[self.property]["upgrade state"] == 8:
                    hotel_total += 1
                else:
                    house_total += 1

                player[property_data[self.property]["owner"]]["$$$"] += property_data[self.property]["house cost"] / 2
                property_data[self.property]["upgrade state"] -= 1

                self(self.property)

            elif user_input in ["r", "R"] and trade_screen.is_trade:
                
                if not (self.property in trade_screen.player_1["props"] or self.property in trade_screen.player_2["props"]):
                    print("\n    === command not recognised ===\n\n    ", end="")
                    return

                # removes the property from the appropriate player's trade
                if self.property in trade_screen.player_1["props"]:
                    trade_screen.player_1["props"].remove(self.property)

                elif self.property in trade_screen.player_2["props"]:
                    trade_screen.player_2["props"].remove(self.property)
               
                # alerts the user of the change
                self(self.property)
                print("=== removed from offer ===\n\n    ", end="")

            else:
                print("\n    === command not recognised ===\n\n    ", end="")


display_property = display_property_class()


class chance_cards_class(parent_class):
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

        global player

        drawn_card = self.values[self.index]

        if drawn_card == 0:
            player[player_turn]["last pos"] = player[player_turn]["pos"]
            player[player_turn]["pos"] = 0
            player[player_turn]["$$$"] += 200
            update_player_position(player[player_turn]["pos"])
            update_player_position(player[player_turn]["last pos"], "remove")

        elif drawn_card == 1:
            player[player_turn]["last pos"] = player[player_turn]["pos"]
            player[player_turn]["pos"] = 24

            if player[player_turn]["last pos"] > 24:
                player[player_turn]["$$$"] += 200
            player_action(player_turn)
            update_player_position(player[player_turn]["pos"])
            update_player_position(player[player_turn]["last pos"], "remove")

        elif drawn_card == 2:
            player[player_turn]["last pos"] = player[player_turn]["pos"]
            player[player_turn]["pos"] = 11

            if player[player_turn]["last pos"] > 11:
                player[player_turn]["$$$"] += 200
            player_action(player_turn)
            update_player_position(player[player_turn]["pos"])
            update_player_position(player[player_turn]["last pos"], "remove")

        elif drawn_card == 3:

            # this moves the player to waterworks if between electricity company and waterworks, otherwise moves to electricity company
            player[player_turn]["last pos"] = player[player_turn]["pos"]
            if player[player_turn]["pos"] >= 12 and player[player_turn]["pos"] < 28:
                player[player_turn]["pos"] = 28

            elif player[player_turn]["pos"] >= 28:
                player[player_turn]["pos"] = 12
                player[player_turn]["$$$"] += 200

            else: player[player_turn]["pos"] = 12
            player_action.rent_mgmt(player_turn, 10)
            update_player_position(player[player_turn]["pos"])
            update_player_position(player[player_turn]["last pos"], "remove")
           
        elif drawn_card == 4:
            player[player_turn]["last pos"] = player[player_turn]["pos"]

            if   player[player_turn]["pos"] >= 35: player[player_turn]["pos"] = 5
            elif player[player_turn]["pos"] >= 25: player[player_turn]["pos"] = 35
            elif player[player_turn]["pos"] >= 15: player[player_turn]["pos"] = 25
            elif player[player_turn]["pos"] >= 5:  player[player_turn]["pos"] = 15

            # if the player is moved across GO (to Kings Cross), they gain $200
            if player[player_turn]["pos"] == 5:
                player[player_turn]["$$$"] += 200
                refresh_board.passed_go = True

            player_action.rent_mgmt(player_turn, 2)
            update_player_position(player[player_turn]["pos"])
            update_player_position(player[player_turn]["last pos"], "remove")

        elif drawn_card == 5:
            player[player_turn]["$$$"] += 50

        elif drawn_card == 6:
            player[player_turn]["jail passes"] += 1

        elif drawn_card == 7:
            player[player_turn]["last pos"] = player[player_turn]["pos"]
            player[player_turn]["pos"] -= 3
            player_action(player_turn)
            update_player_position(player[player_turn]["pos"])
            update_player_position(player[player_turn]["last pos"], "remove")

        elif drawn_card == 8:
            player[player_turn]["last pos"] = player[player_turn]["pos"]
            player[player_turn]["pos"] = 40
            player[player_turn]["status"] = "jail"
            update_player_position(player[player_turn]["pos"])
            update_player_position(player[player_turn]["last pos"], "remove")
            
        elif drawn_card == 9:
            player[player_turn]["$$$"] -= ((player[player_turn]["house total"] * 25) + (player[player_turn]["hotel total"] * 100))
            if player[player_turn]["$$$"] < 0:
                player_is_broke(player_turn)

        elif drawn_card == 10:
            player[player_turn]["last pos"] = player[player_turn]["pos"]
            player[player_turn]["pos"] = 5
            player_action(player_turn)
            update_player_position(player[player_turn]["pos"])
            update_player_position(player[player_turn]["last pos"], "remove")

        elif drawn_card == 11:
            player[player_turn]["last pos"] = player[player_turn]["pos"]
            player[player_turn]["pos"] = 39
            player_action(player_turn)
            update_player_position(player[player_turn]["pos"])
            update_player_position(player[player_turn]["last pos"], "remove")

        elif drawn_card == 12:
            for i in range(players_playing):
                if i + 1 != player_turn:
                    player[i + 1]["$$$"] += 50

            player[player_turn]["$$$"] -= 50 * (players_playing - 1)

            if player[player_turn]["$$$"] < 0:
                player_is_broke(player_turn)

        elif drawn_card == 13:
            player[player_turn]["$$$"] += 150

        elif drawn_card == 14:
            player[player_turn]["$$$"] -= 15
            if player[player_turn]["$$$"] < 0:
                player_is_broke(player_turn)

        refresh_board()


chance = chance_cards_class()


class community_chest_cards_class(parent_class):
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

        global player

        drawn_card = int(self.values[self.index])

        if drawn_card == 0:
            player[player_turn]["last pos"] = player[player_turn]["pos"]
            player[player_turn]["pos"] = 0
            player[player_turn]["$$$"] += 200
            update_player_position(player[player_turn]["pos"])
            update_player_position(player[player_turn]["last pos"], "remove")
           
        elif drawn_card == 1:
            player[player_turn]["$$$"] += 200

        elif drawn_card == 2:
            player[player_turn]["$$$"] -= 50
            if player[player_turn]["$$$"] < 0:
                player_is_broke(player_turn)

        elif drawn_card == 3:
            player[player_turn]["$$$"] += 50

        elif drawn_card == 4:
            player[player_turn]["jail passes"] += 1

        elif drawn_card == 5:
            player[player_turn]["last pos"] = player[player_turn]["pos"]
            player[player_turn]["pos"] = 40    
            player[player_turn]["status"] = "jail"
            update_player_position(player[player_turn]["pos"])
            update_player_position(player[player_turn]["last pos"], "remove")

        elif drawn_card == 6:
            player[player_turn]["$$$"] += 100

        elif drawn_card == 7:
            player[player_turn]["$$$"] += 20

        elif drawn_card == 8:
            player[player_turn]["$$$"] += 10 * (players_playing - 1)

            # loops through the players, all other players get deducted $10, checks if they're broke
            for i in range(1, players_playing + 1):
                if i + 1 != player_turn:
                    player[i]["$$$"] -= 10
                    if player[i]["$$$"] < 0 and player[i] == "playing":
                        player_is_broke(i)

        elif drawn_card == 9:
            player[player_turn]["$$$"] += 100
    
        elif drawn_card == 10:
            player[player_turn]["$$$"] -= 100

            if player[player_turn]["$$$"] < 0:
                player_is_broke(player_turn)
    
        elif drawn_card == 11:
            player[player_turn]["$$$"] += 10

        elif drawn_card == 12:
            player[player_turn]["$$$"] -= ((player[player_turn]["house total"] * 40) + (player[player_turn]["hotel total"] * 115))
            if player[player_turn]["$$$"] < 0:
                player_is_broke(player_turn)

        elif drawn_card == 13:
            player[player_turn]["$$$"] -= 50
            if player[player_turn]["$$$"] < 0:
                player_is_broke(player_turn)

        elif drawn_card == 14:
            player[player_turn]["$$$"] += 25

        elif drawn_card == 15:
            player[player_turn]["$$$"] += 100

        refresh_board()


community_chest = community_chest_cards_class()


class homescreen_class(parent_class):
    def __init__(self):
        self.action = None

    def __call__(self):
        """displays the home screen"""
        clear_screen()

        # the 'current_screen' variable is used for user input, to make sure that the correct action happens
        global current_screen
        current_screen = self.__name__

        # ensures asynchronous online operations will work
        online_config.stop_event.clear()

        print("")
        print(r"       ___  ___        _____     _____ ____     _____      _____      _____     ____     ___  ___"    )
        print(r"      ╱   ╲╱   ╲      ╱     ╲    │    ╲│  │    ╱     ╲    │  _  \    ╱     ╲    │  │     ╲  \/  ╱ │ coded by:")
        print(r"     ╱  /╲  ╱\  ╲    │  (_)  │   │  ╲  ╲  │   │  (_)  │   │  ___/   │  (_)  │   │  │__    ╲_  _╱  │ James E.")
        print(r"    ╱__/  ╲╱  \__╲    ╲_____╱    |__│╲____|    ╲_____╱    |__|       ╲_____╱    |_____|    |__|   │ 2024, 2025")
        print("")
        print("")

        # checks if a save file exists
        saved_game = False
        try: x = open("save_file.james", encoding = "utf-8")
        except: pass
        else: x.close(); saved_game = True
        
        for i in create_button_prompts(["Start game", "Continue", "Online"], [True, saved_game, True]):
            print(i)
        print("")
        print("    ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────")
        print("\n    ", end = "")

    def input_management(self, user_input):
        global dev_mode
        global current_screen

        if user_input in ["devmode", "dev mode"]:
            dev_mode = True
            print("\n    === dev mode enabled ===\n\n    ", end = "")

        elif user_input in ["s", "S"]:
            new_game_select()

        elif user_input in ["c", "C"]:
              read_save("save_file.james", "utf-8") 
              display_game_notice()

        elif user_input in ["o", "O"]:
            online_config()

        elif "nick" in user_input.lower():

            # in dedication to Nick Tho, who always uses his phone with night-shift enabled at the maximum intensity
            # changes the background to yellow
            print("\x1b[43m")
            self()

            print("=== Nick Tho always uses night-shift on maximum intensity, I'm not trying to be racist ===\n")
            for i in create_button_prompts(["I'm offended", "Makes sense"]): print(i)
            print("\n    ", end = "")
            self.action = "nicktho"

        elif user_input in ["i", "I"] and self.action == "nicktho":
            self()
            print("\n    === get over it. ===\n\n    ", end = "")
            
        elif user_input in ["m", "M"] and self.action == "nicktho":
            self()
            print("\n    === wow thank you for understanding and not overreacting. ===\n\n    ", end = "")

        else:
            print("\n    === command not recognised ===\n\n    ", end = "")


homescreen = homescreen_class()


class online_config_class(parent_class):
    """contains the menus and sockets for starting an online game

    as a client, .joined_clients is [[name, name], [icon, icon], [ID, ID]]
    while as a host, [[name, socket, icon, ID], [name, socket, icon, ID]]
    
    .game_strt_event is set once the host starts the game.
    .player_num corresponds to a player key in `player`
    .running_tasks contains all asynchronous tasks created in self.shell()
    .ping count is an int as client, or list[int] as an host.
    """    
    def __init__(self):
        self.joined_clients = []
        self.action = None
        self.action_2 = None
        self.display_name = ""
        self.display_icon = ""
        self.socket_type = None
        self.stop_event = asyncio.Event()
        self.game_strt_event = asyncio.Event()
        self.running_tasks = []
        
        self.player_num = None # ID for specific player

        self.ping_count = 0
        self.max_pings_threshold = 3

        # creates a new socket for connection
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __call__(self):
        global current_screen
        current_screen = self.__name__

        self.action = "name 1"
        clear_screen()
        print()
        print("    === enter display name (this is different to icon shown on board) ===\n\n    ", end="")

    def mode_select(self):
        clear_screen()

        self.action = "mode select"

        print()
        for line in create_button_prompts(["Host", "Join", "Back"], spacing=[4, 3, 6]):
            print(line)
        print("\n    ", end = "")

    def connection_lost(self):
        """alerts user that connection to host was lost
        handles with closing the socket and exiting async"""

        global current_screen
        current_screen = self.__name__
        self.action = "connection lost accept"

        clear_screen()
        print()
        print("    ╔════════════════════════════════════════════════════════════════╗")
        print("    ║                                                                ║")
        print("    ║                             NOTICE:                            ║")
        print("    ║                                                                ║")
        print("    ║             your connection with the host was lost             ║")
        print("    ║                                                                ║")
        print("    ║                             [ENTER]                            ║")
        print("    ║                                                                ║")
        print("    ╚════════════════════════════════════════════════════════════════╝")
        print("\n    ", end="")
        self.quit_async()

    def kicked_notice(self):
        """alerts the user that they were removed by the host
        handles with closing the socket and exiting async"""

        global current_screen
        current_screen = self.__name__
        self.action = "connection lost accept"

        clear_screen()
        print()
        print("    ╔════════════════════════════════════════════════════════════════╗")
        print("    ║                                                                ║")
        print("    ║                             NOTICE:                            ║")
        print("    ║                                                                ║")
        print("    ║               the host kicked you from the game.               ║")
        print("    ║                 this is definitely your fault.                 ║")
        print("    ║                                                                ║")
        print("    ║                             [ENTER]                            ║")
        print("    ║                                                                ║")
        print("    ╚════════════════════════════════════════════════════════════════╝")
        print("\n    ", end="")
        self.quit_async()

    def wrong_version_notice(self):
        """alerts the user that they are not playing on the same version as host"""
        global current_screen
        current_screen = self.__name__
        self.action = "connection lost accept"

        # ahhhhrgh I had to make this a bit wider to fit the link,
        # hopefully no-one will notice
        clear_screen()
        print()
        print("    ╔═════════════════════════════════════════════════════════════════════╗")
        print("    ║                                                                     ║")
        print("    ║                               NOTICE:                               ║")
        print("    ║                                                                     ║")
        print("    ║           Your game version is not the same as the host.            ║")
        print("    ║                     get the latest update from:                     ║")
        print("    ║                                                                     ║")
        print("    ║ https://github.com/James-Edelman/text-based-monopoly-python-version ║")
        print("    ║                                                                     ║")
        print("    ║                               [ENTER]                               ║")
        print("    ║                                                                     ║")
        print("    ╚═════════════════════════════════════════════════════════════════════╝")
        print("\n    ", end="")

    def host_wait_screen(self, connection_details: str | None = None):
        """the host's screen for displaying joined clients."""
        global current_screen
        current_screen = self.__name__
        self.action = "host wait screen"

        if connection_details == None:
            connection_details = f"{self.U_IP_V4}-{self.port}"

        clear_screen()

        extra_space = ["", ""]
        for ii in range((64 - len(connection_details)) // 2): extra_space[0] += " "
        if len(connection_details) % 2 == 1: extra_space[1] = " "

        print()
        print("    ╔════════════════════════════════════════════════════════════════╗")
        print("    ║                                                                ║")
        print("    ║                       CONNECTION DETAILS:                      ║")
        print("    ║                                                                ║")
        print(f"    ║{extra_space[0]}{extra_space[1]}{connection_details}{extra_space[0]}║")
        print("    ║                                                                ║")
        print("    ║            Share this code with up to 3 other people           ║")
        print("    ║                   for them to join this game                   ║")
        print("    ║                                                                ║")
        print("    ╚════════════════════════════════════════════════════════════════╝")
        print("\n    \x1b[s\x1b[0J")

        # buttons are adjusted once a user joins
        for line in create_button_prompts(
                ["Start game", "kick user", "back"],
                [len(self.joined_clients) > 0, len(self.joined_clients) > 0, True],
                [4, 3, 6]
            ):
            print(line)

        print("\n\n    === joined users: ===\n")

        for name in self.joined_clients:
            print(f"    === {name[0]} joined ===")

        # restores cursor position
        print("\x1b[u\x1b[0K", end="", flush=True)

    def client_wait_screen(self):
        global current_screen
        current_screen = self.__name__
        self.action = "client wait screen"

        clear_screen()
        print()
        print("    ╔════════════════════════════════════════════════════════════════╗")
        print("    ║                                                                ║")
        print("    ║                            PLAYERS:                            ║")
        print("    ║                                                                ║")
        
        lock = False
        for _id in self.joined_clients[2]:
            # gets the index in the ID sublist and access value in name sublist
            name = self.joined_clients[0][self.joined_clients[2].index(_id)]

            # the first name is always the host
            if not lock:
                name += " (host)"
                lock = True

            if self.player_num == int(_id):
                name += " (you)"

            extra_space = ""
            extra_extra_space = ""
            for x in range((40 - len(name)) // 2):
                extra_space += " "

            if len(name) % 2 == 1: extra_extra_space = " "
            print(f"    ║            {extra_space}{name}{extra_space}{extra_extra_space}            ║")
        
        print("    ║                                                                ║")
        print("    ╚════════════════════════════════════════════════════════════════╝")
        print()
        for line in create_button_prompts(["back"]):
            print(line)
        print()
        print("    ", end="")
    
    @coro_protection
    async def get_users(self):
        """allows the host to receive users. Handles connection protocol"""
        if self.socket_type != "host": return
        loop = asyncio.get_running_loop()

        @coro_protection
        async def check():
            # users aren't accepted once game starts
            await self.game_strt_event.wait()
            accept_tsk.cancel()

        async def accept(target: asyncio.Task):
            # gets a client
            try:
                client, _ = await loop.run_in_executor(None, self.socket.accept) # port is discarded
            
            # if the other coroutine closes the socket    
            except OSError:
                return None

            else: # ensures the check doesn't block either.
                target.cancel()
                return client

        while not self.stop_event.is_set() or not self.game_strt_event.is_set():
            check_tsk = asyncio.Task(check())
            accept_tsk = asyncio.Task(accept(check_tsk))

            try:
                client, _ = await asyncio.gather(accept_tsk, check_tsk)
            except asyncio.CancelledError:
                return

            if client == None:
                return

            # clients sends version first thing
            client_version = float(client.recv(1024).decode())

            # host sends confirmation that both on same version
            if client_version == game_version:
                client.sendall("True".encode())
            else:
                client.sendall("False".encode())
                continue

            # client sends name immediately after connection
            _, name, icon, num = client.recv(1024).decode().split(":")

            # determines client id number
            found_num = False
            while not found_num:

                # checks if ID already taken
                for item in self.joined_clients:
                    if item[3] == num:
                        client.sendall("False".encode())
                        num = int(client.recv(1024).decode())
                        continue

                # if no matches, (or no other clients)
                found_num = True
                client.sendall("True".encode())
           
            client.sendall(f"{chance.values}:{community_chest.values}".encode())

            client.setblocking(False)
            self.joined_clients.append([name, client, icon, num])

            # alerts all clients to update in players
            client_list = [[self.display_name], [self.display_icon], [1]]
            for item in self.joined_clients:
                client_list[0].append(item[0])
                client_list[1].append(item[2])
                client_list[2].append(item[3])

            for item in self.joined_clients:
                item[1].sendall(f"users update:{client_list}".encode())

            # ensures four players maximum isn't exceeded
            if len(self.joined_clients) == 3: return

            self.host_wait_screen()

    def input_management(self, user_input):
        global player
        global player_turn
        global players_playing
        
        if user_input == "DISPLAY CLIENTS":
            print(self.joined_clients)
        elif user_input.startswith("DISPLAY VAR"):
            _, var = user_input.split(":")
            try:
                print(eval(var))
            except NameError:
                pass

        elif self.action == "name 1":
            user_input = user_input.strip()
            if not user_input:
                print("    === please enter a name ===\n\n    ", end="")
                return

            # gets display name then player icon (see below)
            self.display_name = user_input
            print("\n    === enter player icon ===\n\n    ", end="")
            self.action = "name 2"

        elif self.action == "name 2":

            # enforces 2 characters width for name
            name_width = 0
            for char in user_input:
                if width(char) in ("F", "W"): name_width += 2
                else: name_width += 1
            
            if user_input in ["  ", r"\\"]:
                print("\n    === nice try. ===\n\n    ", end = "")
            elif name_width > 2:
                print("\n    === icon too large, try a different icon (eg: '😊' or 'JE') ===\n\n    ", end="")
            elif name_width < 2:
                print("\n    === icon too small, try a different icon (eg: '😊' or 'JE') ===\n\n    ", end="")
            else:
                self.display_icon = user_input
                self.mode_select()
                
        elif self.action == "host wait screen":
            if self.action_2 == "user to boot":
                if user_input in ["c", "C"]:
                    self.action_2 = None
                    print("\x1b[u\x1b[0K", end="", flush=True)
                    return

                # boots the client when name is matched
                for item in self.joined_clients:
                    if user_input == item[0]:
                        item[1].sendall(b"booted")
                        item[1].close()
                        self.joined_clients.remove(item)
                        break
                else:
                    print("\x1b[u\x1b[0K=== enter player name ([C]ancel): ", end="", flush=True)
                    return
                 
                print("\x1b[u\x1b[0K", end="", flush=True)
                self.host_wait_screen()

            elif self.action_2 == "accept notice":
                pass

            elif user_input in ["s", "S"]:
                if len(self.joined_clients) == 0:
                    print("\x1b[u\x1b[0K=== You need at least 2 players to start. [Enter] ===", end="", flush=True)
                    return

                send_data("hoststart")
                player = {}

                icons = [self.display_icon]
                for item in self.joined_clients:
                    icons.append(item[2])

                # creates the players using the characters provided
                for i in range(len(online_config.joined_clients) + 1):
                    player[i + 1] = {
                    "char": icons[i],
                    "$$$": 1500,
                    "pos": 0,
                    "last pos": 0,
                    "jail passes": 0,
                    "jail time": 0,
                    "house total": 0,
                    "hotel total": 0,
                    "total properties": 0,
                    "status": "playing",
                    "version": game_version
                }

                players_playing = len(self.joined_clients) + 1 # accounts for host
                player_turn = better_iter(range(1, players_playing + 1), True)
                update_player_position(0)

                # ensures users aren't accepted and logic functions properly
                self.game_strt_event.set()
                display_game_notice()

            elif user_input in ["k", "K"]:
                 print("\x1b[u\x1b[0K=== enter player name ([C]ancel): ", end="", flush=True)
                 self.action_2 = "user to boot"

            elif user_input in ["b", "B"]:

                # alerts all clients that the host has canceled
                for items in self.joined_clients:
                    try: items[1].send("%hostquit%")
                    except: pass

                # quits the asyncio.gather()
                self.stop_event.set()

                # ensures other coroutine won't be permanently waiting for another connection
                self.socket.close()
                
                self.quit_async()
            
            else:
                print("\x1b[u\x1b[0K", end="", flush=True)

        elif self.action == "client wait screen":
            if self.action_2 == "enter details":
                try:
                    SERVER_IP_V4, server_port = user_input.strip().split("-")
                    SERVER_PORT = int(server_port)
                    self.socket.connect((SERVER_IP_V4, SERVER_PORT))

                # bit lazy using a bare except,
                # but it should suffice as a basic catch-all
                except:

                    # exits the coroutines
                    if user_input == "b":
                        self.socket_type = None
                        self.mode_select()
                        self.stop_event.set()
                        return

                    print("\n    === Error using join code. please try again ===\n\n    ", end="")
                    return

                # see below loop
                num = 2 # #1 reserved for host

                # protocol is for joined clients to ensure same version
                self.socket.sendall(str(game_version).encode())

                same_ver = self.socket.recv(1024).decode()

                if same_ver != "True":
                    self.wrong_version_notice()
                    return

                # then names are exchanged
                self.socket.sendall(f"clientjoin:{self.display_name}:{self.display_icon}:{num}".encode())

                # finds unique ID number with host help
                found_num = False
                
                while found_num != True:
                    found_num = self.socket.recv(1024).decode()

                    # only strings can be sent
                    if found_num == "True":
                        found_num = True
                    else:
                        num += 1 # process repeats until valid number
                        self.socket.sendall(str(num).encode())

                self.player_num = num
                
                # ensures chance cards are consistent across games
                chance_order, cc_order = self.socket.recv(1024).decode().split(":")
                chance.values = eval(chance_order)
                community_chest.values = eval(cc_order)

                # receives list of playing clients
                _, client_list = self.socket.recv(1024).decode().split(":")
                online_config.joined_clients = eval(client_list)

                # ensures that client screen commands are accessible
                self.action_2 = None

                self.client_wait_screen()
                print(f"\n    === connected to {self.joined_clients[0][0]}'s game. waiting for host start ===\n\n    ", end="")

                try:
                    asyncio.run(self.shell())
                except:
                    pass
                print("    ", end = "")
                quit()

            elif user_input in ["b", "B"]:
                send_data("clientquit")

                # ensures other coroutine won't be permanently waiting for another connection
                self.socket.close()
                self.quit_async()

            else:
                print("\n    === command not recognised ===\n\n    ", end="")

        elif self.action == "mode select":
            if user_input in ["h", "H"]:

                self.socket_type = "host"
                self.player_num = 1

                # gets user IP
                self.U_NAME = socket.gethostname()
                self.U_IP_V4 = socket.gethostbyname(self.U_NAME)
                self.port = 42069

                # this is extremely unlikely, but I want to ensure no errors
                # if port is taken, goes to the next one and tries again
                unbound = True
                while unbound:
                    try:
                        self.socket.bind((self.U_IP_V4, self.port))
                    except OSError:
                        self.port += 1
                    else:
                        unbound = False

                self.socket.listen()
                self.ping_count = []
                self.host_wait_screen(f"{self.U_IP_V4}-{self.port}")
                
                try:
                    asyncio.run(self.shell())
                except:
                    pass
                print("    ", end = "")
                quit()
            
            elif user_input in ["j", "J"]:
                self.socket_type = "client"

                # clients use the joined_clients list differently
                # contains names and icons, but not the sockets
                self.joined_clients = [[],[], []]

                self.ping_count = 0
                self.client_wait_screen()
                self.action_2 = "enter details"
                print("enter connection details: ", end = "")

            elif user_input in ["b", "B"]:
                self.game_strt_event.clear()
                homescreen()

            else:
                print("\n    === command not recognised ===\n\n    ", end="")
        else:
            print("\n    === command not recognised ===\n\n    ", end="")

    def disconnect_management(self, quitter):
        if self.socket_type == "client":

            # removes the player from user's list of players
            for client in online_config.joined_clients:
                if quitter == client[2]:
                    online_config.joined_clients.remove(client)
                    break
            self.client_wait_screen()

        elif self.socket_type == "host":
            # removes the player from user's list of players
            for client in online_config.joined_clients:
                if quitter == client[3]:
                    online_config.joined_clients.remove(client)
                    break
            self.host_wait_screen()

    def quit_async(self):
        """quits all asynchronous tasks"""
        self.stop_event.set()
        self.gather.cancel()
        if self.socket_type == "client":
            self.socket.close()
        else:
            for item in self.joined_clients:
                item[1].close()

        for task in online_config.running_tasks:
            task.cancel()
        #quit()
        #asyncio.get_running_loop().close()

    @coro_protection
    async def ping(self):
        """pings the other socket every four seconds"""
        while not self.stop_event.is_set():
            send_data("ping")
            await asyncio.sleep(3)

            # client only has host connection
            if self.socket_type == "client":
                self.ping_count += 1
                if self.ping_count > self.max_pings_threshold:
                    globals()[current_screen].disconnect_management(1) # host is always ID 1
            else:
                # increments count for all clients
                self.ping_count = [i + 1 for i in self.ping_count]
                for count in self.ping_count:
                    if count > self.max_pings_threshold:
                        globals()[current_screen].disconnect_management(self.ping_count.index(count))
    
    async def shell(self):
        """main entry point for asynchronous functions"""
        if dev_mode:
            asyncio.get_running_loop().set_debug(True)

        self.running_tasks = [asyncio.Task(get_input()), asyncio.Task(get_data()), asyncio.Task(self.get_users())]
        self.gather = asyncio.gather(*self.running_tasks)
        #self.running_tasks.append(asyncio.Task(self.ping()))

        try:
            await self.gather
        except:
            self.quit_async()


online_config = online_config_class()


class trade_screen_class(parent_class):
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

    def __call__(self, player_: int | None = player_turn, queued_prop: int | None = None):
        """
        adds the given player as player 1 of the bid,
        and prompts the player who they would like to trade with.
        
        If there isn't first player, then the current player is chosen

        If a property is given, it will be added to player one's offer,
        after other trading player has been selected
        """
        global current_screen

        try: self.player_1["player"] = int(player_)
        except ValueError: self.player_1["player"] = int(player_turn)
    
        if queued_prop:
            self.player_1["props"].append(queued_prop)

        clear_screen()
        self.action = "player select"
        self.is_trade = True

        current_screen = self.__name__

        self.other_players = []
        self.spacing = []

        print("    ╔════════════════════════════════════════════════════════════════╗")
        print("    ║                                                                ║")
        print("    ║                  CHOOSE PLAYER TO TRADE WITH:                  ║")
        print("    ║                                                                ║")
        print("    ╚════════════════════════════════════════════════════════════════╝")
        print()

        # gets the other players, adds them as available options
        for player_ in player.keys():
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
        global current_screen
        current_screen = self.__name__

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
                prop_ = property_data[self.player_1["props"][i]]
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
                prop_ = property_data[self.player_2["props"][i]]             
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
        for i in property_data:
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
        if property_data[_property]["owner"] == self.player_1["player"]:
            self.player_1["props"].append(_property)
        elif property_data[_property]["owner"] == self.player_2["player"]:
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
        player[self.player_1["player"]]["$$$"] += self.player_2["$$$"]
        player[self.player_2["player"]]["$$$"] += self.player_1["$$$"]

        # subtracts the players offers from their own money
        player[self.player_1["player"]]["$$$"] -= self.player_1["$$$"]
        player[self.player_2["player"]]["$$$"] -= self.player_2["$$$"]

        # updates the properties
        # (I know this is disgustingly long and poorly coded)
        for player_prop in self.player_1["props"]:
            property_data[player_prop]["owner"] = self.player_2["player"]  
            if property_data[player_prop]["type"] == "station":
                continue

            colour_set = []

            for sub_prop in self.player_1["props"]:
                if not ("colour set" in property_data[sub_prop].keys() and "colour set" in property_data[player_prop].keys()):
                    continue

                if property_data[sub_prop]["colour set"] == property_data[player_prop]["colour set"]:
                    colour_set.append(sub_prop)
                         
            # ensures that if all properties in a colour set are traded,
            # they keep relevant upgrade state, otherwise return to default
            if (len(colour_set) == 3 and property_data[player_prop]["colour set"] not in [0, 7]) \
                or (len(colour_set) == 2 and property_data[player_prop]["colour set"] in [0, 7]):

                for _prop in colour_set:
                    if _prop["upgrade state"] != -1:
                        _prop["upgrade state"] = 2
            else:
                for _prop in colour_set:
                    if _prop["upgrade state"] == 2:
                        _prop["upgrade state"] = 1
       
        for player_prop in self.player_2["props"]:
            property_data[player_prop]["owner"] = self.player_1["player"]  
            if property_data[player_prop]["type"] == "station":
                continue

            colour_set = []

            for sub_prop in self.player_1["props"]:
                if not ("colour set" in property_data[sub_prop].keys() and "colour set" in property_data[player_prop].keys()):
                    continue

                if property_data[sub_prop]["colour set"] == property_data[player_prop]["colour set"]:
                    colour_set.append(sub_prop)
                         
            if (len(colour_set) == 3 and property_data[player_prop]["colour set"] not in [0, 7]) \
                or (len(colour_set) == 2 and property_data[player_prop]["colour set"] in [0, 7]):

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

            refresh_board()

        elif self.action == "player select":
            try:
                int(user_input)
            except ValueError:
                
                if user_input in ["b", "B"]:
                    self.player_1 = {"player": None, "$$$": 0, "props": [], "accepted?": False}
                    self.player_2 = {"player": None, "$$$": 0, "props": [], "accepted?": False}
        
                    self.is_trade = False
                    self.action = None
                    refresh_board()

                if self.action != "message":
                    return

                # if the action is 'message' (player wants to trade with themselves)
                self.action = None

                if user_input in ["p", "P"]:
                    self.player_2 = self.player_1
                    self.display_trade_window()
                    print("=== if you insist... ===\n\n    ", end="")

                elif user_input in ["o", "O"]:

                    # clears the conversation and recreates prompts
                    self(self.player_1["player"], self.queued_prop)
                    
            else:
                if user_input in self.other_players:

                    self.player_2["player"] = int(user_input)
                    self.action = None

                    # adds queued property once player selected
                    if self.queued_prop != None:
                        self.add_prop_offer(self.queued_prop)
                        self.queued_prop = None

                    self.curr_player = self.player_1
                    self.display_trade_window()

                elif int(user_input) == self.player_1["player"]: 
                    print("\n    === you can't trade with yourself! ===\n\n")
                    for i in create_button_prompts(["Pleeeeeeease", "Ok"]): print(i)
                    print("\n    ", end="")
                    self.action = "message"

                else:
                    print("\n    === that player does not exist ===\n\n    ", end = "")
         
        elif self.action == "offer screen":
            if user_input in ["o", "O"]:
                self.action = "money"
                print(f"\n    === player {self.curr_player["player"]}, enter cash offer (you can exchange more money than you currently have) ===\n\n    ", end = "")

            elif user_input in ["p","P"]:
                
                has_properties = False
                for i in property_data:
                        if i["owner"] == self.curr_player["player"]:
                            has_properties = True
                            break
                if has_properties == True:
                    display_property_list(self.curr_player["player"])
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
            if player[self.player_1["player"]]["$$$"] < 0:
                broke_alert = True
                player_is_broke(self.player_1["player"], self.player_2["player"])

            elif player[self.player_2["player"]]["$$$"] < 0:
                broke_alert = True
                player_is_broke(self.player_2["player"], self.player_1["player"])
     
            # clears player offers
            self.player_1 = {"player": None, "$$$": 0, "props": [], "accepted?": False}
            self.player_2 = {"player": None, "$$$": 0, "props": [], "accepted?": False}

            # board isn't shown if a player has fallen into debt
            if broke_alert == False:
                refresh_board()
        else:
            print("\n    === command not recognised ===\n\n    ", end = "")

        
trade_screen = trade_screen_class()


class refresh_board_class(parent_class):
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

                return f"{outer} player {turn_spot} | {player[turn_spot]['char']} {outer}"

            def bottom_info():
                outer = extra_space = extra_extra_space = output = ""

                if player_check == turn_spot: outer = "│"
                else: outer = " "

                if player[turn_spot]["status"] in ("playing", "jail"):
                    for i in range(12 - len(str(player[turn_spot]["$$$"]))):
                        extra_space += " "

                    output =  f"{outer} ${player[turn_spot]['$$$']}{extra_space} {outer}"

                # displays the player's status if not playing
                else:
                    for i in range((11 - len(player[turn_spot]["status"])) // 2):
                        extra_space += " "
                    if len(player[turn_spot]["status"]) % 2 == 1:
                        extra_extra_space = " "

                    output = f"{outer}{extra_space} = {player[turn_spot]["status"].upper()} ={extra_extra_space}{extra_space}{outer}"
                return output

            def outer():
                if   player_check == players_playing - (position - 1)    : return "┌───────────────┐"
                elif player_check == players_playing - (alt_position - 1): return "└───────────────┘"
                else                                                    : return "                 "

            # outlines playing player if online, as opposed to current player
            if online_config.game_strt_event.is_set():
                player_check = online_config.player_num
            else:
                player_check = player_turn

            output = "                 " # 17 spaces
            turn_spot = players_playing - (position - 1)

            # check if there is a player to display at this location
            if position <= players_playing: output = locals()[next(self.money_structure)]()
            return output

        def houses(i: int):
            """returns the number of houses the property has"""
            space = lambda: '' if property_data[i]["street value"] >= 100 else ' '

            match property_data[i]["upgrade state"] - 2:
                case 1: return "    🏠    "
                case 2: return "  🏠  🏠  "
                case 3: return "🏠  🏠  🏠"
                case 4: return "🏠 🏠🏠 🏠"
                case 5: return "    🏨    "
                case _: return f"   ${space()}{property_data[i]["street value"]}   "

        def money_change(position: int):
            if position > players_playing:
                return "       "

            output = ""
            change = player[players_playing - (position - 1)]["$$$"] \
                - self.prev_cash[players_playing - position]
            
            if change == 0: return "       " # no change = nothing to display
            elif change < 0: output += "\x1b[31m- " # red text
            else: output += "\x1b[32m+ " # green text
            
            for _ in range(4 - len(str(abs(change)))): output += " " # ensures 7 chars length
            
            output += f"${str(abs(change))}\x1b[0m" # adds value; clears colour change
            return output
            
        # money structure otherwise starts at index 1 from previous use
        self.money_structure.index = -1

        # displays the player whom owns the property if exists
        icon = lambda i: player[property_data[i]["owner"]]["char"] if property_data[i]["owner"] else "  "

        global current_screen

        current_screen = self.__name__
        clear_screen()

        # once player finishes roll, updates player turn player 
        if online_config.game_strt_event.is_set() and player_action.dice_rolled and refresh_board.action == None:
            _list = [item[1]["$$$"] for item in player.items()]

            send_data(f"turnfinished:{player[player_turn]['pos']}:{_list}")
            refresh_board.end_turn_logic()

        # It'll all display fine in terminal, don't worry
        print("")
        print("     ▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁")
        print(f"    \x1b[7m▊\x1b[0m▛               ▎{houses(14)}▎  __()_   ▎{houses(15)}▎{houses(16)}\x1b[0m▎   $200 __\x1b[7m▊\x1b[0m{houses(18)}\x1b[7m▊\x1b[0m{houses(19)}▎   $150   \x1b[7m▊\x1b[0m{houses(21)}\x1b[7m▊\x1b[0m   GO TO JAIL  ▜▎")
        print(f"    \x1b[7m▊\x1b[0m  FREE PARKING  ▎          ▎  \\__ \\   ▎          ▎          \x1b[0m▎_()_()_| /\x1b[7m▊\x1b[0m          \x1b[7m▊\x1b[0m          ▎{player_display_location[28][0]}\x1b[7m▊\x1b[0m          \x1b[7m▊\x1b[0m     {player_display_location[30][0]} ▎")
        print(f"    \x1b[7m▊\x1b[0m      ____      ▎{player_display_location[21][0]}▎{player_display_location[22][0]}▎{player_display_location[23][0]}▎{player_display_location[24][0]}\x1b[0m▎\\  ____ _)\x1b[7m▊\x1b[0m{player_display_location[26][0]}\x1b[7m▊\x1b[0m{player_display_location[27][0]}▎    /\\    \x1b[7m▊\x1b[0m{player_display_location[29][0]}\x1b[7m▊\x1b[0m  /¯¯¯¯\\        ▎")
        print("    \x1b[7m▊\x1b[0m     /[__]\\     ▎          ▎  / /  /\\ ▎          ▎          \x1b[0m▎/__)  /_\\ \x1b[7m▊\x1b[0m          \x1b[7m▊\x1b[0m          ▎   /  \\   \x1b[7m▊\x1b[0m          \x1b[7m▊\x1b[0m | (¯¯)/¯¯¯¯\\   ▎")
        print(f"    \x1b[7m▊\x1b[0m    |_ () _|    ▎          ▎  \\ ‾-‾ / ▎  Fleet   ▎Trafalgar ▎{player_display_location[25][0]}\x1b[7m▊\x1b[0mLeicester \x1b[7m▊\x1b[0m Coventry ▎  |    |  \x1b[7m▊\x1b[0m          \x1b[7m▊\x1b[0m  \\_¯¯| (¯¯) |  ▎")
        print("    \x1b[7m▊\x1b[0m     U----U     ▎  Strand  ▎   ‾---‾  ▎  Street  ▎  Square  \x1b[0m▎Fenchurch \x1b[7m▊\x1b[0m  Square  \x1b[7m▊\x1b[0m  Street  ▎   \\__/   \x1b[7m▊\x1b[0mPiccadilly\x1b[7m▊\x1b[0m    \\/ \\_¯¯_/   ▎")
        print(f"    \x1b[7m▊\x1b[0m   {player_display_location[20][0]}   \x1b[48;2;248;49;47m▎          \x1b[0m▎  CHANCE  \x1b[48;2;248;49;47m▎          ▎          \x1b[0m▎ Station  \x1b[7m▊\x1b[0m\x1b[48;2;255;176;46m          \x1b[30m\x1b[7m▊\x1b[0m\x1b[48;2;255;176;46m          \x1b[0m▎WaterWorks\x1b[7m▊\x1b[0m\x1b[48;2;255;176;46m          \x1b[7m▊\x1b[0m     O   \\/     ▎")
        print("    \x1b[7m▊\x1b[0m                \x1b[48;2;248;49;47m▎          \x1b[0m▎          \x1b[48;2;248;49;47m▎          ▎          \x1b[0m▎          \x1b[7m▊\x1b[0m\x1b[48;2;255;176;46m          \x1b[30m\x1b[7m▊\x1b[0m\x1b[48;2;255;176;46m          \x1b[0m▎          \x1b[7m▊\x1b[0m\x1b[48;2;255;176;46m          \x1b[7m▊\x1b[0m      O O       ▎")
        print("    \x1b[7m▊\x1b[0m▔▔▔▔▔▔▔▔▔▔▔▔\x1b[48;2;255;103;35m▔▔▔▔\x1b[0m▛▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▜\x1b[48;2;0;210;106m▔▔▔▔\x1b[0m▔▔▔▔▔▔▔▔▔▔▔▔▎")
        print(f"    \x1b[7m▊\x1b[0mVine Street \x1b[48;2;255;103;35m    \x1b[0m▎    {icon(14)}                    {icon(15)}         {icon(16)}         {icon(17)}         {icon(18)}         {icon(19)}         {icon(20)}         {icon(21)}    \x1b[7m▊\x1b[0m\x1b[48;2;0;210;106m    \x1b[0m Regent St. ▎")
        print(f"    \x1b[7m▊\x1b[0m {houses(13)} \x1b[48;2;255;103;35m    \x1b[0m▎ {icon(13)}  _____     __          ___    ___  ___   ______     ______       {self.player_turn_display[player_turn][0]}                  {icon(22)} \x1b[7m▊\x1b[0m\x1b[48;2;0;210;106m    \x1b[0m {houses(22)} ▎")
        print(f"    \x1b[7m▊\x1b[0m {player_display_location[19][0]} \x1b[48;2;255;103;35m    \x1b[0m▎    |  _  \\   |  |        /   \\   \\  \\/  /  |  ____|   |  __  \\      {self.player_turn_display[player_turn][1]}                     \x1b[7m▊\x1b[0m\x1b[48;2;0;210;106m    \x1b[0m {player_display_location[31][0]} ▎")
        print(f"    \x1b[7m▊\x1b[0m▁▁▁▁▁▁▁▁▁▁▁▁\x1b[48;2;255;103;35m▁▁▁▁\x1b[0m▎    |  ___/   |  |__     /  ^  \\   \\_  _/   |  __|_    |      /      {self.player_turn_display[player_turn][2]}                     \x1b[7m▊\x1b[0m\x1b[48;2;0;210;106m\x1b[30m▁▁▁▁\x1b[0m▁▁▁▁▁▁▁▁▁▁▁▁▎")
        print(f"    \x1b[7m▊\x1b[0mMarlborough \x1b[48;2;255;103;35m    \x1b[0m▎    |__|      |_____|   /__/¯\\__\\   |__|    |______|   |__|\\__\\      {self.player_turn_display[player_turn][3]}                     \x1b[7m▊\x1b[0m\x1b[48;2;0;210;106m    \x1b[0m            ▎")
        print("    \x1b[7m▊\x1b[0m   Street   \x1b[48;2;255;103;35m    \x1b[0m▎                                                                                                  \x1b[7m▊\x1b[0m\x1b[48;2;0;210;106m    \x1b[0m Oxford St. ▎")
        print(f"    \x1b[7m▊\x1b[0m {houses(12)} \x1b[48;2;255;103;35m    \x1b[0m▎ {icon(12)}   ____       _____      __                                                                 {icon(23)} \x1b[7m▊\x1b[0m\x1b[48;2;0;210;106m    \x1b[0m {houses(23)} ▎")
        print(f"    \x1b[7m▊\x1b[0m {player_display_location[18][0]} \x1b[48;2;255;103;35m    \x1b[0m▎     /  __|     /     \\    |  |                                                                   \x1b[7m▊\x1b[0m\x1b[48;2;0;210;106m    \x1b[0m {player_display_location[32][0]} ▎")
        print("    \x1b[7m▊\x1b[0m▁▁▁▁▁▁▁▁▁▁▁▁\x1b[48;2;255;103;35m▁▁▁▁\x1b[0m▎    |  |_  |   |  (_)  |   |__|                                                                   \x1b[7m▊\x1b[0m\x1b[48;2;0;210;106m▁▁▁▁\x1b[0m▁▁▁▁▁▁▁▁▁▁▁▁▎")
        print("    \x1b[7m▊\x1b[0m COMUNITY CHEST ▎     \\____/     \\_____/    (__)                                                                   \x1b[7m▊\x1b[0m COMUNITY CHEST ▎")
        print(f"    \x1b[7m▊\x1b[0m   {player_display_location[17][0]}   ▎                                                                                                  \x1b[7m▊\x1b[0m   {player_display_location[33][0]}   ▎")
    
        button_states = [False, True, False, True]

        # checks if the players owns any properties, button is 'trade' otherwise
        x = better_iter(property_data)
        prompt_2 = "Trade"
        while prompt_2 == "Trade":
            try:
                check_prop = next(x)

            # if all properties have been checked, loop is broken
            except tripple_affirmative:
                break

            # if player has properties, the prompt is changed and loop broken
            if check_prop["owner"] == player_turn: 
                prompt_2 = "Properties"
                break

        # additional logic is required for online
        online_check = lambda: True if (online_config.player_num == player_turn or not online_config.game_strt_event.is_set()) else False

        # similar checks are performed for the other prompts
        # if the player has spent 3 turns in jail, they MUST pay bail, regardless of conditions
        button_states[0] = (online_check() and player_action.dice_rolled == False \
            and self.action == None and player[player_turn]["jail time"] < 3)

        if (self.action == None and player_action.dice_rolled == True) or \
                (online_config.game_strt_event.is_set() and online_config.socket_type == "host"):
            button_states[2] = True

        if online_config.game_strt_event.is_set():
            if online_config.socket_type == "client":
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
            if player[player_turn]["$$$"] < property_data[prop_from_pos[player[player_turn]["pos"]]]["street value"]: button_states[1][1] = False

        elif player[player_turn]["status"] == "jail":
            button_states[0] = ["Give bail $", "Use card"]
         
            if player[player_turn]["$$$"] < 50        : button_states[1][0] = False
            if player[player_turn]["jail passes"] == 0: button_states[1][1] = False
        button_list = create_button_prompts(button_states[0], button_states[1], [0, 3])

        print(f"    \x1b[7m▊\x1b[0m {houses(11)} \x1b[48;2;255;103;35m    \x1b[0m▎ {icon(11)} {button_list[0]}                                                    {icon(24)} \x1b[7m▊\x1b[0m\x1b[48;2;0;210;106m    \x1b[0m {houses(24)} ▎")
        print(f"    \x1b[7m▊\x1b[0m {player_display_location[16][0]} \x1b[48;2;255;103;35m    \x1b[0m▎    {button_list[1]}                                                       \x1b[7m▊\x1b[0m\x1b[48;2;0;210;106m    \x1b[0m {player_display_location[34][0]} ▎")
        print(f"    \x1b[7m▊\x1b[0m\x1b[▁▁▁▁▁▁▁▁▁▁▁▁▁\x1b[48;2;255;103;35m▁▁▁▁\x1b[0m▎    {button_list[2]}                                                       \x1b[7m▊\x1b[0m\x1b[48;2;0;210;106m▁▁▁▁\x1b[0m▁▁▁▁▁▁▁▁▁▁▁▁▎")
        print(f"    \x1b[7m▊\x1b[0m |\\⁔ Marylebone ▎    {button_list[3]}                                                       \x1b[7m▊\x1b[0m Liverpool|∖↙() ▎")
        print("    \x1b[7m▊\x1b[0m ¯| |◁ Station  ▎                                                                                                  \x1b[7m▊\x1b[0m Station  |‿ |  ▎")
        print(f"    \x1b[7m▊\x1b[0m () |  $200     ▎ {icon(10)}                                                                                            {icon(25)} \x1b[7m▊\x1b[0m $200      | () ▎")
        print(f"    \x1b[7m▊\x1b[0m  | ⁀|{player_display_location[15][0]}▎                                                                                                  \x1b[7m▊\x1b[0m{player_display_location[35][0]}▷|‿|_ ▎")
        print("    \x1b[7m▊\x1b[0m▁()↗∖|▁▁▁▁▁▁▁▁▁▁▎                                                                                                  \x1b[7m▊\x1b[0m▁▁▁▁▁▁▁▁▁▁▁▁▁\\|▁▎")
        print("    \x1b[7m▊\x1b[0mNorthumb'nd \x1b[48;2;245;47;171m    \x1b[0m▎                                                                                                  \x1b[7m▊\x1b[0m      _  CHANCE ▎")
        print("    \x1b[7m▊\x1b[0m   Avenue   \x1b[48;2;245;47;171m    \x1b[0m▎                                                                                                  \x1b[7m▊\x1b[0m    /‾_‾\\|‾|    ▎")
        print(f"    \x1b[7m▊\x1b[0m {houses(9)} \x1b[48;2;245;47;171m    \x1b[0m▎ {icon(9)}                                                                                               \x1b[7m▊\x1b[0m   | | \\_  | () ▎")
        print(f"    \x1b[7m▊\x1b[0m {player_display_location[14][0]} \x1b[48;2;245;47;171m    \x1b[0m▎                                                                                                  \x1b[7m▊\x1b[0m    \\_\\{player_display_location[36][0]}▎")
        print("    \x1b[7m▊\x1b[0m▁▁▁▁▁▁▁▁▁▁▁▁\x1b[48;2;245;47;171m▁▁▁▁\x1b[0m▎                                                                                                  \x1b[7m▊\x1b[0m▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▎")
  
        # ensures that floats aren't shown due to my bad code
        for player_ in player.items(): player_[1]["$$$"] = int(player_[1]["$$$"])
        
        print(f"    \x1b[7m▊\x1b[0m            \x1b[48;2;245;47;171m    \x1b[0m▎                                                                             {display_money(4)}    \x1b[7m▊\x1b[0m\x1b[48;2;28;89;255m    \x1b[0m            ▎")
        print(f"    \x1b[7m▊\x1b[0m Whitehall  \x1b[48;2;245;47;171m    \x1b[0m▎                                                                             {display_money(4)}    \x1b[7m▊\x1b[0m\x1b[48;2;28;89;255m    \x1b[0m Park Lane  ▎")    
        print(f"    \x1b[7m▊\x1b[0m {houses(8)} \x1b[48;2;245;47;171m    \x1b[0m▎ {icon(8)}                                                                  {money_change(4)} {display_money(4)} {icon(26)} \x1b[7m▊\x1b[0m\x1b[48;2;28;89;255m    \x1b[0m {houses(26)} ▎")
        print(f"    \x1b[7m▊\x1b[0m {player_display_location[13][0]} \x1b[48;2;245;47;171m    \x1b[0m▎                                                                             {display_money(3, 4)}    \x1b[7m▊\x1b[0m\x1b[48;2;28;89;255m    \x1b[0m {player_display_location[37][0]} ▎")
        print(f"    \x1b[7m▊\x1b[0m▁▁▁▁▁▁▁▁▁▁▁▁\x1b[48;2;245;47;171m▁▁▁▁\x1b[0m▎                                                                             {display_money(3)}    \x1b[7m▊\x1b[0m\x1b[48;2;28;89;255m▁▁▁▁\x1b[0m▁▁▁▁▁▁▁▁▁▁▁▁▎")
        print(f"    \x1b[7m▊\x1b[0m Electric Co.   ▎                                                                     {money_change(3)} {display_money(3)}    \x1b[7m▊\x1b[0m ∖  ⁄ SUPER TAX ▎")
        print(f"    \x1b[7m▊\x1b[0m $150       |\\  ▎                                                                             {display_money(2, 3)}    \x1b[7m▊\x1b[0m- 💎 -     $100 ▎")
        print(f"    \x1b[7m▊\x1b[0m          __| \\ ▎ {icon(7)}                                                                          {display_money(2)}    \x1b[7m▊\x1b[0m/¯¯¯¯\\{player_display_location[38][0]}▎")
        print(f"    \x1b[7m▊\x1b[0m{player_display_location[12][0]}\\ |¯¯ ▎                                                                     {money_change(2)} {display_money(2)}    \x1b[7m▊\x1b[0m (⁐⁐) |         ▎")   
        print(f"    \x1b[7m▊\x1b[0m           \\|   ▎                                                                             {display_money(1, 2)}    \x1b[7m▊\x1b[0m\\____/\x1b[0m          ▎")
        print(f"    \x1b[7m▊\x1b[0m▔▔▔▔▔▔▔▔▔▔▔▔\x1b[48;2;245;47;171m▔▔▔▔\x1b[0m▎                                                                             {display_money(1)}    \x1b[7m▊\x1b[0m\x1b[48;2;28;89;255m▔▔▔▔\x1b[0m▔▔▔▔▔▔▔▔▔▔▔▔▎")
        print(f"    \x1b[7m▊\x1b[0m Pall Mall  \x1b[48;2;245;47;171m    \x1b[0m▎                                                                     {money_change(1)} {display_money(1)}    \x1b[7m▊\x1b[0m\x1b[48;2;28;89;255m    \x1b[0m   Mayfair  ▎")
        print(f"    \x1b[7m▊\x1b[0m {houses(6)} \x1b[48;2;245;47;171m    \x1b[0m▎ {icon(6)}                                                                          {display_money(0, 1)} {icon(27)} \x1b[7m▊\x1b[0m\x1b[48;2;28;89;255m    \x1b[0m {houses(27)} ▎")
        print(f"    \x1b[7m▊\x1b[0m {player_display_location[11][0]} \x1b[48;2;245;47;171m    \x1b[0m▎    {icon(5)}         {icon(4)}                    {icon(3)}         {icon(2)}                    {icon(1)}                    {icon(0)}    \x1b[7m▊\x1b[0m\x1b[48;2;28;89;255m    \x1b[0m {player_display_location[39][0]} ▎")
        print("    \x1b[7m▊\x1b[0m▁▁▁▁▁▁▁▁▁▁▁▁\x1b[48;2;245;47;171m▁▁▁▁\x1b[0m▙▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▟\x1b[0m\x1b[48;2;28;89;255m▁▁▁▁\x1b[0m▁▁▁▁▁▁▁▁▁▁▁▁▎")
        print(f"    \x1b[7m▊\x1b[0m      │ ║ ║ ║ ║ \x1b[48;2;0;166;237m▎          \x1b[30m│          \x1b[0m▎  CHANCE  \x1b[48;2;0;166;237m▎          \x1b[0m▎  King's  ▎          \x1b[48;2;165;105;83m▎          \x1b[0m▎ COMUNITY \x1b[7m▊\x1b[0m\x1b[48;2;165;105;83m          \x1b[7m▊\x1b[0m  ____    ____  ▎")
        print(f"    \x1b[7m▊\x1b[0m   J  │ J A I L \x1b[48;2;0;166;237m▎          \x1b[30m│          \x1b[0m▎  _---_   \x1b[48;2;0;166;237m▎          \x1b[0m▎  Cross   ▎  INCOME  \x1b[48;2;165;105;83m▎          \x1b[0m▎   CHEST  \x1b[7m▊\x1b[0m\x1b[48;2;165;105;83m          \x1b[7m▊\x1b[0m /  __|  /    \\ ▎")
        print(f"    \x1b[7m▊\x1b[0m   U  │ ║ ║ ║ ║ ▎Pent'ville│  Euston  ▎ / _-_ \\  ▎The Angel ▎{player_display_location[5][0]}▎   TAX    ▎whitechp'l▎{player_display_location[2][0]}\x1b[7m▊\x1b[0m Old Kent \x1b[0m\x1b[7m▊\x1b[0m|  |_ ‾||  ()  |▎")
        print(f"    \x1b[7m▊\x1b[0m   S  │{player_display_location[40][0]}▎   Road   │   Road   ▎ \\/  / /  ▎Islington ▎ \\¯/___(¯/▎          ▎   Road   ▎          \x1b[7m▊\x1b[0m   Road   \x1b[7m▊\x1b[0m \\____/  \\____/ ▎")
        print(f"    \x1b[7m▊\x1b[0m   T  │_║_║_║_║_▎          │          ▎   / /_   ▎          ▎( _______\\▎    🔷    ▎          ▎🪙  💰  💵\x1b[7m▊\x1b[0m          \x1b[0m\x1b[7m▊\x1b[0m{player_display_location[0][0]}____  ▎")
        print(f"    \x1b[7m▊\x1b[0m   {player_display_location[10][0]}   ▎{player_display_location[9][0]}│{player_display_location[8][0]}▎   \\___\\  ▎{player_display_location[6][0]}▎/_| () () ▎{player_display_location[4][0]}▎{player_display_location[3][0]}▎  💵  💰  \x1b[7m▊\x1b[0m{player_display_location[1][0]}\x1b[7m▊\x1b[0m  /|-----/   /  ▎")
        print(f"    \x1b[7m▊\x1b[0m    VISITING    ▎{houses(5)}│{houses(4)}▎{player_display_location[7][0]}▎{houses(3)}▎{houses(2)}▎ PAY $200 ▎{houses(1)}▎💰  🪙  💵\x1b[7m▊\x1b[0m{houses(1)}\x1b[7m▊\x1b[0m  \\|-----\\___\\  ▎")
        print("    \x1b[7m▊\x1b[0m▙               ▎          │          ▎          ▎          ▎          ▎          ▎          ▎          \x1b[7m▊\x1b[0m          \x1b[0m\x1b[7m▊\x1b[0m               ▟▎")
        print("     ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔ ")

        # devmode commands are listed here
        if dev_mode == True:
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
            print("    \"arbitrarycode\"")
            print("    \"setbidqueue\"")
            print("    \"dumpsave\"")
            print()
        
        if self.passed_go == True:
            for line in self.passed_go_art: print(f"    {line}")
            print()
            self.passed_go = False

        print("    ", end="")

        for item in player.items():
            self.prev_cash[item[0] - 1] = item[1]["$$$"]

    def input_management(self, user_input):
        global dev_mode
        global player_turn

        if self.action == "trade query" and user_input in ["y", "Y"]:
            trade_screen(player_turn)

        elif self.action == "trade query":
            self.action = None

        elif self.action == "dice_roll_accept":
            self.action = None
            # moves the cursor above the dice ('ESC[11F') and clears everything below ('ESC[0J')
            print("\x1b[11F\x1b[0J")

            player_action.move()

        elif self.action == "chance notice":
            self.action = None
            chance.perform_action()

        elif self.action == "community chest notice":
            self.action = None
            community_chest.perform_action()

        elif self.action == "save notice":
            self.action = None
            homescreen()

        elif self.action == "kick user":
            for item in online_config.joined_clients:
                if item[3] == user_input:
                    item[1].sendall(b"booted")
                    self.disconnect_management(item[3])
                    break
            else:
                print("\n    === invalid user ID ===\n\n    ", end = "")

        elif user_input in ["r", "R"]:
            if (player_action.dice_rolled == False and self.action == None \
                and player[player_turn]["jail time"] < 3):
                
                # additional logic is required for online
                if online_config.game_strt_event.is_set() and online_config.player_num != player_turn:
                    print("\n    === it's not your turn ===\n\n    ", end="")
                    return

                refresh_board()
                player_action.start_roll()
            elif dev_mode:
                input("\n    === skipped with devmode [Enter] ===\n\n    ", end="")

                refresh_board()
                player_action.start_roll()

            elif self.action != None:
                print("\n    === complete space-dependent action first ===\n\n    ", end="")
            else:
                print("\n    === you've already rolled ===\n\n    ", end = "")

        elif user_input in ["p", "P"]:
            has_properties = False
            for i in range(28):
                if property_data[i]["owner"] == player_turn:
                    has_properties = True
                    break

            if has_properties == False:
                print("\n    === you don't own any properties ===\n\n    ", end = "")
            else:
                display_property_list(player_turn)

        elif user_input in ["t", "T"]:
            trade_screen(player_turn)

        elif user_input in ["e", "E"] and not online_config.game_strt_event.is_set():
            if (player_action.dice_rolled == True and self.action == None) or dev_mode == True:
                next(player_turn)
                player_action.dice_rolled = False
                player_action.doubles_rolled = 0

                # when a player goes bankrupt, players alive are checked,
                # so there will be at least 2 people when this code is active.
                while player[player_turn]["status"] in ("bankrupt", "disconnected"): next(player_turn)
                
                # forcibly moves the player out of jail if they've been in for 3 turns,
                # and they don't have a card
                if player[player_turn]["jail time"] >= 3 and player[player_turn]["jail passes"] == 0:
                    player_action.remove_from_jail(player_turn)
                    player[player_turn]["$$$"] -= 50

                    if player[player_turn]["$$$"] < 0: player_is_broke(player_turn)
                    
                refresh_board()
                
            else: 
                print("\n    === roll dice first and complete space-dependent action first ===\n\n    ", end = "")
                
        elif user_input in ["s", "S"]:
            global players_playing
            global house_total
            global hotel_total
            global time_played
            global game_version

            if online_config.game_strt_event.is_set():
                send_data("clientquit")

            save_game_to_file(
                "game_version", "players_playing", "player_turn", "player_action.doubles_count",
                "dev_mode", "player_action.dice_rolled", "refresh_board.action", "player", "chance.values",
                "chance.index", "community_chest.values", "community_chest.index"
            )
            self.action = "save notice"
            self.prev_cash = [0, 0, 0, 0]
            self.passed_go = False
            
            # forcibly resets all variables in case user 
            # starts new game without restarting program
            players_playing = 0
            dev_mode = False
            house_total = 32
            hotel_total = 12
            time_played = 0
            game_version = 0.7
            player_turn = None

            for prop in property_data:
                prop["owner"] = None
                prop["upgrade state"] = 0

            # resets all attribute for my custom classes  
            for item in globals():
                if isinstance(item, parent_class):
                    item.__init__()

            print("\n    === game saved. [Enter] to return to the main menu ===\n\n    ", end = "")

        elif user_input in ["b", "B"] and self.action == "property":
            _prop = property_data[prop_from_pos[player[player_turn]["pos"]]]

            # the property isn't purchased if the player cannot afford it
            if player[player_turn]["$$$"] < _prop["street value"]:
                print("\n    === you can't afford this property ===\n\n    ", end="")
                return
            
            _prop["owner"] = int(player_turn)
            _prop["upgrade state"] = 1
            player[player_turn]["total properties"] += 1
            player[player_turn]["$$$"] -= _prop["street value"]

            colour_set = []
            for prop in property_data:
                if not ("colour set" in prop.keys() and "colour set" in _prop.keys()):
                    continue

                if prop["colour set"] == _prop["colour set"] and prop["owner"] == _prop["owner"]:
                    colour_set.append(prop)
                         
            # brown and dark blue (sets 0 and 7) only have two properties in their set
            if (len(colour_set) == 3 and _prop["colour set"] not in [0, 7]) \
                or (len(colour_set) == 2 and _prop["colour set"] in [0, 7]):

                for _prop in colour_set: _prop["upgrade state"] = 2

            self.action = None
            refresh_board()

        elif user_input in ["a", "A"] and self.action == "property":
            auctioned_property = prop_from_pos[player[player_turn]["pos"]]
            display_property(auctioned_property, bid = True)

        elif user_input in ["g", "G"] and player[player_turn]["status"] == "jail":
            
            # moving the player to just visiting
            if player[player_turn]["$$$"] >= 50:
                player[player_turn]["$$$"] -= 50
                player_action.remove_from_jail(player_turn)
            else:
                print("\n    === you cannot afford bail ===\n\n    ", end = "")

        elif user_input in ["u", "U"] and player[player_turn]["status"] == "jail":
            if player[player_turn]["jail passes"] > 0:
                player[player_turn]["jail passes"] -= 1
                player_action.remove_from_jail(player_turn)
            else:
                print("\n    === you don't have any get out of jail free cards to use ===\n\n    ", end = "")

        elif user_input in ["k", "K"] and online_config.game_strt_event.is_set() \
                and online_config.socket_type == "host":
            self.action = "kick user"
            print("\n    === enter ID of player you wish to kick ===\n")

            for item in online_config.joined_clients:
                print(f"    [{item[3]}] {item[0]}")
            print("\n    ", end="")

        elif user_input == "devmode":
            dev_mode = True
            refresh_board()

        # certainly all of these input()s won't cause online issues
        elif user_input == "setplayerpos" and dev_mode == True:
            x = input("    === which player: ")
            xx = input("    === set pos: ")
            player[int(x)]["last pos"] = player[int(x)]["pos"]
            player[int(x)]["pos"] = int(xx)
            update_player_position(int(xx))
            update_player_position(player[int(x)]["last pos"], "remove")
            if player[int(x)]["pos"] == 40: player[int(x)]["status"] = "jail"
            refresh_board()
            player_action(int(x))

        elif user_input == "showplayerdict" and dev_mode == True:
            for i in player:
                print(f"{i}: {player[i]}")

        elif user_input == "setdiceroll" and dev_mode == True:
            player_action.dice_value[1] = int(input("    === first dice value: "))
            player_action.dice_value[2] = int(input("    === second dice value: "))
            player_action.move()
           
        elif user_input == "bankruptcy" and dev_mode == True:
            x = input("    === which player: ")
            player_is_broke(int(x))

        elif user_input ==  "editplayerdict" and dev_mode == True:
            print("    === Please edit position using the 'setplayerpos' command ===")
            x = input("    === which player: ")
            xx = input("    === which key: ")
            xxx = input("    === what value: ")
            try   : player[int(x)][xx] = int(xxx)
            except ValueError: player[int(x)][xx] = xxx

        elif user_input == "propertybid" and dev_mode == True:
            auctioned_property = int(input("    === enter property number: "))

            # since bidding will require 'player_turn' to change, this stores the proper player turn
            display_property.true_player_turn = player_turn.index
            display_property.action = "auction"
            display_property(auctioned_property)

        elif user_input == "showproplist" and dev_mode == True:
            for i in property_data:
                print(i)

        elif user_input == "showchangedprops" and dev_mode == True:
            for i in property_data:
                if i["owner"] != None:
                    print(i)

        elif user_input == "setplayerprops" and dev_mode == True:
            x = int(input("    === what player: "))
            xx = input("    === what property (commands: 'all', 'done'): ")
            while xx != "done":
                if xx == "all":
                    for i in range(28): property_data[i]["owner"] = x; property_data[i]["upgrade state"] = 1
                    xx = "done"
                else:
                    try:
                        int(xx)
                    except ValueError:
                        print("=== invalid number ===")
                        xx = input("    === what property (commands: 'all', 'done'): ") 
                        continue
                    property_data[int(xx)]["owner"] = x
                    property_data[int(xx)]["upgrade state"] = 1

                    # checks if the player now owns all the properties in a colour set
                    colour_set = []
                    for prop in property_data:
                        if not ("colour set" in prop.keys() and "colour set" in property_data[int(xx)].keys()):
                            continue

                        if prop["colour set"] == property_data[int(xx)]["colour set"] and prop["owner"] == property_data[int(xx)]["owner"]:
                            colour_set.append(prop)
                         
                    # brown and dark blue (sets 0 and 7) only have two properties in their set
                    if ((len(colour_set) == 3 and property_data[int(xx)]["colour set"] not in [0, 7])
                        or (len(colour_set) == 2 and property_data[int(xx)]["colour set"] in [0, 7])):

                        for _prop in colour_set: _prop["upgrade state"] = 2
                    xx = input("    === what property (commands: 'all', 'done'): ") 
            refresh_board()

        elif user_input == "forcechancecard" and dev_mode == True:
            x = int(input("    === what player: "))
            xx = input("    === what card value: ")
            if len(xx) == 1: xx = xx + " "

            for i in range(len(chance.cards_value)):
                if chance.cards_value[i] == xx:
                    chance.index = i

            chance.perform_action()

        elif user_input == "forcecccard" and dev_mode == True:
            x = int(input("    === what player: "))
            xx = input("    === what card value: ")

            if len(xx) == 1: xx = xx + " "

            for i in range(len(community_chest.cards_value)):
                if community_chest.cards_value[i] == xx:
                    community_chest.index = i

            chance.perform_action()

        elif user_input == "displayvar" and dev_mode == True:
            x = input("enter var:")
            if x in globals():
                print(globals()[x])
            else:
                print("    === variable not found ===\n\n    ", end = "")

        elif user_input == "queuechance" and dev_mode == True:
            card = int(input("    === enter num: "))
            chance.values.remove(card)
            chance.values.insert(chance.index + 1, card)

        elif user_input == "arbitrarycode" and dev_mode == True:
            exec(input())

        elif user_input == "setbidqueue" and dev_mode == True:
            u_input = ''
            queue = []
            while u_input != "done":
                u_input = input("enter property (commands: 'done'): ")

                try: queue.append(int(u_input))
                except ValueError: pass

            input(f"confirm: {queue}")
            display_property(*queue, bid = True)

        elif user_input == "dumpsave" and dev_mode == True:
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

        if online_config.socket_type == "client":
            index = online_config.joined_clients[2].index(quitter)
            name = online_config.joined_clients[0][index]
        else:
            for item in online_config.joined_clients:
                if item[3] == quitter:
                    name = item[0]
                    break

        print(f"=== {name} lost connection to game ===\n\n    ", end="")

    def end_turn_logic(self):
        """increments the player turn, handles edge cases"""
        global player_turn

        next(player_turn)
        player_action.dice_rolled = False
        player_action.doubles_rolled = 0

        # when a player goes bankrupt, players alive are checked,
        # so there will be at least 2 people when this code is active.
        while player[player_turn]["status"] in ("bankrupt", "disconnected"): next(player_turn)
                
        # forcibly moves the player out of jail if they've been in for 3 turns,
        # and they don't have a card
        if player[player_turn]["jail time"] >= 3 and player[player_turn]["jail passes"] == 0:
            player_action.remove_from_jail(player_turn)
            player[player_turn]["$$$"] -= 50

            if player[player_turn]["$$$"] < 0: player_is_broke(player_turn)


refresh_board = refresh_board_class()


class display_game_notice_class(parent_class):
    def __call__(self):
        global current_screen
        current_screen = self.__name__

        clear_screen()

        print()
        print("    ╔════════════════════════════════════════════════════════════════╗")
        print("    ║                                                                ║")
        print("    ║                             NOTICE:                            ║")
        print("    ║                                                                ║")
        print("    ║                 To display the board properly,                 ║")
        print("    ║           you may need to resize text or the window            ║")
        print("    ║                                                                ║")
        print("    ║                             [enter]                            ║")
        print("    ╚════════════════════════════════════════════════════════════════╝")
        print()
        print("    |<──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────>|")
        print()
        print("    the board is the length of this line, adjust until the line doesn't wrap around your screen.\n    ", end = "")

    def input_management(self, user_input):
        global start_time
        start_time = time()
        refresh_board()


display_game_notice = display_game_notice_class()


class new_game_select_class(parent_class):
    def __init__(self):
        self.action = None

    def __call__(self):
        clear_screen()

        global current_screen
        global player_turn

        current_screen = self.__name__

        print()
        if self.action == "name input":
            print("    === enter player icons ===")
        else:
            print("    === choose number of players ===")
        print()

        if players_playing == 0:
            button_states = [True, True, True, True]
        elif players_playing == 2:
            button_states = [True, False, False, True]
        elif players_playing == 3:
            button_states = [False, True, False, True]
        elif players_playing == 4:
            button_states = [False, False, True, True]

        for i in create_button_prompts(["2 players", "3 players", "4 players", "Back"], button_states, [4, 3, 3, 6]):
            print(i)
        print()

        # this is displaying each players's character
        if self.action != "name input":
            print("    ", end="")
            return

        print("    ____________________________________________________________________________________")
        print("")

        if player_turn == 1:
            print("    Player 1: ", end="")
        elif player_turn == 2:
            print(f'    Player 1: {player[1]["char"]}')
            print("    Player 2: ", end="")
        elif player_turn == 3:
            print(f'    Player 1: {player[1]["char"]}')
            print(f'    Player 2: {player[2]["char"]}')
            print("    Player 3: ", end="")
        elif player_turn == 4:
            print(f'    Player 1: {player[1]["char"]}')
            print(f'    Player 2: {player[2]["char"]}')
            print(f'    Player 3: {player[3]["char"]}')
            print("    Player 4: ", end="")

    def input_management(self, user_input):
        global players_playing
        global player_turn
        global player

        if user_input in ["2", "3", "4"]:

            players_playing = int(user_input)
            player_turn = better_iter(range(1, players_playing + 1), True)

            self.action = "name input"
            player = {}

            for i in range(players_playing):

                # players start at 1, not 0
                player[i + 1] = {
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

                    # separate to the game version for online games
                    "version": game_version
                }

            self()

        elif user_input in ["b", "B"]:
            self.action = None
            players_playing = 0
            homescreen()
            
        # recording entered names
        elif self.action == "name input":

            # enforces 2 characters width for name
            name_width = 0
            for char in user_input:
                if width(char) in ("F", "W"): name_width += 2
                else: name_width += 1
            
            if user_input in ["  ", r"\\"]:
                print("\n    === nice try. ===\n\n    ", end = "")
                return

            elif name_width > 2:
                print("\n    === icon too large, try a different icon (eg: '😊' or 'JE') ===\n\n    ", end="")
                return

            elif name_width < 2:
                print("\n    === icon too small, try a different icon (eg: '😊' or 'JE') ===\n\n    ", end="")
                return

            # in theory better_iters should use __hash__ or __index__ automatically,
            # but player_turn is feeling uncooperative today
            player[int(player_turn)]["char"] = user_input
            next(player_turn)

            if player_turn == 1:
                self.action = None

                update_player_position(0)

                display_game_notice()
            else:
                self()
        else:
            print("\n    === command not recognised ===\n\n    ", end = "")


new_game_select = new_game_select_class()


def read_save(
        _file: str | None = "save_file.james",
        _encoding: str | None = "utf-8"):
    """reads save_file.james as python code"""
    savefile = open(_file, encoding = _encoding)

    # game version will get overwritten, so a copy is recorded to
    # compare with save version to make sure they're the same
    true_game_version = game_version
    
    # totally secure 😎
    for _line in savefile:
        exec(_line, globals())
   
    # this subtracts the time played on the save from the start time,
    # so the end-screen calculations reflect the extra time played
    global start_time
    start_time = time() - time_played

    for item in player.values():
        update_player_position(item["pos"])


    if game_version != true_game_version:
        raise Exception("=== save is not the same version as game ===")


def save_game_to_file(*variables: str):
    """
    writes given variables, modified properties, and time played to
    'save_file.james'. the save is created if it does not exist
    """

    save_file = open("save_file.james", "w", encoding="utf-8")

    save_file.write("# Wonder what happens if you mess with the save? Stuff around and find out.\n")
    save_file.write("# (note: the save is read using 'exec()', so any python code can be added ;))\n\n")

    for var in variables:

        if isinstance(eval(var), better_iter):
            save_file.write(f"{var} = better_iter({eval(var).list}, {eval(var).loop}, {eval(var).index})\n")
        else:
            save_file.write(f"{var} = {eval(var)}\n")

    # since only modified properties are saved, they have their own check
    for i in range(28):
        if property_data[i]["owner"] != None:
            save_file.write(f"property_data[{i}].update({{'owner': {property_data[i]['owner']},"
                            f"'upgrade state': {property_data[i]['upgrade state']}}})\n")

    # the time is rounded to the nearest second
    save_file.write(f"time_played = {str(round(time() - start_time))}\n")

    save_file.close()


def bankruptcy(_player: int | None = player_turn, cause = "bank" or "disconnected" or 1/2/3/4):
    """
    determines how to handle a player's bankruptcy, based on cause,
    and displays win/game finished screen if applicable
    """
    global player_turn
    global house_total
    global hotel_total

    # ensures no key errors
    _player = int(_player)

    if cause == "disconnected":
        player[_player]["status"] = "disconnected"
        cause = "bank"
    else:
        player[_player]["status"] = "bankrupt"
    
    # this is checking how many players remain after a bankruptcy
    remaining_players = 0
    for i in player.items():
        if i[1]["status"] in ("playing", "jail"): remaining_players += 1

    # if only one player remains, then the game finished screen is displayed
    # otherwise, the rest of the function is performed
    if remaining_players == 1:

        # total amount of seconds played
        _total = round(time() - start_time)

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
        for item in player.items():
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

        if online_config.game_strt_event.is_set():
            raise exit_async
        return

    # finds next competing player
    next(player_turn)
    while player[player_turn]["status"] in ("bankrupt", "disconnected"):
        next(player_turn)

    # adds houses and hotels back as available
    for _property in property_data:
        if _property["owner"] != _player:
            continue

        if _property["upgrade state"] == 8:
            hotel_total += 1
            house_total += 4
        elif _property["upgrade state"] > 2:
            house_total += _property["upgrade state"] - 2

    # player_is_broke passes on None as cause
    if cause == None: cause = "bank"

    # if the player is in debt to the bank, 
    # all properties are returned then auctioned
    if cause == "bank":
        auction_queue = []
        for i in range(len(property_data)):
            if property_data[i]["owner"] != _player:
                continue

            # properties remained mortgaged, but don't keep any upgrades
            if property_data[i]["upgrade state"] != -1:
                property_data[i]["upgrade state"] == 0
            property_data[i]["owner"] = None
            auction_queue.append(i)

        # auctions properties if any exist
        if len(auction_queue) > 0:
            display_property(*auction_queue, bid = True)
        else:
            refresh_board()

    # for some stupid reason, upgrades on properties are not transferred,
    # but are sold and the money is given to the owed player instead.
    # (monopoly's stupid rules not mine)
    else:
        owed_player = int(cause)
        for _property in property_data:
            if _property["owner"] != _player:
                continue

            _property["owner"] = owed_player
            upgrades = _property["upgrade state"] - 2
            
            # houses are sold back to bank for half price
            if upgrades > 0:
                player[owed_player]["$$$"] += upgrades * (_property["house cost"] / 2)

            # upgraded properties have to be part of a colour set,
            # and so are reset to state 2, while un-upgraded properties remain as is
            if _property["upgrade state"] > 2:
                _property["upgrade state"] = 2

        # transfers any escape jail cards to the other player
        player[owed_player]["jail passes"] += player[_player]["jail passes"]
        player[owed_player]["$$$"] += player[_player]["$$$"]


class player_action_class(parent_class):
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
    
    def __call__(self, _player: int | None = player_turn):
        """updates actions based on given player's position"""

        # chance + C.C card actions
        if player[_player]["pos"] in [7, 22, 36]:
            refresh_board.action = "chance notice"

            print(chance.art[0])
            print(f"    {chance.art[1]}")
            print(f"    {chance.art[2]}")
            print()
            print(f"    === {chance.draw_card()} ===\n\n    ", end="")

        elif player[_player]["pos"] in [2, 17, 33]:
            refresh_board.action = "community chest notice"

            print(community_chest.art[0])
            print(f"    {community_chest.art[1]}")
            print(f"    {community_chest.art[2]}")
            print()
            print(f"    === {community_chest.draw_card()} ===\n\n    ", end="")

        # income & super tax
        elif player[_player]["pos"] == 4:
            player[player_turn]["$$$"] -= 200

        elif player[_player]["pos"] == 38:
            player[player_turn]["$$$"] -= 100

        # go to jail space
        elif player[_player]["pos"] == 30:
            self.send_to_jail()

        # properties
        elif player[_player]["pos"] not in [0, 10, 20, 40]:
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

        _prop = prop_from_pos[player[_player]["pos"]]
        _owner = property_data[_prop]["owner"]
        if _owner == None:
            refresh_board.action = "property"
            return

        elif property_data[_prop]["upgrade state"] == -1:
            return

        elif rent_fixed != None:
            player[_player]["$$$"] -= rent_fixed * rent_multi
            player[_owner]["$$$"] += rent_fixed * rent_multi
                 
        elif property_data[_prop]["type"] == "utility":

            # if the player ownes both utilities (rent = 10x dice roll)
            if property_data[7]["owner"] == _owner and property_data[10]["owner"] == _owner:
                    
                # if the multiplier is default (1), it is changed to 10
                if rent_multi == 1: rent_multi = 10
                player[_player]["$$$"] -= (self.dice_value[1] + self.dice_value[2]) * rent_multi
                player[_owner]["$$$"] += (self.dice_value[1] + self.dice_value[2]) * rent_multi
            else:
                if rent_multi == 1: rent_multi = 10
                player[_player]["$$$"] -= (self.dice_value[1] + self.dice_value[2]) * rent_multi
                player[_owner]["$$$"] += (self.dice_value[1] + self.dice_value[2]) * rent_multi

        elif property_data[_prop]["type"] == "station":

            # counts how many stations owned to determine rent
            num = 0
            for i in [2, 10, 17, 25]:
                if property_data[i]["owner"] == _owner: num += 1
            player[_player]["$$$"] -= station_rent[num] * rent_multi
            player[_owner]["$$$"] += station_rent[num] * rent_multi
                
        # properties with houses or hotels
        elif property_data[_prop]["upgrade state"] > 2:

            # eg: if upgrade_state = 3; key would be "h1"
            key = f"h{property_data[_prop]['upgrade state'] - 2}"
            player[_player]["$$$"] -= property_data[_prop][key] * rent_multi
            player[_owner]["$$$"] += property_data[_prop][key] * rent_multi

        # properties in a colour set
        elif property_data[_prop]["upgrade state"] == 2:
            player[_player]["$$$"] -= property_data[_prop]["rent"] * 2 * rent_multi
            player[_owner]["$$$"] += property_data[_prop]["rent"] * 2 * rent_multi

        elif property_data[_prop]["upgrade state"] == 1:
            player[_player]["$$$"] -= property_data[_prop]["rent"] * rent_multi
            player[_owner]["$$$"] += property_data[_prop]["rent"] * rent_multi

        if player[_player]["$$$"] < 0:
            player_is_broke(_player, _owner)

    def remove_from_jail(self, _player: int | None = player_turn):
        """moves player from jail to just visiting"""

        player[_player]["pos"] = 10
        player[_player]["jail time"] = 0
        player[_player]["status"] = "playing"

        # updates the board
        update_player_position(10)
        update_player_position(40, "remove")

        refresh_board()

    def send_to_jail(self, _player: int | None = player_turn):
        """sends given player to jail, doesn't refresh board"""
        player[player_turn]["last pos"] = player[player_turn]["pos"]
        player[player_turn]["pos"] = 40
        player[player_turn]["status"] = "jail"
        
        self.dice_rolled = True

        update_player_position(40)
        update_player_position(player[player_turn]["last pos"], "remove")

    def start_roll(self):
        """main entry to start dice roll animation"""
        global current_screen
        global player_turn
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
                    
                        if player[player_turn]["pos"] != 40: print(f"      {self.doubles_art[i]}")
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

        refresh_board.action = "dice_roll_accept"

    def move(self):
        """start player movement around board, performs movement logic"""

        # this is updating the player's last position, so that the player's icon can be removed from the board
        player[player_turn]["last pos"] = player[player_turn]["pos"]

        # increases the doubles streak the player has, or resets it to 0
        if self.dice_value[1] == self.dice_value[2]:
            self.doubles_count += 1
        else:
            self.doubles_count = 0

        # if player rolls 3 doubles in a row, they're sent to jail
        if self.doubles_count == 3:
            player_action.send_to_jail()
            refresh_board()
            return

        # determines player movement length
        self.player_roll_itr = iter(range(self.dice_value[1] + self.dice_value[2]))

        if player[player_turn]["status"] == "jail":
            if self.doubles_count == 0:
                player[player_turn]["jail time"] += 1

                # cancels the player movement
                self.dice_rolled = True
        
            # the player escapes jail if they roll doubles
            else:
                self.remove_from_jail(player_turn)
                
                # a player that escapes jail gets to go again
                self.doubles_count = 0
                self.dice_rolled = False
            
            refresh_board()
            return # stops movement and position change

        # this is adding the dice roll's value to the player's position
        player[player_turn]["pos"] = (player[player_turn]["pos"] + self.dice_value[1] + self.dice_value[2])

        # makes sure that the player's position is valid
        if player[player_turn]["pos"] >= 40:
            player[player_turn]["pos"] -= 40

        while True:
            try:
                # determines what space the player is added to
                space = next(self.player_roll_itr) + player[player_turn]["last pos"] - 39

            # once the iterator has ran out the player is at the 
            # correct spot and the board will stop being refreshed
            except StopIteration:

                # only happens once the player passes go and their position is reset
                # extra check if the player leaves jail to stop passed go text
                if player[player_turn]["pos"] < player[player_turn]["last pos"] and player[player_turn]["last pos"] != 40:
                    player[player_turn]["$$$"] += 200
                    refresh_board.passed_go = True

                player_action(player_turn)
                   
                self.dice_rolling_state = "off"
                if self.doubles_count in [0, 3]:
                    self.dice_rolled = True

                # board isn't displayed if chance/community chest displays message
                if not (refresh_board.action in ("chance notice", "community chest notice")): refresh_board()
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
                refresh_board()


player_action = player_action_class()


def run():
    """main entry point to start monopoly program"""
    homescreen()
    while True:
        try: globals()[current_screen].input_management(input())
        except KeyboardInterrupt: pass # stupid keyboard interrupts


async def get_input():
    """gets user input (nonblocking) and executes appropriate logic"""
    loop = asyncio.get_running_loop()

    while not online_config.stop_event.is_set():
        u_input = await loop.run_in_executor(None, input)
        globals()[current_screen].input_management(u_input)


async def get_data():
    """gets data sent from other players in an online game"""
    global player
    global player_turn
    global players_playing

    loop = asyncio.get_running_loop()

    if online_config.socket_type == "host":
        while not online_config.stop_event.is_set():
            for item in online_config.joined_clients:
                try:
                    online_input = await loop.run_in_executor(None, item[1].recv, 1024)
                    online_input = online_input.decode()
                except (UnicodeDecodeError, BlockingIOError):
                    continue
                
                except (ConnectionError, ConnectionAbortedError, ConnectionResetError, ConnectionRefusedError):

                    # host alerts other clients that this client has lost communication
                    for sub_item in online_config.joined_clients:
                        if sub_item != item:
                            sub_item[1].sendall(f"clientquit:{item[3]}".encode())
                    
                    globals()[current_screen].disconnect_management(item[3])

                except Exception as e:
                    input(f"{e=}")

                # ensures all clients except sender receive message
                for sub_item in online_config.joined_clients:
                    if sub_item != item:
                        sub_item[1].sendall(f"{online_input}:{item[2]}".encode())

                if online_input.startswith("clientquit"):
                    # host alerts other clients that this client has lost communication
                    for sub_item in online_config.joined_clients:
                        if sub_item != item:
                            sub_item[1].sendall(f"clientquit:{item[3]}".encode())

                    globals()[current_screen].disconnect_management(item[3])

                elif online_input.startswith("turnfinshed"):
                    refresh_board.end_turn_logic()
               

                elif online_input.startswith("turnfinished:"):
                    _, player_change, money_change, _ = online_input.split(":")
                    money_change = eval(money_change)
                
                    for i in range(players_playing):
                        player[i + 1]["$$$"] = money_change[i]
                
                    # ensures player is sent to jail across all devices
                    if player_change == 40:
                        player_action.send_to_jail()
                    else:
                        player[player_turn]["last pos"] = player[player_turn]["pos"]
                        player[player_turn]["pos"] = int(player_change)

                        update_player_position(player[player_turn]["pos"])
                        update_player_position(player[player_turn]["last pos"], "remove")

                    refresh_board.end_turn_logic()

                    if current_screen == refresh_board:
                        refresh_board()
                    elif online_config.player_num == player_turn and player_turn == online_config.player_num:
                        print("\n    === it's now your turn to roll ===\n\n    ", end="")
                elif online_input.startswith("ping"):
                    send_data("ack")

                    # position in clients list == position in ping list
                    online_config.ping_count[online_config.joined_clients.index(item)] = 0

                # resets timeout count to 0
                elif online_input.startswith("ack"):
                    online_config.ping_count[online_config.joined_clients.index(item)] = 0

                elif online_input.startswith("varupdate:"):
                    _, var, value = online_input.split(":")
                    globals()[var] = eval(value)

                elif online_input.startswith("carddrawn:"):
                    _, card = online_input.split(":")
                    if card == "cc": community_chest.draw_card()
                    else: chance.draw_card()
                elif online_input == '':
                    return
                else:
                    input(f"{online_input=}")
      
            # reduces computational strain
            await asyncio.sleep(1)

    elif online_config.socket_type == "client":
        while not online_config.stop_event.is_set():
            try:
                online_input = await loop.run_in_executor(None, online_config.socket.recv, 1024)
                online_input = online_input.decode()
                if online_config.stop_event.is_set():
                    return

            except (ConnectionAbortedError, ConnectionResetError, ConnectionError, ConnectionRefusedError):
                online_config.connection_lost()
                return

            # if user exits out, then message doesn't need to be shown
            except OSError:
                return

            # malformed messages are ignored
            except UnicodeDecodeError:
                continue

            # for debugging
            except Exception as e:
                input(f"{e=}")

            if online_input.startswith("booted"):
                online_config.kicked_notice()
                return

            elif online_input.startswith("users update:"):

                # this is not used for clients, so is re-purposed
                _, client_list = online_input.split(":")
                client_list = eval(client_list)

                online_config.joined_clients = client_list
                online_config.client_wait_screen()

            elif online_input.startswith("clientquit:"):
                _, quitter = online_input.split(":")

                if online_config.game_strt_event.is_set():
                    player[quitter]["status"] = "disconnected"

                globals()[current_screen].disconnect_management(quitter)

            elif online_input.startswith("hoststart"):
                player = {}
                players_playing = len(online_config.joined_clients[0])

                # creates the players using the characters provided
                for i in range(players_playing):
                    player[i + 1] = {
                    "char": online_config.joined_clients[1][i],
                    "$$$": 1500,
                    "pos": 0,
                    "last pos": 0,
                    "jail passes": 0,
                    "jail time": 0,
                    "house total": 0,
                    "hotel total": 0,
                    "total properties": 0,
                    "status": "playing",
                    "version": game_version
                }

                player_turn = better_iter(range(1, players_playing + 1), True)
                update_player_position(0)
                online_config.game_strt_event.set()
                display_game_notice()

            elif online_input.startswith("turnfinished:"):
                _, player_change, money_change, _ = online_input.split(":")
                money_change = eval(money_change)
                
                for i in range(players_playing):
                    player[i + 1]["$$$"] = money_change[i]
                
                # ensures player is sent to jail across all devices
                if player_change == 40:
                    player_action.send_to_jail()
                else:
                    player[player_turn]["last pos"] = player[player_turn]["pos"]
                    player[player_turn]["pos"] = int(player_change)

                    update_player_position(player[player_turn]["pos"])
                    update_player_position(player[player_turn]["last pos"], "remove")

                refresh_board.end_turn_logic()

                if current_screen == refresh_board:
                    refresh_board()
                elif online_config.player_num == player_turn and player_turn == online_config.player_num:
                    print("\n    === it's now your turn to roll ===\n\n    ", end="")
            
            elif online_input.startswith("varupdate:"):
                _, var, value = online_input.split(":")
                globals()[var] = eval(value)

            elif online_input.startswith("carddrawn:"):
                _, card = online_input.split(":")
                if card == "cc": community_chest.draw_card()
                else: chance.draw_card()

            elif online_input.startswith("ping"):
                send_data("ack")
                online_config.ping_count = 0

            # resets timeout count to 0
            elif online_input.startswith("ack"):
                    online_config.ping_count = 0  
            else:
                # I know this is blocking, but it should ensure
                # that logic errors are visible for debugging
                input(f"{online_input=}")
            
            await asyncio.sleep(1)


def send_data(data: str):
    """sends message to correct socket. appends ID to end of message"""
    if online_config.socket_type == "host":
        for item in online_config.joined_clients:
            item[1].sendall(f"{data}:{online_config.player_num}".encode())

    elif online_config.socket_type == "client":
        online_config.socket.sendall(f"{data}:{online_config.player_num}".encode())

# perhaps I should start all others with trailing 
# underscores so this is the only accessible function
if __name__ == "__main__":
    run()