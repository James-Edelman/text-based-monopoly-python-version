# importing required functions
from os import system, name
from random import randint, shuffle
from sys import exit
from time import time
from unicodedata import east_asian_width as width
from better_iterator import better_iter

# setting the terminal name
print("\033]1;💰 Text-Based Monopoly 💰\007")

# initialising variables
players_playing = 0
dev_mode = False
house_total = 32
hotel_total = 12
time_played = 0
game_version = 0.7
trade_query = False
passed_go = False

# the players' icons can only appear in certain points, so this list will have the default and modified art for the game board
# the default space is blank but there are some special cases that are specified individually
# (1st item = default art | 2nd item = modified art | 3rd item = standard/irregular display type...
# ...4th-7th items if players 1-4 are on the current space | total numbers of players on the space)
player_display_location = [["          ", "          ", "regular", False, False, False, False, 0] for i in range(41)]

player_display_location[7] = ["    ()    ", "    ()    ", "irregular", False, False, False, False, 0]
player_display_location[22] = ["    / /   ", "    / /   ", "irregular", False, False, False, False, 0]
player_display_location[36] = ["  \\_|    ", "  \\_|    ", "irregular", False, False, False, False, 0]
player_display_location[40] = [" ║ ║ ║ ║ ", " ║ ║ ║ ║ ", "irregular", False, False, False, False, 0]

passed_go_art = [
    r"✨    \¯\/¯/ /¯¯\  |¯||¯|    |¯¯¯\  /¯\   /¯⁐⁐| /¯⁐⁐| |¯¯¯| |¯¯¯\      /¯¯¯|   /¯¯\    ✨  ",
    r"   ✨  \  / | () | | || |    | ⁐_/ / ^ \  \__ \ \__ \ | ⁐|_ | [) |    | (⁐¯¯| | () | ✨     ",
    r" ✨    /_/   \__/   \__/     |_|  /_/¯\_\ |___/ |___/ |___| |___/      \___/   \__/      ✨",
]

player_turn_display = [[] for i in range(5)]

# art displaying the current turn
player_turn_display[1] = [" ___    ", "/__ |   ", " _| |_  ", "|_____| "]
player_turn_display[2] = [" _----_ ", "/__/  / ", " /  /___", "|______|"]
player_turn_display[3] = [" ______ ", "|____  \\", " |___ ⟨⁐", "|______/"]
player_turn_display[4] = ["__  __  ", "| || |_ ", "|___  _|", "   |_|  "]

property_data = [{} for i in range(28)]

# (note: colour set rent is double normal rent, isn't recorded. 
#  mortgage/unmortgage value based on street value; isn't recorded)
# upgrades: 0 = unpurchased, -1 = mortgaged, 1 = purchased, 2 = colour set, 3 - 8 = upgrades
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


def floor(_num: float):
    """returns closest lower integer to given float"""    
    try: val, rem = str(_num).split(".")
    except: return int(_num)
    else: return int(val)


def ceil(_num: float):
    """returns closest higher integer to given float"""
    try: val, rem = str(_num).split(".")
    except: return int(_num)
    if int(rem) != 0: return int(val) + 1
    else: return int(val)


def clear_screen(sys: str | None = name):
    if dev_mode == False:
        if   name == "nt"   : system("cls")
        elif name == "posix": system("clear")
        else: raise Exception("bro what are you running this on??!!")


# I'm very proud of this use of typing hints
def create_button_prompts(prompts: list[str], prompt_state: list[bool] | None =  "default", spacing: list[int] | None = "default"):
    """
    creates a list of ascii art that displays button-looking prompts.
    words should be a maximum of 12 characters long per button.

    prompt_state defaults to True, but buttons can be greyed out with False
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

    # if "prompt_state" or "spacing" is left to default, its size is dependant on the amount of prompts
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

        # this adds an extra space to each side for every two charactrs the prompt is from the maxium, rounded down
        for ii in range(floor((12 - len(prompts[i]))/ 2)): extra_space[0] += " "

        # if an additional space is needed (instead of an extra 1 on each side) it is added to the right
        if len(prompts[i]) % 2 == 1:
            extra_space[1] = " "

        for ii in range(spacing[i]): button_list[2] += " "
        try   : x = prompts[i][0].upper()
        except: 
            try   : x = prompts[i][0]
            except: pass

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
    global player_display_location

    # this is updating the display location by marking that a player is there, and the player's number (1, 2, 3, 4)
    if _action == "add":
        if dev_mode == True:
            print("-----------------------")
            print(f"this space will be modified: {player_display_location[_pos]} ║ pos = {_pos}")
        player_display_location[_pos][player_turn + 2] = True
        player_display_location[_pos][7] += 1
        if dev_mode == True:
            print(f"this space is modified to: {player_display_location[_pos]} ║ pos = {_pos}")
            print("-----------------------")

    elif _action == "remove":

        if dev_mode == True:
            print("-----------------------")
            print(f"the previous space was modified from: {player_display_location[_pos]} ║ pos {_pos}")

        # since if the player is going to jail they don't go on all the spaces on the way, this code is skipped
        if player[player_turn]["pos"] != 40:

            player_display_location[_pos][7] -= 1
            player_display_location[_pos][player_turn + 2] = False

        else:
            player_display_location[player[player_turn]["last pos"]][7] -= 1
            player_display_location[player[player_turn]["last pos"]][player_turn + 2] = False

        if dev_mode == True:
            print(f"the previous space was modified to: {player_display_location[_pos]} ║ pos {_pos}")
            print("-----------------------")

    player_itr = iter(player)

    # this works by adding the surrounding spaces, and when receives a 'p' it adds the next player currently at the space
    # it is dependent on the order not to overuse "next(player_itr)"
    def update_displayed_art(order):
        global player_display_location
        
        string = ""
        x = 0

        for char in order:
            if char != "p":
                string += char
            else:
                x = next(player_itr)
                while player_display_location[_pos][x + 2] != True:
                    x = next(player_itr)
                string += player[x]["char"]
        
        player_display_location[_pos][1] = string
                

    if player_display_location[_pos][7] == 0:
        player_display_location[_pos][1] = player_display_location[_pos][0]

    #################### REGULAR SPACES ####################

    # this is updating the displayed art with the player's icon
    # all the regulars can be done in the same way so I'll start with specifying them first
    elif player_display_location[_pos][2] == "regular":

        # (layout for reference: |    💎    |)
        if player_display_location[_pos][7] == 1:
            update_displayed_art("    p    ")

        # (layout for reference: |  💎  💎  |)
        elif player_display_location[_pos][7] == 2:
            update_displayed_art("  p  p  ")

        # (layout for reference: | 💎 💎 💎 |)
        elif player_display_location[_pos][7] == 3:
            update_displayed_art(" p p p ")

        # (layout for reference: |💎 💎💎 💎|)
        elif player_display_location[_pos][7] == 4:
            update_displayed_art("p pp p")

    #################### IRREGULAR SPACES ####################

    elif player_display_location[_pos][2] == "irregular":

        ########## |    ()    | [chance @ space 7] ##########
        if _pos == 7:

            # (layout for reference: | 💎 ()    |)
            if player_display_location[_pos][7] == 1:
                update_displayed_art(" p ()    ")

            # (layout for reference: | 💎 () 💎 |)
            elif player_display_location[_pos][7] == 2:
                update_displayed_art(" p () p ")

            # (layout for reference: |💎💎() 💎 |)
            elif player_display_location[_pos][7] == 3:
                update_displayed_art("pp() p ")

            # (layout for reference: |💎💎()💎💎|)
            elif player_display_location[_pos][7] == 4:
                update_displayed_art("pp()pp")

        ########## |    / /   | [chance @ space 22] ##########

        if _pos == 22:

            # (layout for reference: | 💎 / /   |)
            if player_display_location[_pos][7] == 1:
                update_displayed_art(" p / /   ")

            # (layout for reference: | 💎 / /💎 |)
            elif player_display_location[_pos][7] == 2:
                update_displayed_art(" p / /p ")

            # (layout for reference: |💎💎/ /💎 |)
            elif player_display_location[_pos][7] == 3:
                update_displayed_art("pp/ /p ")

            # (layout for reference: |💎💎/ 💎💎|)
            elif player_display_location[_pos][7] == 4:
                update_displayed_art("pp/ pp")

        ########## |  \_|    | [chance @ space 36]

        if _pos == 36:

            # (layout for reference : |  \_| 💎 |)
            if player_display_location[_pos][7] == 1:
                update_displayed_art(r" \_| p p")

            # (layout for reference : |💎\_| 💎 |)
            elif player_display_location[_pos][7] == 2:
                update_displayed_art(r"p\_| p ")

            # (layout for reference : |💎\_|💎💎|)
            elif player_display_location[_pos][7] == 3:
                update_displayed_art(r"p\_|pp")
                
            # (layout for reference : |💎💎💎|💎|)
            elif player_display_location[_pos][7] == 4:
                update_displayed_art("ppp|p")

        ########## | ║ ║ ║ ║ | [jail @ space 40 (in just visiting)] ##########
        if _pos == 40:
            player_display_location[_pos][1] = ""

            # (layout for reference: | ║ 💎║ ║ |)
            if player_display_location[_pos][7] == 1:
               update_displayed_art(" ║ p║ ║ ")

            # (layout for reference: | 💎║ ║💎 |)
            elif player_display_location[_pos][7] == 2:
                update_displayed_art(" p║ ║p |")

            # (layout for reference: | 💎💎║💎 |)
            elif player_display_location[_pos][7] == 3:
                update_displayed_art(" pp║p ")

            # (layout for reference: |💎💎 💎💎|)
            elif player_display_location[_pos][7] == 4:
                update_displayed_art("pp pp")

    if dev_mode == True:
        print(f"{player_display_location[_pos]}  ║  the function was: {_action}. the current player was: {player[player_turn]['char']}")


def player_is_broke(_player: int):
    """alerts the player that they are in debt/ are bankrupt"""
    global current_screen
    
    clear_screen()

    player_has_properties = False

    # checks if the player could afford to pay off their debts,
    # if not, the prompt to declare bankruptcy appears.
    # even if that happens, the player is still shown their properties,
    # to attempt to trade their way out of bankruptcy
    available_funds = 0
    for i in range(28):
        if property_data[i]["owner"] == _player:
            if property_data[i]["upgrade state"] >= 1:
                available_funds += (property_data[i]["street value"] / 2)
                if property_data[i]["upgrade state"] > 2:
                    number_of_upgrades = property_data[i]["upgrade state"] - 2
                    available_funds += number_of_upgrades * (property_data[i]["house cost"] / 2)

            player_has_properties = True

    if player_has_properties == True:

        global entered_number
        global conversion_dictionary
        global current_screen

        entered_number = False

        # this makes sure that the text is centered by adding extra space if the debt is a different length than 4 digits
        extra_space = ""
        for i in range(5 - len(str(abs(player[_player]["$$$"])))): extra_space += " "

        print()
        print("    ╔════════════════════════════════════════════════════════════════╗")
        print("    ║                                                                ║")
        print("    ║                             NOTICE:                            ║")
        print("    ║                                                                ║")
        print(f"    ║{extra_space}       Player {player_turn}, You are ${abs(player[_player]["$$$"])} in debt! raise ${abs(player[_player]["$$$"])} by:       {extra_space}║")
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

        display_property_list(_player, clear = False)
 
    # if the player has no properties, they immediately get eliminated
    else:
        print()
        print("    ╔════════════════════════════════════════════════════════════════╗")
        print("    ║                                                                ║")
        print("    ║                      PLAYER ELIMINATED :(                      ║")
        print("    ║                                                                ║")
        print("    ║                  you cannot repay your debts,                  ║")
        print("    ║            so you are bankrupt and out of the game.            ║")
        print("    ║                                                                ║")
        print("    ║    Now's a great opportunity to go outside and touch grass!    ║")
        print("    ║                                                                ║")
        print("    ║                             [enter]                            ║")
        print("    ╚════════════════════════════════════════════════════════════════╝")
        
        # updates the player's status to "bankrupt" and removes them from play
        player[_player]["status"] = "bankrupt"
        current_screen = "bankruptcy"


class display_property_list_class():
    def __init__(self): self.player = None; self.allow_bankruptcy = False
        
    def __call__(self, _player, clear = True, allow_bankruptcy = False):

        self.player = _player
        self.allow_bankruptcy = allow_bankruptcy

        global conversion_dictionary
        global current_screen

        if clear == True: clear_screen()

        current_screen = "property_list"
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
            if property_data[i]["owner"] == _player and property_data[i]["type"] == "property":
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
                    print(f" │ ${property_data[i]['house cost']}", end = "")
                    if property_data[i]["house cost"] < 100: print(" ", end = "")
                    
                    print(" × ", end = "")
                    if property_data[i]["upgrade state"] == 7:   print("🏠🏠🏠🏠 🏨     ║")

                    else:

                        # prints the number of houses on the property
                        x = ""
                        for ii in range(property_data[i]["upgrade state"] - 2): x += "🏠"

                        print(f"{x}", end = "")
                        for ii in range(15 - (2 * len(x))): print(" ", end = "")
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

            # checks that the player doesn't have negative cash, and that no other players have negative cash
            if player[player_turn]["$$$"] < 0:
                print("\n    === you must clear your debts before returning to the game ===\n\n    ", end = "")
            else:
                lock = False
                for i in range(players_playing):
                    if player[i + 1]["$$$"] < 0:
                        player_is_broke(i + 1)
                        lock = True
                        break
                if lock == False: refresh_board()

        elif user_input in ["t", "T"]:
            if trade_screen.is_trade == True:
                trade_screen.display_trade_window()
            else:
                trade_screen(player_turn)

        if user_input in ["g", "G"] and self.allow_bankruptcy == True:
            bankruptcy(self.player, "bank") # Note to self: fix
        else:
            try:
                int(user_input)                
            except:
                print("\n    === command not recognised ===\n\n    ", end = "")
            else:
                if int(user_input) in conversion_dictionary:
                   display_property(conversion_dictionary[int(user_input)])
                else:
                    print("\n    === command not recognised ===\n\n    ", end = "")


display_property_list = display_property_list_class()


class display_property_class(): 
    def __init__(self): 
        self.property = None
        self.skipped_bids = 0
        self.bid_number = 0
        self.player_bids = {1: 0, 2: 0, 3: 0, 4: 0}
        self.printed_bids = 0
        self.bid_order = []
        self.action = None
        self.action_2 = None
        self.true_player_turn = None
        self.notice = better_iter(["      ╔════════════════════════════════════════════════════════════════╗",
                                   "      ║                                                                ║",
                                   "      ║                             NOTICE:                            ║",
                                   "      ║                                                                ║",
                                   "      ║   you can bid more than your current cash, and go into debt.   ║",
                                   "      ║  however, at the end you will still have to find enough money  ║",
                                   "      ║                                                                ║",
                                   "      ╚════════════════════════════════════════════════════════════════╝"])
        self.bid = better_iter(["      ╔═════════════════════╗",

                                # not a function string as bids() in call() properly assembles the output
                                "      ║ Player @@@ bid: $### &&&║",
                                "      ╚═════════════════════╝"], True)

    def __call__(self, _prop_num: int):
        self.property = _prop_num
        global current_screen

        # resets the iterators each time, as a precaution
        self.notice.index = -1
        self.bid.index = -1

        extra_space = ["", "", "", ""]
        current_screen = "property"
        clear_screen()
        print()
        
        def bidding_notice():
            if self.action in ["auction", "finished"]: return next(self.notice)
            else: return ""

        def display_bids():
            """displays the players bids alongside the property"""
           
            output = ""

            # ensures that only when there are bids yet to be displayed is the code called
            if self.action in ["auction", "finished"] and self.printed_bids < self.bid_number:
                
                output = next(self.bid)
                
                # these symbols are only in the middle line, which need to be replaced with actual information
                if "@" in output:

                    # makes sure that there is the correct amount of spaces
                    extra_space = ""
                    for i in range(4 - len(str(self.player_bids[self.bid_order[self.printed_bids]]))): extra_space += " "

                    output = output.replace("@@@", str(self.bid_order[self.printed_bids]))
                    output = output.replace("###", str(self.player_bids[self.bid_order[self.printed_bids]]))
                    output = output.replace("&&&", extra_space)

                    # if this is the first bid displayed, they in will be the highest
                    if self.printed_bids == 0: output += " ✨ TOP BID ✨"

                if output == "      ╚═════════════════════╝": self.printed_bids += 1

            return output

        if property_data[_prop_num]["upgrade state"] == -1:

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
                if   line == 1 : output = f"{extra_space[0]}{extra_space[1]} {property_data[self.property]["name"].upper()}{extra_space[0]}  "
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

            m_val = int(property_data[_prop_num]["street value"] / 2)
            if len(str(m_val)) == 2           : extra_space[2] = " "
            if len(str(int(m_val * 1.1))) == 2: extra_space[3] = " "

            for i in range(floor((21 - len(property_data[_prop_num]["name"])) /2)): extra_space[0] += " "
            if len(property_data[_prop_num]["name"]) % 2 == 0: extra_space[1] = " "

            # do not be afraid
            print(f"    \x1b[38;2;255;255;255m▗▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▖\x1b[0m{bidding_notice()}")
            print(f"    \x1b[38;2;12;12;12m\x1b[48;2;255;255;255m▌  \x1b[38;2;255;95;59m▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃  \x1b[0m\x1b[38;2;255;255;255m▌\x1b[0m{bidding_notice()}")
            
            for i in range(21):
                print(f"    \x1b[38;2;12;12;12m\x1b[48;2;255;255;255m▌  {gradient(i, True, 3)}{gradient(i)}▊\x1b[38;2;255;255;255m{extra_text(i)}{gradient(i, False, 3)}{gradient(i, True)}▎\x1b[48;2;255;255;255m  \x1b[0m\x1b[38;2;255;255;255m▌\x1b[0m{side_info(i)}")

            print("    \x1b[38;2;12;12;12m\x1b[48;2;255;255;255m▌\x1b[0m\x1b[48;2;255;255;255m  \x1b[48;2;255;67;23m\x1b[38;2;255;255;255m▅▅▅▅▅▅▅▅▅▅▅▅▅▅▅▅▅▅▅▅▅▅▅▅▅▅\x1b[0m\x1b[48;2;255;255;255m  \x1b[0m\x1b[38;2;255;255;255m▌\x1b[0m")
            print("    \x1b[38;2;255;255;255m▝\x1b[38;2;12;12;12m\x1b[48;2;255;255;255m▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄\x1b[0m\x1b[38;2;255;255;255m▘\x1b[0m")

        # station cards
        elif _prop_num in [2, 10, 17, 25]:

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
            for ii in range(floor((21 - len(property_data[_prop_num]["name"])) /2)): extra_space[0] += " "
            
            # since the upper code can only add two spaces, if the difference
            # between the maximum length and actual length is odd (so the value is even)...
            # ...an extra space is added to the left of the name to center it properly
            if len(property_data[_prop_num]["name"]) % 2 == 0: extra_space[1] = " "

            print(f"    │                              │{display_bids()}")
            print(f"    │{extra_space[0]}{extra_space[1]}    {property_data[_prop_num]['name']}     {extra_space[0]}│{display_bids()}")
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
        elif _prop_num == 7:

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
        elif _prop_num == 20:
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
            
            print(f"    ┌──────────────────────────────┐{bidding_notice()}")

            # this checks what colour set the property is in and adjusts the colour of the printed title deed
            if property_data[_prop_num]["colour set"] == 0:
                colour = "🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫" # brown

            # light blue (set 1) and dark blue (set 7) use the same colour
            elif property_data[_prop_num]["colour set"] in [1, 7]:
                colour = "🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦"
        
            elif property_data[_prop_num]["colour set"] == 2:
                colour = "🟪🟪🟪🟪🟪🟪🟪🟪🟪🟪🟪🟪🟪🟪" # purple (there's no pink square emoji)

            elif property_data[_prop_num]["colour set"] == 3:
                colour = "🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧" # orange

            elif property_data[_prop_num]["colour set"] == 4:
                colour = "🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥" # red

            elif property_data[_prop_num]["colour set"] == 5:
                colour = "🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨" # yellow

            else:
                colour = "🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩" # green

            for i in range(4): print(f"    │ {colour} │{bidding_notice()}")

            print(f"    │                              │{bidding_notice()}")

            # see the same code for the stations
            extra_space[0] = ""
            for ii in range(floor((21 - len(property_data[_prop_num]["name"])) /2)): extra_space[0] += " "

            extra_space[1] = ""
            if len(property_data[_prop_num]["name"]) % 2 == 0: extra_space[1] = " "

            print(f"    │{extra_space[0]}{extra_space[1]}    {property_data[_prop_num]['name']}     {extra_space[0]}│{bidding_notice()}")
            print(f"    │                              │{bidding_notice()}")

            # these just add an extra 1-2 spaces if depending on the length, for rent, colour set rent and all the other stats
            extra_space[0] = ""
            for ii in range(2 - len(str(property_data[_prop_num]["rent"]))): extra_space[0] += " "

            print(f"    │ Rent                   ${property_data[_prop_num]['rent']}{extra_space[0]}   │")


            extra_space[0] = ""
            for ii in range(3 - len(str(property_data[_prop_num]["rent"] * 2))): extra_space[0] += " "

            extra_space[1] = ""
            for ii in range(3 - len(str(property_data[_prop_num]["h1 rent"]))): extra_space[1] += " "

            print(f"    │ Rent with colour set   ${(property_data[_prop_num]['rent'] * 2)}{extra_space[0]}  │{display_bids()}")
            print(f"    │                              │{display_bids()}")
            print(f"    │ Rent with 🏠           ${property_data[_prop_num]['h1 rent']}{extra_space[1]}  │{display_bids()}")

            extra_space[0] = ""
            for ii in range(3 - len(str(property_data[_prop_num]["h2 rent"]))): extra_space[0] += " "

            extra_space[1] = ""
            for ii in range(4 - len(str(property_data[_prop_num]["h3 rent"]))): extra_space[1] += " "

            extra_space[2] = ""
            for ii in range(4 - len(str(property_data[_prop_num]["h4 rent"]))): extra_space[2] += " "

            print(f"    │ Rent with 🏠🏠         ${property_data[_prop_num]['h2 rent']}{extra_space[0]}  │{display_bids()}")
            print(f"    │ Rent with 🏠🏠🏠       ${property_data[_prop_num]['h3 rent']}{extra_space[1]} │{display_bids()}")
            print(f"    │ Rent with 🏠🏠🏠🏠     ${property_data[_prop_num]['h4 rent']}{extra_space[2]} │{display_bids()}")

            extra_space[0] = ""
            for ii in range(4 - len(str(property_data[_prop_num]["h5 rent"]))): extra_space[0] += " "

            print(f"    │                              │{display_bids()}")
            print(f"    │ Rent with 🏠🏠🏠🏠 🏨  ${property_data[_prop_num]['h5 rent']}{extra_space[0]} │{display_bids()}")
            print(f"    │                              │{display_bids()}")

            extra_space[0] = ""
            for ii in range(4 - len(str(property_data[_prop_num]["house cost"]))): extra_space[0] += " "

            print(f"    │ ---------------------------- │{display_bids()}")        
            print(f"    │ House/hotel cost       ${property_data[_prop_num]['house cost']}{extra_space[0]} │{display_bids()}")
            print(f"    │                              │{display_bids()}")

            extra_space[0] = ""
            for ii in range(4 - len(str(property_data[_prop_num]["street value"]))): extra_space[0] += " "

            print(f"    │ Street value           ${property_data[_prop_num]['street value']}{extra_space[0]} │")

            extra_space[0] = ""
            for ii in range(3 - len(str(int(property_data[_prop_num]["street value"] / 2)))): extra_space[0] += " "   
        
            if property_data[_prop_num]["upgrade state"] != -1:
                print(f"    │ mortgage value         ${int(property_data[_prop_num]['street value'] / 2)}{extra_space[0]}  │")
            else:
                print(f"    │ unmortgage value       ${int((property_data[_prop_num]['street value'] / 2) * 1.1)}{extra_space[0]}  │")

            print("    └──────────────────────────────┘")

        if self.action == "auction" and self.player_bids[player_turn] == 0:
            if self.action_2 == "final chance":
                print(f"\n    === player {player_turn}, now's your final chance to place a bid, or [S]kip ===\n\n    ", end = "")
            else:
                print(f"\n    === player {player_turn}, place a bid or [S]kip ===\n\n    ", end = "")

        elif self.action == "auction":
            if self.action_2 == "final chance":
                print(f"\n    === player {player_turn}, now's your final chance to raise your bid, or [S]kip ===\n\n    ", end = "")
            else:
                print(f"\n    === player {player_turn}, either raise your bid or [S]kip ===\n\n    ", end = "")

        elif self.action == "finished":
            print(f"\n    === player {self.highest_bidder} has won the bid, press [Enter] to continue ===\n\n    ", end = "")

        else:
            print()
            actions = [[], [], [4]]

            # if the property has no upgrades, can be mortgaged
            if property_data[_prop_num]["upgrade state"] in [0, 1, 2]:
                actions[0].append("Mortgage")
                actions[1].append(True)

            # if the property has upgrades, cannot be mortgaged
            elif property_data[_prop_num]["upgrade state"] > 2:
                actions[0].append("Mortgage")
                actions[1].append(False)

            # if the property is mortgaged, checks if the player can affoard to unmortgage
            elif property_data[_prop_num]["upgrade state"] == -1:
                actions[0].append("Unmortgage")
                if player[property_data[_prop_num]["owner"]]["$$$"] > round((property_data[_prop_num]["street value"] / 2) * 1.1): actions[1].append(True)
                else                                                                                                             : actions[1].append(False)
            
            if property_data[_prop_num]["type"] == "property":
                actions[0].append("Add houses")
                actions[0].append("Sell houses")
                actions[2].append(3)
                actions[2].append(3)
                if 2 <= property_data[_prop_num]["upgrade state"] < 7 and player[property_data[_prop_num]["owner"]]["$$$"] >= property_data[_prop_num]["house cost"]: actions[1].append(True)
                else                                                                                                                                                : actions[1].append(False)
                
                if property_data[_prop_num]["upgrade state"] > 2: actions[1].append(True)
                else                                            : actions[1].append(False)

            actions[2].append(3)
            # if the player is trading, and wants to remove a property
            if trade_screen.is_trade == True and _prop_num in (trade_screen.player_1["props"] or trade_screen.player_2["props"]):
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
        """determines what action to perform with user input"""

        def exit_bid(self):
            """resets bid variables, corrects player turn, and clears current_action"""

            self.action = None
            self.action_2 = None
            self.bid_number = 0
            self.skipped_bids = 0
            self.printed_bids = 0
            self.player_bids = {1: 0, 2: 0, 3: 0, 4: 0}
            player_turn.index = self.true_player_turn

            global current_action
            current_action = None

            refresh_board()

        if self.action == "auction":
            try:
                int(user_input)
            except:
                if user_input in ["s", "S"]:
                    self.skipped_bids += 1
                                        
                    if self.skipped_bids == players_playing - 1 and self.bid_number > 0:
                        self.action = "finished"

                        self.player_bids = dict(sorted(self.player_bids.items(), key=lambda item: item[1], reverse=True))

                        # more help from GitHub Copilot. (apparently, I had to convert the 
                        # keys into a list first,to reference the first object - highest bid)
                        self.highest_bidder = list(self.player_bids.keys())[0]
                        self.printed_bids = 0

                        player[self.highest_bidder]["$$$"] -= self.player_bids[self.highest_bidder]
                        property_data[self.property]["owner"] = self.highest_bidder
                                                
                        display_property(self.property)
                        self.action = "prop notice"

                    # provides a chance if players change their minds
                    elif self.skipped_bids == players_playing:
                        self.action_2 = "final chance"
                        next(player_turn)
                        display_property(self.property)

                    elif self.skipped_bids == players_playing * 2:
                        exit_bid(self)
                        refresh_board()
                    else:
                        next(player_turn)
                        display_property(self.property)

                else:
                    print("\n    === command not recognised. Please enter a number or [S]kip ===\n\n    ", end = "")
            else:

                # checks that the player has entered an higher bid
                valid_bid = True
                for bid in self.player_bids.values():
                    if int(user_input) <= bid: valid_bid = False

                if valid_bid == True:
                    self.player_bids[player_turn] = int(user_input)
                    next(player_turn)
                    self.bid_number += 1
                    if self.bid_number > players_playing: self.bid_number = players_playing
                    self.skipped_bids = 0
                    self.printed_bids = 0

                    # Sorts the dictionary based on values (created with GitHub Copilot)
                    self.player_bids = dict(sorted(self.player_bids.items(), key = lambda item: item[1], reverse = True))

                    # creates a list of the order of bids, so i can refer to the dictionary sequentially
                    self.bid_order = []
                    for i in self.player_bids.keys():
                        self.bid_order.append(i)

                    display_property(self.property)
                else:
                    print(f"\n    === player {player_turn} either raise your bid or [S]kip ===\n\n    ", end = "")

        elif self.action == "prop notice":
            broke_alert = False
            exit_bid(self)
            for i in range(players_playing):
                if player[i + 1]["$$$"] < 0:
                    player_is_broke(i + 1)
                    broke_alert = True
                    break

            if broke_alert == False: refresh_board()

        else:
            if user_input in ["b", "B"]:
                display_property_list(player_turn)
  
            elif user_input in ["t", "T"]:
                if trade_screen.is_trade == True:
                    trade_screen.add_prop_offer(display_property.property)
                else:
                    trade_screen(player_turn)
            
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
                if property_data[self.property]["upgrade state"] == -1:
                    cost = (property_data[self.property]["street value"] / 2) * 1.1
                    
                    # unmortgages the property if the player can affoard it
                    if player[player_turn]["$$$"] >= cost:
                        player[player_turn]["$$$"] -= cost
                        property_data[self.property]["upgrade state"] = 1
                        self(self.property)
                    else:
                        print("\n    === you cannot afford to unmortgage this property ===\n\n    ", end="")
                else:
                    print("\n    === property not mortgaged ===\n\n    ", end = "")

            elif user_input in ["a", "A"] and property_data[self.property]["type"] == "property":
                if 2 <= property_data[self.property]["upgrade state"] < 7:
                    if player[property_data[self.property]["owner"]]["$$$"] >= property_data[self.property]["house cost"]:
                        player[property_data[self.property]["owner"]]["$$$"] -= property_data[self.property]["house cost"]
                        property_data[self.property]["upgrade state"] += 1
                        self(self.property)
                    else:
                        print("\n    === you cannot afford to buy an upgrade ===\n\n    ", end = "")
                else:
                    print("\n    === you cannot upgrade this property ===\n\n    ", end = "")


display_property = display_property_class()


class chance_cards_class():
    """contains all actions related to chance card management"""

    def __init__(self):

        # note: the numbers at the start are for saving the arrangement of the shuffled cards
        self.cards = [
                      "0 Advance to go (collect $200)",
                      "1 Advance to Trafalgar Square. If you pass go, collect $200",
                      "2 Advance to Pall Mall. If you pass go, collect $200",
                      "3 Advance to the nearest utility. If unowned, you may buy it from the bank. If owned, throw the dice and pay owner 10x dice roll",
                      "4 Advance to the nearest station. If unowned, you may buy it from the bank. If owned, pay owner twice the rental to which they are otherwise entitled",
                      "4 Advance to the nearest station. If unowned, you may buy it from the bank. If owned, pay owner twice the rental to which they are otherwise entitled",
                      "5 Bank pays you dividend of $50",
                      "6 Get out of jail free. This card may be kept until needed or traded",
                      "7 Go back three spaces",
                      "8 Go directly to jail. Do not pass go, do not collect $200",
                      "9 Make general repairs on all your property: For each house pay $25, for each hotel pay 100",
                      "10Take a trip to Kings Cross Station. If you pass go, collect $200.",
                      "11Advance to Mayfair",
                      "12You have been elected chairman of the board. Pay each player $50",
                      "13Your building loan matures. Collect $150",
                      "14Speeding fine $15",
        ]
        self.art = [
                    r"✨     /¯¯¯| |¯| |¯|   /¯\   |¯¯\|¯|  /¯¯¯| |¯¯¯|   ✨  ",
                    r"   ✨ | (⁐⁐  | ¯¯¯ |  / ^ \  | \ \ | | (⁐⁐  | ⁐|_ ✨    ",
                    r" ✨    \___| |_|¯|_| /_/¯\_\ |_|\__|  \___| |___|     ✨",
]
        shuffle(self.cards)

        self.cards_value = []
        self.cards_message = []

        for i in self.cards: self.cards_value.append(i[:2])
        for i in self.cards: self.cards_message.append(i[2:])
        self.index = -1

    def __str__(self):
        return self.cards_message[self.index]

    def draw_card(self):
        """returns the next shuffled card message"""

        # this draws the next chance card, if exceeded resets to zero
        self.index += 1
        try:
            return self.cards_message[self.index]
        except:
            self.index = 0
            return self.cards_message[self.index]

    def perform_action(self):
        """
        performs action based on draw_card(). 
        Can be done multiple times per card but requires at least one draw_card()
        """

        global doubles_rolled
        global player
        global passed_go

        drawn_card = int(self.cards_value[self.index])

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
                passed_go = True

            player_action.rent_mgmt(player_turn, 2)
            update_player_position(player[player_turn]["pos"])
            update_player_position(player[player_turn]["last pos"], "remove")

        elif drawn_card == 5:
            player[player_turn]["$$$"] += 50

        elif drawn_card == 6:
            player[player_turn]["has jail pass"] += 1

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
            doubles_rolled = 0
            update_player_position(player[player_turn]["pos"])
            update_player_position(player[player_turn]["last pos"], "remove")

        elif drawn_card == 9:
            player[player_turn]["$$$"] -= ((player[player_turn]["house total"] * 25) + (player[player_turn]["hotel total"] * 100))
            if player[player_turn]["$$$"] < 0:
                player_is_broke(player_turn, abs(player[player_turn]["$$$"]))

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
                player_is_broke(player_turn, abs(player[player_turn]["$$$"]))

        elif drawn_card == 13:
            player[player_turn]["$$$"] += 150

        elif drawn_card == 14:
            player[player_turn]["$$$"] -= 15
            if player[player_turn]["$$$"] < 0:
                player_is_broke(player_turn, abs(player[player_turn]["$$$"]))

        refresh_board()


chance = chance_cards_class()


class community_chest_cards_class():
    """contains all actions related to community chest card management"""

    def __init__(self):
        self.cards = [
                     "0 Advance to go (collect $200)",
                     "1 Bank error in your favour. Collect $200",
                     "2 Doctor's fees. Pay $50",
                     "3 From sale of stock you get $50",
                     "4 Get out of jail free. This card may be kept until needed or traded",
                     "5 Go directly to jail. Do not pass go, do not collect $200",
                     "6 Holiday fund matures. Collect $100",
                     "7 Income tax refund. Collect $20",
                     "8 It's your birthday. Collect $10 from every player",
                     "9 Life insurance matures. Collect $100",
                     "10Hospital fees. Pay $100",
                     "11You have won second prise in a beauty contest. Collect $10",
                     "12You are assessed for street repairs: Pay $40 per house and $115 per hotel you own",
                     "13School fees. Pay $50",
                     "14Receive $25 consultancy fee.",
                     "15You inherit $100",
]

        self.art = [
                    r"✨     /¯¯¯|  /¯¯\  |¯¯\/¯¯| |¯¯\/¯¯| |¯||¯| |¯¯\|¯| |¯¯¯| |¯¯¯¯¯| \¯\/¯/    /¯¯¯| |¯| |¯| |¯¯¯| /¯⁐⁐| |¯¯¯¯¯|   ✨  ",
                    r"   ✨ | (⁐⁐  | () | | \  / | | \  / | | || | | \ \ | ⁐| |⁐  ¯| |¯   \  /    | (⁐⁐  | ¯¯¯ | | ⁐|_ \__ \  ¯| |¯  ✨    ",
                    r" ✨    \___|  \__/  |_|\/|_| |_|\/|_|  \__/  |_|\__| |___|   |_|    /_/      \___| |_|¯|_| |___| |___/   |_|       ✨",
]
        shuffle(self.cards)

        self.cards_value = []
        self.cards_message = []

        for i in self.cards: self.cards_value.append(i[:2])
        for i in self.cards: self.cards_message.append(i[2:])
        self.index = 0

    def __str__(self):
        return self.cards_message[self.index]

    def draw_card(self):
        """returns the next shuffled card message"""

        # this draws the next chance card, if exceeded resets to zero
        self.index += 1
        try:
            return self.cards_message[self.index]
        except:
            self.index = 0
            return self.cards_message[self.index]

    def perform_action(self):
        """
        performs action based on draw_card(). 
        Can be done multiple times per card but requires at least one draw_card() 
        """

        global doubles_rolled
        global player

        drawn_card = int(self.cards_value[self.index])

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
                player_is_broke(player_turn, abs(player[player_turn]["$$$"]))

        elif drawn_card == 3:
            player[player_turn]["$$$"] += 50

        elif drawn_card == 4:
            player[player_turn]["has jail pass"] += 1

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
            for i in range(players_playing):
                if i + 1 != player_turn:
                    player[i + 1]["$$$"] -= 10
                    if player[i + 1]["$$$"] < 0:
                        player_is_broke(i + 1, abs(player[i + 1]["$$$"]))

        elif drawn_card == 9:
            player[player_turn]["$$$"] += 100
    
        elif drawn_card == 10:
            player[player_turn]["$$$"] -= 100

            if player[player_turn]["$$$"] < 0:
                player_is_broke(player_turn, abs(player[player_turn]["$$$"]))
    
        elif drawn_card == 11:
            player[player_turn]["$$$"] += 10

        elif drawn_card == 12:
            player[player_turn]["$$$"] -= ((player[player_turn]["house total"] * 40) + (player[player_turn]["hotel total"] * 115))
            if player[player_turn]["$$$"] < 0:
                player_is_broke(player_turn, abs(player[player_turn]["$$$"]))

        elif drawn_card == 13:
            player[player_turn]["$$$"] -= 50
            if player[player_turn]["$$$"] < 0:
                player_is_broke(player_turn, abs(player[player_turn]["$$$"]))

        elif drawn_card == 14:
            player[player_turn]["$$$"] += 25

        elif drawn_card == 15:
            player[player_turn]["$$$"] += 100

        refresh_board()


community_chest = community_chest_cards_class()


class player_action_class():
    """allows the player to interact with the board"""
    def __call__(self, _player: int):
        """updates actions based on given player's position"""

        global current_action
        global current_screen

        # chance + C.C card actions
        if player[_player]["pos"] in [7, 22, 36]:
            current_action = "chance"
            current_screen = "game_notice"

            print(chance.art[0])
            print(f"    {chance.art[1]}")
            print(f"    {chance.art[2]}")
            print()
            print(f"    === {chance.draw_card()} ===\n\n    ", end="")

        elif player[_player]["pos"] in [2, 17, 33]:
            current_action = "community chest"
            current_screen = "game_notice"

            # cannot be looped through as extra space is only added to last two lines
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
            player[player_turn]["last pos"] = player[player_turn]["pos"]
            player[player_turn]["pos"] = 40
            player[player_turn]["status"] = "jail"
            update_player_position(40)
            update_player_position(player[player_turn]["last pos"], "remove")

        elif player[_player]["pos"] not in [0, 10, 20, 40]:
            self.rent_mgmt(_player)

    def rent_mgmt(self, _player: int, rent_multi: int | None = 1, rent_fixed: int | None = None):
        """
        determines rent owed, or if the property can be bought.
        rent_fixed is applied equally to upgraded properties 
        (except mortgages), and is applied alongside rent_multi.
        rent_multi overrides utility multiplier
        """

        global current_action
        _prop = prop_from_pos[player[_player]["pos"]]
        _owner = property_data[_prop]["owner"]
        if property_data[_prop]["owner"] == None:
            current_action = "property"

        elif property_data[_prop]["upgrade state"] != -1:
            
            if rent_fixed != None:
                player[_player]["$$$"] -= rent_fixed * rent_multi
                player[_owner]["$$$"] += rent_fixed * rent_multi
                 
            elif property_data[_prop]["type"] == "utility":

                # if the player ownes both utilities (rent = 10x dice roll)
                if property_data[7]["owner"] == _player and property_data[10]["owner"] == _player:
                    
                    # if the multiplier is default (1), it is changed to 10
                    if rent_multi == 1: rent_multi = 10
                    player[_player]["$$$"] -= (player_movement.dice_value[1] + player_movement.dice_value[2]) * rent_multi
                    player[_owner]["$$$"] += (player_movement.dice_value[1] + player_movement.dice_value[2]) * rent_multi
                else:
                    if rent_multi == 1: rent_multi = 10
                    player[_player]["$$$"] -= (player_movement.dice_value[1] + player_movement.dice_value[2]) * rent_multi
                    player[_owner]["$$$"] += (player_movement.dice_value[1] + player_movement.dice_value[2]) * rent_multi

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
                player_is_broke(_player)


player_action = player_action_class()
                

def homescreen():
    clear_screen()

    # the 'current_screen' variable is used for user input, to make sure that the correct output happens
    global current_screen
    current_screen = "home_screen"

    # displaying the main menu
    print("")
    print(r"       ___  ___        _____     _____ ____     _____      _____      _____     ____     ___  ___"    )
    print(r"      ╱   ╲╱   ╲      ╱     ╲    │    ╲│  │    ╱     ╲    │  _  \    ╱     ╲    │  │     ╲  \/  ╱ │ coded by:")
    print(r"     ╱  /╲  ╱\  ╲    │  (_)  │   │  ╲  ╲  │   │  (_)  │   │  ___/   │  (_)  │   │  │__    ╲_  _╱  │ James E.")
    print(r"    ╱__/  ╲╱  \__╲    ╲_____╱    │__│╲____│    ╲_____╱    │__│       ╲_____╱    │_____│    │__│   │ 2024, 2025"    )
    print("")
    print("")
    saved_game = False
    try: x = open("save_file.james", encoding = "utf-8")
    except: pass
    else: x.close(); saved_game = True
    for i in create_button_prompts(["Start game", "Continue", "Online"], [True, saved_game, True]):
        print(i)
    print("")
    print("    ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────")
    print("\n    ", end = "")


homescreen()


class trade_screen_class():
    """stores all necessary functions for trading"""

    def __init__(self):
        self.player_1 = {"player": None, "$$$": 0, "props": [], "accepted?": False}
        self.player_2 = {"player": None, "$$$": 0, "props": [], "accepted?": False}

        self.nothing_art = ["",
                            "",
                            "                                        ╱─────────╮",
                            "                                        ╲──────╮  │",
                            "                                               │  │",
                            "                                               │  │",
                            "                                               │  │",
                            "                                               └──┘",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "         ┌──┐       ",
                            "         │  │       ",
                            "         │  │       ",
                            "         │  │       ",
                            "         │  ╰──────╲",
                            "         ╰─────────╱"]
        self.prop_prop_art = ["    ┌──────────────────────────────┐",
                              "    │ 🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦 │",
                              "    │ 🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦 │    ╱─────────╮",
                              "    │ 🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦 │    ╲──────╮  │",
                              "    │ 🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦 │           │  │",
                              "    │                              │           │  │",
                              "    │                              │           │  │",
                              "    │                              │           └──┘",
                              "    │                              │",
                              "    │                              │───────────────────┐",
                              "    │                              │🟦🟦🟦🟦🟦🟦🟦🟦🟦 │",
                              "    │                              │🟦🟦🟦🟦🟦🟦🟦🟦🟦 │",
                              "    │                              │🟦🟦🟦🟦🟦🟦🟦🟦🟦 │",
                              "    │                              │🟦🟦🟦🟦🟦🟦🟦🟦🟦 │",
                              "    │                              │                   │",
                              "    │                              │                   │",
                              "    │                              │                   │",
                              "    │                              │                   │",
                              "    │                              │                   │",
                              "    │                              │                   │",
                              "    │                              │                   │",
                              "    │                              │                   │",
                              "    └──────────────────────────────┘                   │",
                              "                        │                              │",
                              "         ┌──┐           │                              │",
                              "         │  │           │                              │",
                              "         │  │           │                              │",
                              "         │  │           │                              │",
                              "         │  ╰──────╲    │                              │",
                              "         ╰─────────╱    │                              │",
                              "                        │                              │",
                              "                        └──────────────────────────────┘"]
        self.prop_money_art = ["    ┌──────────────────────────────┐",
                               "    │ 🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦 │",
                               "    │ 🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦 │",
                               "    │ 🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦 │",
                               "    │ 🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦 │",
                               "    │                              │",
                               "    │                              │",
                               "    │                              │",
                               "    │                              │",
                               "    │                              │",
                               "    │                              │    ╱─────────╮",
                               "    │                              │    ╲──────╮  │",
                               "    │                              │           │  │",
                               "    │                              │           │  │",
                               "    │                              │           │  │",
                               "    │                              │           └──┘",
                               "    │                              │",
                               "    │                              │    ┌──────────────────────────────────────────────┐",
                               "    │                              │   ┌──────────────────────────────────────────────┐│",
                               "    │                              │  ┌──────────────────────────────────────────────┐││",
                               "    │                              │  │ |---------------| MONOPOLY |---------------| │││",
                               r"    │                              │  │ | ┌───┐         ‾‾╱‾‾‾‾‾‾╲‾‾        ┌─V─_┐ | │││",
                               r"    └──────────────────────────────┘  │ | │100│      __╱‾‾        ‾‾╲__     │(¯¯❬│ | │││",
                               r"                                      │ | └───┘     ╱ ____   __    __  ╲    └◿°°─┘ | │││",
                               r"                       ┌──┐           │ |          | /_| |  /  \  /  \  |          | │││",
                               r"                       │  │           │ |          |  _| |_| (, || (, | |          | │││",
                               r"                       │  │           │ | ┌_/\_┐    \_|___| \__/  \__/_╱     ┌───┐ | │││",
                               r"                       │  │           │ | │|__|│       ╲__        __╱        │100│ | │││",
                               r"                       │  ╰──────╲    │ | └────┘          ╲______╱           └───┘ | ││┘",
                               "                       ╰─────────╱    │ |------------------------------------------| │┘ ",
                               "                                      └──────────────────────────────────────────────┘  "]
        self.prop_prop_money_art = ["    ┌──────────────────────────────┐",
                                    "    │ 🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦 │",
                                    "    │ 🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦 │    ╱─────────╮",
                                    "    │ 🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦 │    ╲──────╮  │",
                                    "    │ 🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦 │           │  │",
                                    "    │                              │           │  │",
                                    "    │                              │           │  │",
                                    "    │                              │           └──┘",
                                    "    │                              │",
                                    "    │                              │───────────────────┐",
                                    "    │                              │🟦🟦🟦🟦🟦🟦🟦🟦🟦 │",
                                    "    │                              │🟦🟦🟦🟦🟦🟦🟦🟦🟦 │",
                                    "    │                              │🟦🟦🟦🟦🟦🟦🟦🟦🟦 │",
                                    "    │                              │🟦🟦🟦🟦🟦🟦🟦🟦🟦 │",
                                    "    │                              │                   │",
                                    "    │                              │                   │",
                                    "    │                              │                   │",
                                    "    │                              │    ┌──────────────────────────────────────────────┐",
                                    "    │                              │   ┌──────────────────────────────────────────────┐│",
                                    "    │                              │  ┌──────────────────────────────────────────────┐││",
                                    r"    │                              │  │ |---------------| MONOPOLY |---------------| │││",
                                    r"    │                              │  │ | ┌───┐         ‾‾╱‾‾‾‾‾‾╲‾‾        ┌─V─_┐ | │││",
                                    r"    └──────────────────────────────┘  │ | │100│      __╱‾‾        ‾‾╲__     │(¯¯❬│ | │││",
                                    r"                        │             │ | └───┘     ╱ ____   __    __  ╲    └◿°°─┘ | │││",
                                    r"         ┌──┐           │             │ |          | /_| |  /  \  /  \  |          | │││",
                                    r"         │  │           │             │ |          |  _| |_| (, || (, | |          | │││",
                                    r"         │  │           │             │ | ┌_/\_┐    \_|___| \__/  \__/_╱     ┌───┐ | │││",
                                    r"         │  │           │             │ | │|__|│       ╲__        __╱        │100│ | │││",
                                    r"         │  ╰──────╲    │             │ | └────┘          ╲______╱           └───┘ | ││┘",
                                    r"         ╰─────────╱    │             │ |------------------------------------------| │┘",
                                    "                        │             └──────────────────────────────────────────────┘",
                                    "                        └──────────────────────────────┘"]

        self.action = None
        self.action2 = None
        self.is_trade = False
        self.curr_player = self.player_1["player"]

    def __call__(self, player):
        """adds the given player as player 1 of the bid"""

        try: self.player_1["player"] = int(player)
        except: pass
        else: self.other_player_prompt()

    def other_player_prompt(self, prop_ = None):
        """
        prompts the player who they would like to trade with.
        if a property is given, it is added once a player is chosen.
        if there isn't first player, then the current player is chosen
        """

        if self.player_1["player"] == None:
            self.player_1["player"] = player_turn
        self.queued_prop = prop_
        clear_screen()
        self.action = "player select"
        self.is_trade = True

        global current_screen 
        current_screen = "trade window"

        self.other_players = []
        self.spacing = []

        print("    ╔════════════════════════════════════════════════════════════════╗")
        print("    ║                                                                ║")
        print("    ║                  CHOOSE PLAYER TO TRADE WITH:                  ║")
        print("    ║                                                                ║")
        print("    ╚════════════════════════════════════════════════════════════════╝")
        print()

        for i in range(players_playing):
            if i + 1 != self.player_1["player"]: 
                self.other_players.append(str(i + 1))
                self.spacing.append(3)

        self.other_players.append("Back")
        self.spacing.append(6)
        self.spacing[0] = 4

        for i in create_button_prompts(self.other_players, spacing = self.spacing): print(i)
        print("\n    ", end = "")

    def display_trade_window(self):
        """displays the current player offers"""

        self.action = "offer screen"
        clear_screen()
        print()
        print("    ╔═══════════════════════════════╗ ╔═══════════════════════════════╗")
        print("    ║                               ║ ║                               ║")
        print(f"    ║        PLAYER {self.player_1['player']} OFFER:        ║ ║        PLAYER {self.player_2['player']} OFFER:        ║")
        print("    ║                               ║ ║                               ║")

        extra_space = ["", ""]
        for i in range(28 - len(str(self.player_1["$$$"]))):
            extra_space[0] += " "

        for i in range(28 - len(str(self.player_2["$$$"]))):
            extra_space[1] += " "

        print(f"    ║ ${self.player_1['$$$']}{extra_space[0]} ║ ║ ${self.player_2['$$$']}{extra_space[1]} ║")
        print("    ║                               ║ ║                               ║")
               
        # prints offered properties, space is left blank if run out
        for i in range(max(len(self.player_1["props"]), len(self.player_2["props"]))):

            extra_space = ["", ""]
            is_mortgaged = [" ", " "]
            property_ = ["", ""]
            seperator = ["│","│"]
            try:
                for ii in range(21 - len(property_data[self.player_1["props"][i]]["name"])): extra_space[0] += " "
                if property_data[self.player_1["props"][i]]["upgrade state"] == -1: is_mortgaged[0] = "M"
            except:
                extra_space[0] = "                     "
                property_[0] = ""
                seperator[0] = " "
                
            try:
                for ii in range(21 - len(property_data[self.player_2["props"][i]]["name"])): extra_space[1] += " "
                if property_data[self.player_2["props"][i]]["upgrade state"] == -1: is_mortgaged[1] = "M"
            except:
                extra_space[1] = "                     "
                property_[1] = ""
                seperator[1] = " "
                

            print(f"    ║ {property_[0]}{extra_space[0]} {seperator[0]} {is_mortgaged[0]}     ║ ║ {property_[1]}{extra_space[1]} {seperator[1]} {is_mortgaged[1]}     ║")

        print("    ╚═══════════════════════════════╝ ╚═══════════════════════════════╝")
        print()
        
        props = False
        for i in property_data:
            if i["owner"] == self.curr_player: props = True

        if self.curr_player == self.player_1["player"]:
            _prompt = f"Swap to P{self.player_2['player']}"
        else:
            _prompt = f"Swap to P{self.player_1['player']}"

        for i in create_button_prompts(["Offer money", "Properties", _prompt, "Accept trade", "Back"], [True, props, True, True, True], [4, 3, 3, 3, 6]):
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
        #reduces unnecessary money transfer (eg: $50, $30) > ($20, $0)
        if self.player_1["$$$"] != 0 and self.player_2["$$$"] != 0:
            x = min(self.player_1["$$$"], self.player_2["$$$"])
            self.player_1["$$$"] -= x
            self.player_2["$$$"] -= x

        # if players are ONLY swapping properties
        if self.player_1["$$$"] == 0 and self.player_2["$$$"] == 0:
            if len(self.player_1["props"]) + len(self.player_2["props"]) > 0:
                for i in self.prop_prop_art: print(i)
            else: 
                for i in self.nothing_art: print(i)

        # if a player is ONLY donating money
        elif len(self.player_1["props"]) == 0 and len(self.player_2["props"]) == 0:
            
            print("    === you can't just [give money] ===\n    ", end = "")
            self.action2 = "donate"

        # if both players are swapping properties (AND MONEY)
        elif len(self.player_1["props"]) > 0 and len(self.player_2["props"]) > 0:
            for i in self.prop_prop_money_art: print(i)

        # if a player is swapping properties for money
        else:
            for i in self.prop_money_art: print(i)


        if self.action2 != "donate":

            # adds the players offers to the opposite player
            player[self.player_1["player"]]["$$$"] += self.player_2["$$$"]
            player[self.player_2["player"]]["$$$"] += self.player_1["$$$"]

            # subtracts the players offers from their own money
            player[self.player_1["player"]]["$$$"] -= self.player_1["$$$"]
            player[self.player_2["player"]]["$$$"] -= self.player_2["$$$"]

            # updates the properties
            for prop in self.player_1["props"]: prop["owner"] = self.player_2["player"]  
            for prop in self.player_2["props"]: prop["owner"] = self.player_1["player"]

            # clears player offers
            self.player_1 = {"player": None, "$$$": 0, "props": [], "accepted?": False}
            self.player_2 = {"player": None, "$$$": 0, "props": [], "accepted?": False}
            
        clear_screen()
        print("\n    ", end="")

    def input_management(self, _input):
        """determines what to do with user input"""
        if _input in ["b", "B"]:

            has_properties = False
            for i in property_data:
                if i["owner"] == self.player_1:
                    has_properties = True

            if has_properties == True:
                display_property_list(player_turn)
            else:
                broke_alert = False
                for i in range(players_playing):
                    if player[i + 1]["$$$"] < 0:
                        player_is_broke(i + 1)
                        broke_alert = True
                        break

                if broke_alert == False:
                    refresh_board()

        elif self.action == "player select":
            try:
                int(_input)
            except:
                if self.action2 == "message":
                    if _input in ["p", "P"]:
                        self.player_2 = self.player_1
                        self.action2 = None
                        self.action = None
                        self.display_trade_window()
                        print("=== if you insist... ===\n\n    ", end="")

                    elif _input in ["o", "O"]:

                        # clears the conversation and recreates prompts
                        self.action2 = None
                        self.other_player_prompt()
                        
                else:
                    print("\n    === command not recognised. Please enter a number. ===\n\n", end = "")

            else:
                if _input in self.other_players:
                    self.player_2["player"] = int(_input)
                    self.action = None
                    if self.queued_prop != None:
                        self.add_prop_offer(self.queued_prop)
                        self.queued_prop = None
                    self.curr_player = self.player_1["player"]
                    self.display_trade_window()

                elif int(_input) == self.player_1["player"]: 
                    print("\n    === you can't trade with yourself! ===\n\n")
                    for i in create_button_prompts(["Pleeeeeeease", "Ok"]):
                        print(i)
                    print("\n    ", end="")

                else:
                    print("\n    === that player does not exist ===\n\n    ", end = "")
         
        elif self.action == "offer screen":
            if user_input in ["o", "O"]:
                self.action = "money"
                print(f"\n    === player {self.curr_player}, enter cash offer (you can exchange more money than you currently have) ===\n\n    ", end = "")

            elif user_input in ["p","P"]:
                
                has_properties = False
                for i in property_data:
                        if i["owner"] == self.curr_player:
                            has_properties = True
                            break
                if has_properties == True:
                    display_property_list(self.curr_player)
                else:
                    print("\n    === you have no properties to view ===\n\n    ", end = "")

            elif user_input in ["s", "S"]:
                if self.curr_player == self.player_1[0]:
                    self.curr_player = self.player_2[0]
                else:
                    self.curr_player = self.player_1[0]

            elif user_input in ["a", "A"]:
                if self.curr_player == self.player_1[0]:
                    self.player_1[3] = True
                    self.curr_player = self.player_2[0]
                    if self.player_2[3] == True:
                        self.trade_completed()
                else: 
                    self.player_2[3] = True                    
                    self.curr_player = self.player_1[0]
                    
        elif self.action == "money":
            try:
                if self.curr_player == self.player_1["player"]:
                    self.player_1["$$$"] = int(_input)
                else:
                    self.player_2["$$$"] = int(_input)
                self.display_trade_window()
             
            except:
                print("\n    === command not recognised. please enter a number (you can enter [0]) ===\n\n   ", end = "")


trade_screen = trade_screen_class()


class refresh_board_class():
    def __init__(self):
        self.money_structure = better_iter(["outer", "top_info", "bottom_info"], True)
        self.action = None

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
                if player_turn == players_playing - (position - 1): outer = "│"

                return f"{outer} player {players_playing - (position - 1)} | {player[players_playing - (position - 1)]['char']} {outer}"

            def bottom_info():
                outer = " "; extra_space = ""

                if player_turn == players_playing - (position - 1): outer = "│"
                for i in range(12 - len(str(player[players_playing - (position - 1)]["$$$"]))): extra_space += " "

                return f"{outer} ${player[players_playing - (position - 1)]['$$$']}{extra_space} {outer}"

            def outer():
                if   player_turn == players_playing - (position - 1)    : return "┌───────────────┐"
                elif player_turn == players_playing - (alt_position - 1): return "└───────────────┘"
                else                                                    : return "                 "

            output = "                 " # 17 spaces

            # check if there is a player to display at this location
            if position <= players_playing: output = locals()[next(self.money_structure)]()
            return output

        # money structure otherwise starts at index 1 from previous use
        self.money_structure.index = -1

        global current_screen
        global passed_go

        current_screen = "game"
        clear_screen()

        # some of the emojis don't display properly in VS, distorting the board, but looks normal in terminal
        print("")
        print("     ▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁")
        print("    \x1b[7m▊\x1b[0m▛               ▎   $220   ▎  __()_   ▎   $220   ▎   $240   \x1b[0m▎   $200 __\x1b[7m▊\x1b[0m   $260   \x1b[7m▊\x1b[0m   $260   ▎   $150   \x1b[7m▊\x1b[0m   $280   \x1b[7m▊\x1b[0m   GO TO JAIL  ▜▎")
        print(f"    \x1b[7m▊\x1b[0m  FREE PARKING  ▎          ▎  \\__ \\   ▎          ▎          \x1b[0m▎_()_()_| /\x1b[7m▊\x1b[0m          \x1b[7m▊\x1b[0m          ▎{player_display_location[28][1]}\x1b[7m▊\x1b[0m          \x1b[7m▊\x1b[0m     {player_display_location[30][1]} ▎")
        print(f"    \x1b[7m▊\x1b[0m      ____      ▎{player_display_location[21][1]}▎{player_display_location[22][1]}▎{player_display_location[23][1]}▎{player_display_location[24][1]}\x1b[0m▎\\  ____ _)\x1b[7m▊\x1b[0m{player_display_location[26][1]}\x1b[7m▊\x1b[0m{player_display_location[27][1]}▎    /\\    \x1b[7m▊\x1b[0m{player_display_location[29][1]}\x1b[7m▊\x1b[0m  /¯¯¯¯\\        ▎")
        print("    \x1b[7m▊\x1b[0m     /[__]\\     ▎          ▎  / /  /\\ ▎          ▎          \x1b[0m▎/__)  /_\\ \x1b[7m▊\x1b[0m          \x1b[7m▊\x1b[0m          ▎   /  \\   \x1b[7m▊\x1b[0m          \x1b[7m▊\x1b[0m | (¯¯)/¯¯¯¯\\   ▎")
        print(f"    \x1b[7m▊\x1b[0m    |_ () _|    ▎          ▎  \\ ‾-‾ / ▎  Fleet   ▎Trafalgar ▎{player_display_location[25][1]}\x1b[7m▊\x1b[0mLeicester \x1b[7m▊\x1b[0m Coventry ▎  |    |  \x1b[7m▊\x1b[0m          \x1b[7m▊\x1b[0m  \\_¯¯| (¯¯) |  ▎")
        print("    \x1b[7m▊\x1b[0m     U----U     ▎  Strand  ▎   ‾---‾  ▎  Street  ▎  Square  \x1b[0m▎Fenchurch \x1b[7m▊\x1b[0m  Square  \x1b[7m▊\x1b[0m  Street  ▎   \\__/   \x1b[7m▊\x1b[0mPiccadilly\x1b[7m▊\x1b[0m    \\/ \\_¯¯_/   ▎")
        print(f"    \x1b[7m▊\x1b[0m   {player_display_location[20][1]}   \x1b[48;2;248;49;47m▎          \x1b[0m▎  CHANCE  \x1b[48;2;248;49;47m▎          ▎          \x1b[0m▎ Station  \x1b[7m▊\x1b[0m\x1b[48;2;255;176;46m          \x1b[30m\x1b[7m▊\x1b[0m\x1b[48;2;255;176;46m          \x1b[0m▎WaterWorks\x1b[7m▊\x1b[0m\x1b[48;2;255;176;46m          \x1b[7m▊\x1b[0m     O   \\/     ▎")
        print("    \x1b[7m▊\x1b[0m                \x1b[48;2;248;49;47m▎          \x1b[0m▎          \x1b[48;2;248;49;47m▎          ▎          \x1b[0m▎          \x1b[7m▊\x1b[0m\x1b[48;2;255;176;46m          \x1b[30m\x1b[7m▊\x1b[0m\x1b[48;2;255;176;46m          \x1b[0m▎          \x1b[7m▊\x1b[0m\x1b[48;2;255;176;46m          \x1b[7m▊\x1b[0m      O O       ▎")
        print("    \x1b[7m▊\x1b[0m▔▔▔▔▔▔▔▔▔▔▔▔\x1b[48;2;255;103;35m▔▔▔▔\x1b[0m▛▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▜\x1b[48;2;0;210;106m▔▔▔▔\x1b[0m▔▔▔▔▔▔▔▔▔▔▔▔▎")
        print("    \x1b[7m▊\x1b[0mVine Street \x1b[48;2;255;103;35m    \x1b[0m▎                                                                                                  \x1b[7m▊\x1b[0m\x1b[48;2;0;210;106m    \x1b[0m Regent St. ▎")
        print(f"    \x1b[7m▊\x1b[0m    $200    \x1b[48;2;255;103;35m    \x1b[0m▎     _____     __          ___    ___  ___   ______     ______       {player_turn_display[player_turn][0]}                     \x1b[7m▊\x1b[0m\x1b[48;2;0;210;106m    \x1b[0m    $300    ▎")
        print(f"    \x1b[7m▊\x1b[0m {player_display_location[19][1]} \x1b[48;2;255;103;35m    \x1b[0m▎    |  _  \\   |  |        /   \\   \\  \\/  /  |  ____|   |  __  \\      {player_turn_display[player_turn][1]}                     \x1b[7m▊\x1b[0m\x1b[48;2;0;210;106m    \x1b[0m {player_display_location[31][1]} ▎")
        print(f"    \x1b[7m▊\x1b[0m▁▁▁▁▁▁▁▁▁▁▁▁\x1b[48;2;255;103;35m▁▁▁▁\x1b[0m▎    |  ___/   |  |__     /  ^  \\   \\_  _/   |  __|_    |      /      {player_turn_display[player_turn][2]}                     \x1b[7m▊\x1b[0m\x1b[48;2;0;210;106m\x1b[30m▁▁▁▁\x1b[0m▁▁▁▁▁▁▁▁▁▁▁▁▎")
        print(f"    \x1b[7m▊\x1b[0mMarlborough \x1b[48;2;255;103;35m    \x1b[0m▎    |__|      |_____|   /__/¯\\__\\   |__|    |______|   |__|\\__\\      {player_turn_display[player_turn][3]}                     \x1b[7m▊\x1b[0m\x1b[48;2;0;210;106m    \x1b[0m            ▎")
        print("    \x1b[7m▊\x1b[0m   Street   \x1b[48;2;255;103;35m    \x1b[0m▎                                                                                                  \x1b[7m▊\x1b[0m\x1b[48;2;0;210;106m    \x1b[0m Oxford St. ▎")
        print("    \x1b[7m▊\x1b[0m   $180     \x1b[48;2;255;103;35m    \x1b[0m▎      ____       _____      __                                                                    \x1b[7m▊\x1b[0m\x1b[48;2;0;210;106m    \x1b[0m    $300    ▎")
        print(f"    \x1b[7m▊\x1b[0m {player_display_location[18][1]} \x1b[48;2;255;103;35m    \x1b[0m▎     /  __|     /     \\    |  |                                                                   \x1b[7m▊\x1b[0m\x1b[48;2;0;210;106m    \x1b[0m {player_display_location[32][1]} ▎")
        print("    \x1b[7m▊\x1b[0m▁▁▁▁▁▁▁▁▁▁▁▁\x1b[48;2;255;103;35m▁▁▁▁\x1b[0m▎    |  |_  |   |  (_)  |   |__|                                                                   \x1b[7m▊\x1b[0m\x1b[48;2;0;210;106m▁▁▁▁\x1b[0m▁▁▁▁▁▁▁▁▁▁▁▁▎")
        print("    \x1b[7m▊\x1b[0m COMUNITY CHEST ▎     \\____/     \\_____/    (__)                                                                   \x1b[7m▊\x1b[0m COMUNITY CHEST ▎")
        print(f"    \x1b[7m▊\x1b[0m   {player_display_location[17][1]}   ▎                                                                                                  \x1b[7m▊\x1b[0m   {player_display_location[33][1]}   ▎")
    
        button_states = [False, False, False, True]

        # checks if the players owns any properties, greys out the button otherwise
        for i in range(28):
            if property_data[i]["owner"] == player_turn: 
                button_states[1] = True
                break

        # similar checks are performed for the other prompts
        # if the player has spent 3 turns in jail, they MUST pay bail, regardless
        if player_movement.dice_rolled == False and current_action == None and player[player_turn]["jail time"] < 3:
            button_states[0] = True

        if current_action == None and player_movement.dice_rolled == True:
            button_states[2] = True

        button_list = create_button_prompts(["Roll dice","Properties", "End turn", "Save & Exit"], button_states, [4, 3, 3, 6])
        print(f"    \x1b[7m▊\x1b[0m  💰  💵  🪙    ▎{button_list[0]}          \x1b[7m▊\x1b[0m  💰  💵  🪙    ▎")
        print(f"    \x1b[7m▊\x1b[0m💵  🪙  💰  💵  ▎{button_list[1]}          \x1b[7m▊\x1b[0m💵  🪙  💰  💵  ▎")
        print(f"    \x1b[7m▊\x1b[0m▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▎{button_list[2]}          \x1b[7m▊\x1b[0m▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▎")
        print(f"    \x1b[7m▊\x1b[0m            \x1b[48;2;255;103;35m    \x1b[0m▎{button_list[3]}          \x1b[7m▊\x1b[0m\x1b[48;2;0;210;106m    \x1b[0m            ▎")
        print("    \x1b[7m▊\x1b[0m Bow Street \x1b[48;2;255;103;35m    \x1b[0m▎                                                                                                  \x1b[7m▊\x1b[0m\x1b[48;2;0;210;106m    \x1b[0m  Bond St.  ▎")
    
        button_states = [["", ""],[True, True]]

        if current_action == "property":
            button_states[0] = ["Buy property", "Auction"]
            if player[player_turn]["$$$"] < property_data[prop_from_pos[player[player_turn]["pos"]]]["street value"]: button_states[1][1] = False

        elif player[player_turn]["status"] == "jail":
            button_states[0] = ["Give bail $", "Use card"]
         
            if player[player_turn]["$$$"] < 50        : button_states[1][0] = False
            if player[player_turn]["jail passes"] == 0: button_states[1][1] = False
        button_list = create_button_prompts(button_states[0], button_states[1])

        print(f"    \x1b[7m▊\x1b[0m   $180     \x1b[48;2;255;103;35m    \x1b[0m▎{button_list[0]}                                                       \x1b[7m▊\x1b[0m\x1b[48;2;0;210;106m    \x1b[0m    $320    ▎")
        print(f"    \x1b[7m▊\x1b[0m {player_display_location[16][1]} \x1b[48;2;255;103;35m    \x1b[0m▎{button_list[1]}                                                       \x1b[7m▊\x1b[0m\x1b[48;2;0;210;106m    \x1b[0m {player_display_location[34][1]} ▎")
        print(f"    \x1b[7m▊\x1b[0m\x1b[▁▁▁▁▁▁▁▁▁▁▁▁▁\x1b[48;2;255;103;35m▁▁▁▁\x1b[0m▎{button_list[2]}                                                       \x1b[7m▊\x1b[0m\x1b[48;2;0;210;106m▁▁▁▁\x1b[0m▁▁▁▁▁▁▁▁▁▁▁▁▎")
        print(f"    \x1b[7m▊\x1b[0m |\\⁔ Marylebone ▎{button_list[3]}                                                       \x1b[7m▊\x1b[0m Liverpool|∖↙() ▎")
        print("    \x1b[7m▊\x1b[0m ¯| |◁ Station  ▎                                                                                                  \x1b[7m▊\x1b[0m Station  |‿ |  ▎")
        print("    \x1b[7m▊\x1b[0m () |  $200     ▎                                                                                                  \x1b[7m▊\x1b[0m $200      | () ▎")
        print(f"    \x1b[7m▊\x1b[0m  | ⁀|{player_display_location[15][1]}▎                                                                                                  \x1b[7m▊\x1b[0m{player_display_location[35][1]}▷|‿|_ ▎")
        print("    \x1b[7m▊\x1b[0m▁()↗∖|▁▁▁▁▁▁▁▁▁▁▎                                                                                                  \x1b[7m▊\x1b[0m▁▁▁▁▁▁▁▁▁▁▁▁▁\\|▁▎")
        print("    \x1b[7m▊\x1b[0mNorthumb'nd \x1b[48;2;245;47;171m    \x1b[0m▎                                                                                                  \x1b[7m▊\x1b[0m      _  CHANCE ▎")
        print("    \x1b[7m▊\x1b[0m   Avenue   \x1b[48;2;245;47;171m    \x1b[0m▎                                                                                                  \x1b[7m▊\x1b[0m    /‾_‾\\|‾|    ▎")
        print("    \x1b[7m▊\x1b[0m    $160    \x1b[48;2;245;47;171m    \x1b[0m▎                                                                                                  \x1b[7m▊\x1b[0m   | | \\_  | () ▎")
        print(f"    \x1b[7m▊\x1b[0m {player_display_location[14][1]} \x1b[48;2;245;47;171m    \x1b[0m▎                                                                                                  \x1b[7m▊\x1b[0m    \\_\\{player_display_location[36][1]}▎")
        print("    \x1b[7m▊\x1b[0m▁▁▁▁▁▁▁▁▁▁▁▁\x1b[48;2;245;47;171m▁▁▁▁\x1b[0m▎                                                                                                  \x1b[7m▊\x1b[0m▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▎")
        print("    \x1b[7m▊\x1b[0m            \x1b[48;2;245;47;171m    \x1b[0m▎                                                                                                  \x1b[7m▊\x1b[0m\x1b[48;2;28;89;255m    \x1b[0m            ▎")
        print(f"    \x1b[7m▊\x1b[0m Whitehall  \x1b[48;2;245;47;171m    \x1b[0m▎                                                                                {display_money(4)} \x1b[7m▊\x1b[0m\x1b[48;2;28;89;255m    \x1b[0m Park Lane  ▎")    
        print(f"    \x1b[7m▊\x1b[0m   $140     \x1b[48;2;245;47;171m    \x1b[0m▎                                                                                {display_money(4)} \x1b[7m▊\x1b[0m\x1b[48;2;28;89;255m    \x1b[0m    $350    ▎")
        print(f"    \x1b[7m▊\x1b[0m {player_display_location[13][1]} \x1b[48;2;245;47;171m    \x1b[0m▎                                                                                {display_money(4)} \x1b[7m▊\x1b[0m\x1b[48;2;28;89;255m    \x1b[0m {player_display_location[37][1]} ▎")
        print(f"    \x1b[7m▊\x1b[0m▁▁▁▁▁▁▁▁▁▁▁▁\x1b[48;2;245;47;171m▁▁▁▁\x1b[0m▎                                                                                {display_money(3, 4)} \x1b[7m▊\x1b[0m\x1b[48;2;28;89;255m▁▁▁▁\x1b[0m▁▁▁▁▁▁▁▁▁▁▁▁▎")
        print(f"    \x1b[7m▊\x1b[0m Electric Co.   ▎                                                                                {display_money(3)} \x1b[7m▊\x1b[0m ∖  ⁄ SUPER TAX ▎")
        print(f"    \x1b[7m▊\x1b[0m $150       |\\  ▎                                                                                {display_money(3)} \x1b[7m▊\x1b[0m- 💎 -     $100 ▎")
        print(f"    \x1b[7m▊\x1b[0m          __| \\ ▎                                                                                {display_money(2, 3)} \x1b[7m▊\x1b[0m/¯¯¯¯\\{player_display_location[38][1]}▎")
        print(f"    \x1b[7m▊\x1b[0m{player_display_location[12][1]}\\ |¯¯ ▎                                                                                {display_money(2)} \x1b[7m▊\x1b[0m (⁐⁐) |         ▎")   
        print(f"    \x1b[7m▊\x1b[0m           \\|   ▎                                                                                {display_money(2)} \x1b[7m▊\x1b[0m\\____/\x1b[0m          ▎")
        print(f"    \x1b[7m▊\x1b[0m▔▔▔▔▔▔▔▔▔▔▔▔\x1b[48;2;245;47;171m▔▔▔▔\x1b[0m▎                                                                                {display_money(1, 2)} \x1b[7m▊\x1b[0m\x1b[48;2;28;89;255m▔▔▔▔\x1b[0m▔▔▔▔▔▔▔▔▔▔▔▔▎")
        print(f"    \x1b[7m▊\x1b[0m Pall Mall  \x1b[48;2;245;47;171m    \x1b[0m▎                                                                                {display_money(1)} \x1b[7m▊\x1b[0m\x1b[48;2;28;89;255m    \x1b[0m   Mayfair  ▎")
        print(f"    \x1b[7m▊\x1b[0m   $140     \x1b[48;2;245;47;171m    \x1b[0m▎                                                                                {display_money(1)} \x1b[7m▊\x1b[0m\x1b[48;2;28;89;255m    \x1b[0m    $400    ▎")
        print(f"    \x1b[7m▊\x1b[0m {player_display_location[11][1]} \x1b[48;2;245;47;171m    \x1b[0m▎                                                                                {display_money(0, 1)} \x1b[7m▊\x1b[0m\x1b[48;2;28;89;255m    \x1b[0m {player_display_location[39][1]} ▎") # the 0 is necessary because otherwise things break
        print("    \x1b[7m▊\x1b[0m▁▁▁▁▁▁▁▁▁▁▁▁\x1b[48;2;245;47;171m▁▁▁▁\x1b[0m▙▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▟\x1b[0m\x1b[48;2;28;89;255m▁▁▁▁\x1b[0m▁▁▁▁▁▁▁▁▁▁▁▁▎")
        print("    \x1b[7m▊\x1b[0m      │ ║ ║ ║ ║ \x1b[48;2;0;166;237m▎          \x1b[30m│          \x1b[0m▎  CHANCE  \x1b[48;2;0;166;237m▎          \x1b[0m▎  King's  ▎          \x1b[48;2;165;105;83m▎          \x1b[0m▎ COMUNITY \x1b[7m▊\x1b[0m\x1b[48;2;165;105;83m          \x1b[7m▊\x1b[0m  ____    ____  ▎")
        print("    \x1b[7m▊\x1b[0m   J  │ J A I L \x1b[48;2;0;166;237m▎          \x1b[30m│          \x1b[0m▎  _---_   \x1b[48;2;0;166;237m▎          \x1b[0m▎  Cross   ▎  INCOME  \x1b[48;2;165;105;83m▎          \x1b[0m▎   CHEST  \x1b[7m▊\x1b[0m\x1b[48;2;165;105;83m          \x1b[7m▊\x1b[0m /  __|  /    \\ ▎")
        print(f"    \x1b[7m▊\x1b[0m   U  │ ║ ║ ║ ║ ▎Pent'ville│  Euston  ▎ / _-_ \\  ▎The Angel ▎{player_display_location[5][1]}▎   TAX    ▎whitechp'l▎{player_display_location[2][1]}\x1b[7m▊\x1b[0m Old Kent \x1b[0m\x1b[7m▊\x1b[0m|  |_ ‾||  ()  |▎")
        print(f"    \x1b[7m▊\x1b[0m   S  │{player_display_location[40][1]}▎   Road   │   Road   ▎ \\/  / /  ▎Islington ▎ \\¯/___(¯/▎          ▎   Road   ▎          \x1b[7m▊\x1b[0m   Road   \x1b[7m▊\x1b[0m \\____/  \\____/ ▎")
        print(f"    \x1b[7m▊\x1b[0m   T  │_║_║_║_║_▎          │          ▎   / /_   ▎          ▎( _______\\▎    🔷    ▎          ▎🪙  💰  💵\x1b[7m▊\x1b[0m          \x1b[0m\x1b[7m▊\x1b[0m{player_display_location[0][1]}____  ▎")
        print(f"    \x1b[7m▊\x1b[0m   {player_display_location[10][1]}   ▎{player_display_location[9][1]}│{player_display_location[8][1]}▎   \\___\\  ▎{player_display_location[6][1]}▎/_| () () ▎{player_display_location[4][1]}▎{player_display_location[3][1]}▎  💵  💰  \x1b[7m▊\x1b[0m{player_display_location[1][1]}\x1b[7m▊\x1b[0m  /|-----/   /  ▎")
        print(f"    \x1b[7m▊\x1b[0m    VISITING    ▎   $120   │   $100   ▎{player_display_location[7][1]}▎   $100   ▎   $200   ▎ PAY $200 ▎   $ 60   ▎💰  🪙  💵\x1b[7m▊\x1b[0m   $ 60   \x1b[7m▊\x1b[0m  \\|-----\\___\\  ▎")
        print("    \x1b[7m▊\x1b[0m▙               ▎          │          ▎          ▎          ▎          ▎          ▎          ▎          \x1b[7m▊\x1b[0m          \x1b[0m\x1b[7m▊\x1b[0m               ▟▎")
        print("     ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔ ")

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
            print()
        
        if passed_go == True:
            for i in range(3):
                print(f"    {passed_go_art[i]}")
            passed_go = False

        print("    ", end="")

    def input_management(self, user_input):
        global dev_mode
        global current_action

        if self.action == "save notice": homescreen()

        if self.action == "trade query" and user_input in ["y", "Y"]:
            trade_screen(player_turn)
            trade_screen.other_player_prompt()

        elif self.action == "trade query" and user_input in ["n", "N"]:
            self.action = None

        elif self.action == "trade query":
            print("\n    === command not recognised ===\n\n    ", end = "")

        elif user_input in ["r", "R"]:
            if (player_movement.dice_rolled == False and current_action == None and player[player_turn]["status"] != "jail") or dev_mode != False:
                if dev_mode != False: print("=== skipped with devmode ===")
                refresh_board()
                player_movement.start_roll()

            elif current_action != None:
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
                print("\n    === you don't own any properties. Do you want to initiate a trade instead ([Y]es/[N]o)? ===\n\n    ", end = "")
                self.action = "trade query"
            else:
                display_property_list(player_turn)

        elif user_input in ["e", "E"]:
            if (player_movement.dice_rolled == True and current_action == None) or dev_mode == True:
                next(player_turn)
                player_movement.dice_rolled = False
                player_movement.doubles_rolled = 0

                # when a player goes bankrupt, players alive are checked,
                # so there will be at least 2 people when this code is active.
                while player[player_turn]["status"] == "bankrupt": next(player_turn)
                
                # forcibly moves the player out of jail if they've been in for 3 turns
                if player[player_turn]["jail time"] >= 3:
                    player_movement.remove_from_jail(player_turn)
                    player[player_turn]["$$$"] -= 50
                    if player[player_turn]["$$$"] < 0: player_is_broke(player_turn, abs(player[player_turn]["$$$"]))
                    

                refresh_board()
                
            else: 
                print("\n    === roll dice first and complete space-dependent action first ===\n\n    ", end = "")
                
        elif user_input in ["s", "S"]:

            save_game_to_file("game_version", "players_playing", "player_turn", "player_movement.doubles_rolled",
                              "dev_mode", "player_movement.dice_rolled", "current_action", "player", "chance.cards_value", 
                              "chance.index","community_chest.cards_value", "community_chest.index")
            self.action = "save_notice"
            print("\n    === game saved. [Enter] to return to the main menu ===\n\n    ", end = "")

        elif user_input in ["b", "B"] and current_action == "property":
            _prop = property_data[prop_from_pos[player[player_turn]["pos"]]]
            if player[player_turn]["$$$"] >= _prop["street value"]:
            
                _prop["owner"] = int(player_turn)
                _prop["upgrade state"] = 1
                player[player_turn]["total properties"] += 1
                player[player_turn]["$$$"] -= _prop["street value"]

                # one line = more optimised 😎
                colour_set = list(filter(lambda x: (x["colour set"] == _prop["colour set"] and x["owner"] == _prop["owner"]) if "colour set" in x.keys() else False, property_data))

                # brown and dark blue (sets 0 and 7) only have two properties in their set
                if ((len(colour_set) == 3 and _prop["colour set"] not in [0, 7])
                    or (len(count) == 2 and _prop["colour set"] in [0, 7])):

                    for _prop in colour_set: _prop["upgrade state"] = 2

                current_action = None
                refresh_board()

            else:
                print("\n    === you can't afford this property ===\n\n    ", end="")

        elif user_input in ["a", "A"] and current_action == "property":
            auctioned_property = prop_from_pos[player[player_turn]["pos"]]

            # since bidding will require 'player_turn' to change, this stores the proper player turn
            display_property.true_player_turn = player_turn.index
            display_property.action = "auction"
            display_property(auctioned_property)

        elif user_input in ["g", "G"] and player[player_turn]["status"] == "jail":
            
            # moving the player to just visiting
            if player[player_turn]["$$$"] >= 50:
                player[player_turn]["$$$"] -= 50
                player_movement.remove_from_jail(player_turn)
                refresh_board()
            else:
                print("\n    === you cannot afford bail ===\n\n    ", end = "")

        elif user_input in ["u", "U"] and player[player_turn]["status"] == "jail":
            if player[player_turn]["jail passes"] > 0:
                player[player_turn]["jail passes"] -= 1
                player_movement.remove_from_jail(player_turn)
                refresh_board()
            else:
                print("\n    === you don't have any get out of jail free cards to use ===\n\n    ", end = "")

        elif user_input == "devmode":
            dev_mode = True
            refresh_board()

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
            player_movement.dice_value[1] = int(input("    === first dice value: "))
            player_movement.dice_value[2] = int(input("    === second dice value: "))
            player_movement.current_die_rolling = 3
            player_movement.dice_countdown = 1
            player_movement.dice_roll_animation()
           
        elif user_input == "bankruptcy" and dev_mode == True:
            x = input("    === which player: ")
            xx = input("    === debt: ")
            player_is_broke(int(x), int(xx))

        elif user_input ==  "editplayerdict" and dev_mode == True:
            print("    === Please edit position using the 'setplayerpos' command ===")
            x = input("    === which player: ")
            xx = input("    === which key: ")
            xxx = input("    === what value: ")
            try   : player[int(x)][xx] = int(xxx)
            except: player[int(x)][xx] = xxx

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
                    property_data[int(xx)]["owner"] = x
                    property_data[int(xx)]["upgrade state"] = 1

                    # checks if the player now owns all the properties in a colour set
                    count = 0
                    for i in property_data:
                        if "colour set" in i.keys():
                            if (i["colour set"] == property_data[int(xx)]["colour set"]
                                and i["owner"] == property_data[int(xx)]["owner"]):
                                count += 1

                    # brown and dark blue (sets 0 and 7) only have two properties in their set
                    if ((count == 3 and property_data[int(xx)]["colour set"] not in [0, 7])
                        or (count == 2 and property_data[int(xx)]["colour set"] in [0, 7])):

                        property_data[int(xx)]["upgrade state"] = 2
                        for i in property_data:
                            if "colour set" in i.keys():
                                if i["colour set"] == property_data[int(xx)]["colour set"]: i["upgrade state"] = 2
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

        elif user_input == "arbitrarycode" and dev_mode == True:
            exec(input())

        else:
            print("\n    === command not recognised ===\n\n    ", end = "")


refresh_board = refresh_board_class()


def new_game():
    global player_turn
    global current_screen
    global current_die_rolling
    global player_display_location
    global doubles_rolled
    global passed_go
    global current_action
    global start_time

    doubles_rolled = 0
    current_die_rolling = 0

    current_screen = "game_notice"
    passed_go = False
    current_action = None
    
         
    # updating the board so all players are on start
    for i in range(players_playing):
        player_display_location[0][i + 3] = True

    player_display_location[0][7] = players_playing - 1
    update_player_position(0)

    start_time = time()

    display_game_notice()


def display_game_notice():
    global current_screen
    current_screen = "game_notice"

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
    print("    ", end = "")


def new_game_select():
    clear_screen()

    global current_screen
    global name_detection
    global player_turn

    print()
    if name_detection == True:
        print("    === enter player icons ===")
    else:
        print("    === choose number of players ===")
    print("")

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
    print("")

    # this is displaying each players's character
    if name_detection == True:
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

    else:
        print("    ", end="")


def read_save(_file: str | None = "save_file.james", _encoding: str | None = "utf-8"):
    """reads save_file.james as python code """
    testfile = open(_file, encoding = _encoding)

    # game version will get overwritten, so a copy is recorded to compare with save version to make sure they're the same
    true_game_version = game_version
    
    for _line in testfile:
        exec(_line, globals())    
   
    # this subtracts the time played on the save from the start time so the end-screen calculations reflect the extra time played
    global start_time
    start_time = time() - time_played

    if game_version != true_game_version:
        raise Exception("=== save is not the same version as game ===")


def save_game_to_file(*variables):
    """
    writes given variables, modified properties, and time played to
    save_file.james. the save is created if it does not exist
    """

    try   : save_file = open("save_file.james", "w", encoding="utf-8")
    except: save_file = open("save_file.james", "x", encoding="utf-8")

    save_file.write("# Wonder what happens if you mess with the save? Stuff around and find out.\n")
    save_file.write("# (note: the save is read using \"exec()\", so any python code can be added ;))\n\n")

    for var in variables:
        var_type = type(eval(var)).__name__

        # strings have quotation marks added as otherwise determining type would be difficult
        if var_type == "str":
            save_file.write(f"{var} = \"{eval(var)}\"\n")

        # iterators are saved as lists with "i", and the index below
        elif var_type == "better_iter":
            _list = []
            for i in eval(var): _list.append(i)
            
            save_file.write(f"{var} = better_iter({_list}); {var}.index = {eval(var).index}; {var}.loop = {eval(var).loop}\n")
        else:
            save_file.write(f"{var} = {eval(var)}\n")

    # since only modified properties are saved, they have their own check
    for i in range(28):
        if property_data[i]["owner"] != None:
            save_file.write(f"property_data[{i}] = {property_data[i]}\n")

    # the time is rounded to the nearest second 
    save_file.write(f"time_played = {str(round(time() - start_time))}\n")

    save_file.close()


def bankruptcy(_player: int, cause: str | None = "bank"):
    """
    determines how to handle a player's bankruptcy, based on cause,
    and displays win/game finished screen if applicable

    cause should either be "bank" or the player owed (1/2/3/4)
    """

    player[_player]["status"] = "bankrupt"
    player[_player]["$$$"] = 0
    # if the player is in debt to the bank, all properties are returned
    if cause == "bank":
        for _property in property_data:
            if _property["owner"] == _player:
                _property["upgrade state"] = 0
                _property["owner"] = None

    else:
        owed_player = int(cause)
        for _property in property_data:
            if _property["owner"] == _player:
                _property["owner"] = owed_player

                # for some stupid reason, upgraded properties are not transferred,
                # but are sold and the money is given to the owed player instead.
                upgrades = _property["upgrade state"] - 2
                _property["upgrade state"] = 1
                if upgrades > 0:
                    player[owed_player]["$$$"] += upgrades * (_property["house cost"] / 2)

        # transfers any escape jail cards to the other player
        player[owed_player]["jail passes"] += player[_player]["jail passes"]

    remaining_players = 0

    # this is checking how many players remain after a bankruptcy
    for i in range(players_playing):
        if player[i + 1]["status"] == "playing": remaining_players += 1

    # if only one player remains, then the game finished screen is displayed
    if remaining_players == 1:

        # total amount of seconds played
        _total = round(time() - start_time)

        # bit of simple math that converts a integer of seconds played into Xh Ym Zs format
        _hours = floor(_total/3600)
        _remainder = _total % 3600
        _minutes = floor(_remainder / 60)
        _seconds = _remainder % 60

        _length = len(str(_hours)) + len(str(_minutes)) + len(str(_seconds))

        extra_space = ""
        for ii in range(floor((6 - _length) / 2)): extra_space += " "

        extra_extra_space = ""
        if _length % 2 == 1: extra_extra_space = " "

        clear_screen()
        print("    ╔════════════════════════════════════════════════════════════════╗")
        print("    ║                                                                ║")
        print("    ║                       CONGRATULATIONS :)                       ║")
        print("    ║                                                                ║")
        print("    ║                     You have won the game!                     ║")
        print(f"    ║{extra_space}                 you spent {_hours}h {_minutes}m {_seconds}s to do it                 {extra_extra_space}{extra_space}║")
        print("    ║                                                                ║")
        print("    ║           was this really the best use of your time?           ║")
        print("    ║                                                                ║")
        print("    ╚════════════════════════════════════════════════════════════════╝")
        print("\n    ", end = "")
        exit()


class player_movement_class:
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
        self.dice_value = [None, 0, 0, 0]
        self.dice_countdown = 0
        self.doubles_rolled = 0
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

    def start_roll(self):
        self.dice_value[1] = randint(1, 6)
        print("┌───────────┐")
        print("    │           │")
        print(f"    {self.dice_image_frame[self.dice_value[1]][0]}")
        print(f"    {self.dice_image_frame[self.dice_value[1]][1]}")
        print(f"    {self.dice_image_frame[self.dice_value[1]][2]}")
        print("    │           │")
        print("    └───────────┘")
        self.dice_rolling_state = 1
        self.dice_countdown = 10

        # moves the cursor (text output location) to the middle of the die
        print("\x1b[6F")

        self.mgmt()

    def second_dice_start(self):
        self.dice_value[2] = randint(1, 6)

        print("\x1b[3F")
        print("    ┌───────────┐   ┌───────────┐")
        print("    │           │   │           │")
        for i in range(3):
            print(f"    {self.dice_image_frame[self.dice_value[1]][i]}   {self.dice_image_frame[self.dice_value[2]][i]}")
        print("    │           │   │           │")
        print("    └───────────┘   └───────────┘")
        self.dice_rolling_state = 2
        self.dice_countdown = 10

        # moves the cursor (text output location) to the middle of the die
        print("\x1b[6F")

    def remove_from_jail(self, _player):
        player[_player]["last pos"] = 40
        player[_player]["pos"] = 10
        update_player_position(10)
        update_player_position(40, "remove")
        player[_player]["jail time"] = 0
        player[_player]["status"] = "playing"

    def movement_setup(self):
        global current_screen

        # this is updating the player's last position, so that the player's icon can be removed from the board
        player[player_turn]["last pos"] = player[player_turn]["pos"]

        if self.dice_value[1] == self.dice_value[2]:
            self.doubles_rolled += 1
            
            # the player escapes jail if they roll doubles
            if player[player_turn]["status"] == "jail":
                self.remove_from_jail(player_turn)

                # resets the player's 
                self.doubles_rolled = 0
                self.dice_rolled = False

            # rolling 3 doubles in a row sends the player to jail
            elif doubles_rolled == 3:

                # 40 is the space value for jail
                player[player_turn]["pos"] = 40
                player[player_turn]["status"] = "jail"
                update_player_position(40)
                update_player_position(player[player_turn]["last pos"], "remove")

                # makes sure that the player can't continue their turn once in jail
                self.dice_rolled = True

        if player[player_turn]["status"] != "jail":

            # this is adding the dice roll's value to the player's position
            player[player_turn]["pos"] = (player[player_turn]["pos"] + self.dice_value[1] + self.dice_value[2])

            # makes sure that the player's position is valid (unless they got sent to jail)
            if player[player_turn]["pos"] >= 40 and player[player_turn]["status"] != "jail":
                player[player_turn]["pos"] -= 40

        # rolling doubles in jail has logic above, as well as non-jail conditions
        elif self.dice_value[1] != self.dice_value[2]:
            player[player_turn]["jail time"] += 1

            # cancels the player movement
            self.dice_rolled = True

        # moves the cursor back to the bottom of the dice
        print("\x1b[5E")

        # giving the player time to check their dice roll
        print("    === [Enter] to continue ===\n    ", end = "")

        current_screen = "dice_roll_accept"

        # disables the dice to recieve user input, but then is re-enabled
        self.dice_rolling_state = "off"

        if self.dice_value[1] != self.dice_value[2]: self.doubles_rolled = 0
        else: self.doubles_rolled += 1
        self.player_roll_itr = iter(range(self.dice_value[1] + self.dice_value[2]))

    def mgmt(self):
        """makes the player hop on all the spaces on the way to their roll"""

        global passed_go
        global current_screen
        global player_turn

        # when either die 1 or die 2 is being rolled
        if self.dice_rolling_state in [1, 2]:
            sleep(150)
            self.dice_roll_animation()

        # moves the player's icon forward one space, accounting for passing go
        elif self.dice_rolling_state == "movement":

            try:
                """
                x = next(player_roll_itr)
                if x + player[player_turn]["last pos"] + 1 < 40:
                    update_player_position(x + player[player_turn]["last pos"] + 1)
                    update_player_position(x + player[player_turn]["last pos"], "remove")
                else:
                    update_player_position(x + player[player_turn]["last pos"] - 39)
                    if x + player[player_turn]["last pos"] - 40 >= 0:
                        update_player_position(x + player[player_turn]["last pos"] - 40, "remove")
                    else:
                        update_player_position(39, "remove")
                """

                # determines what space the player is added to
                space = next(self.player_roll_itr) + player[player_turn]["last pos"] - 39
                if space < 0: space += 40
                update_player_position(space)

                # removes player from previous space, but if space is negative, add 40,
                # for when the player passes go (eg: currently at space 0, remove from 39)
                space -= 1
                if space < 0: space += 40
                update_player_position(space, "remove")

                sleep(500)
                refresh_board()

            # once the iterator has ran out the player is at the 
            # correct spot and the board will stop being refreshed
            except StopIteration:

                # only happens once the player passes go and their position is reset
                # extra check if the player leaves jail to stop passed go text
                if player[player_turn]["pos"] < player[player_turn]["last pos"] and player[player_turn]["last pos"] != 40:
                    player[player_turn]["$$$"] += 200
                    passed_go = True

                player_action(player_turn)
                   
                self.dice_rolling_state = "off"
                if self.doubles_rolled in [0, 3]: self.dice_rolled = True

                # board isn't displayed if actions show something else
                if current_screen == "game": refresh_board()

    def dice_roll_animation(self):

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

            # since the 'doubles' text is next to the dice and not under them, the calculations need to be performed while the lines are getting printed
            # it only is done when the dice are finished rolling, or otherwise it will appear while the dice are rolling
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
            self.second_dice_start()

        elif self.dice_countdown == 0: self.movement_setup()


player_movement = player_movement_class()


while True:

    # detecting user input pauses the program, and so is disables for the animations
    if player_movement.dice_rolling_state == "off":
        user_input = input()
        input_confirmation = True
    else:
         player_movement.mgmt()

    if current_screen == "home_screen" and input_confirmation == True:

        if user_input in ["devmode", "dev mode"]:
            dev_mode = True
            print("\n    === dev mode enabled ===\n\n    ", end = "")

        elif user_input in ["s", "S"]:
            current_screen = "player_select"
            name_detection = False
            new_game_select()

        elif user_input in ["c", "C"]:
              read_save("save_file.james", "utf-8") 
              display_game_notice()

        elif "nick" in user_input.lower():

            # in dedication to Nick Tho, who always uses his phone with night-shift enabled at the maximum intensity
            # changes the background to yellow
            system("\x1b[43m")
            homescreen()

            print("=== Nick Tho always uses night-shift on maxium intensity, I'm not trying to be racist ===\n")
            for i in create_button_prompts(["I'm offended", "Makes sense"]): print(i)
            print("\n    ", end = "")
            current_action = "nicktho"

        elif user_input in ["i", "I"] and current_action == "nicktho":
            homescreen()
            print("\n    === get over it. ===\n\n    ", end = "")

        elif user_input in ["m", "M"] and current_action == "nicktho":
            homescreen()
            print("\n    === wow thank you for understanding and not overreacting. ===\n\n    ", end = "")

        else:
            print("\n    === command not recognised ===\n\n    ", end = "")

    elif current_screen == "player_select" and input_confirmation == True:
        if user_input in ["2", "3", "4"]:

            players_playing = int(user_input)

            x = [] 
            for i in range(players_playing): x.append(i + 1)
            player_turn = better_iter(x, True)

            # the default index is -1, this make sure that player_turn always can return a value
            next(player_turn)

            name_detection = True

            player = {}

            _count = 0

            for i in range(players_playing):

                # players start at 1, not 0
                player[i + 1] = {
                    "char": "",
                    "$$$": 1500,
                    "pos": 0,

                    # this is so that the player's icon can be removed from the board
                    "last pos": 0,
                    
                    # not a bool since the player could get 2 get out of jail free cards
                    "jail passes": 0,
                    "jail time": 0,
                    "house total": 0,
                    "hotel total": 0,
                    "total properties": 0,
                    "status": "playing",

                    # separate to the game version for online games
                    "version": game_version
                    }
            new_game_select()

        elif user_input in ["b", "B"]:
            name_detection == False
            players_playing = 0
            homescreen()

        # recording entered names
        elif name_detection == True:

            # measures inputted name width, as having the width 
            # be too long or short distorts the board
            def char_width(char):
            
                # filters out unnecessary widths
                return width(char) in ("F", "W")

            # this counts the character width inputted, enforces 2 characters width
            x = 0
            for i in user_input:
                if char_width(i) == True: x += 2
                else: x += 1
            
            if user_input in ["  ", r"\\"]:
                print("\n    === nice try. ===\n\n    ", end = "")

            elif x == 2:
                _count += 1
                player[player_turn]["char"] = user_input
                next(player_turn)

                if _count == players_playing:
                    name_detection = False
                    new_game()
                else:                                    
                    new_game_select()

            elif x > 2:
                print("\n    === icon too large, try a different icon (eg: '😊' or 'JE') ===\n\n    ", end="")

            else:
                print("\n    === icon too small, try a different icon (eg: '😊' or 'JE') ===\n\n    ", end="")
        else:
            print("    === command not recognised === ")
            print("\n    ", end = "")

    elif current_screen == "game_notice" and input_confirmation == True:
        
        refresh_board()
        
        if current_action == "chance":
            current_action = None
            chance.perform_action()

        elif current_action == "community chest":
            current_action = None
            community_chest.perform_action()

    elif current_screen == "dice_roll_accept" and input_confirmation == True:
        
        # moves the cursor above the dice ('ESC[11F') and clears everything below ('ESC[0J')
        print("\x1b[11F\x1b[0J")

        # player movement is disabled within jail
        if player[player_turn]["pos"] != 40 and player[player_turn]["last pos"] != 40:
            player_movement.dice_rolling_state = "movement"
            player_movement.mgmt()
        else:
            player_movement.dice_rolling_state = "off"
            refresh_board()

    elif current_screen == "game" and input_confirmation == True:
        refresh_board.input_management(user_input)

    elif current_screen == "property_list" and input_confirmation == True:
        display_property_list.input_management(user_input)

    elif current_screen == "property" and input_confirmation == True:
        display_property.input_management(user_input)

    elif current_screen == "raise_money_screen" and input_confirmation == True:

        # makes sure that the user entered a number, than makes sure that the player owns that property
        try:
            x = int(user_input)
        except:
            print("\n    === command not recognised. please enter the number to the left of the desired property ===\n\n    ", end = "")
        else:
            if property_data[int(prop_from_pos[user_input])]["owner"] == player[player_turn]["pos"]:
                display_property(int(user_input))
            else:
                print("\n    === you don't own that property. please enter the number to the left of the desired property ===\n\n    ", end = "")

    elif current_screen == "bankruptcy" and input_confirmation == True:
        bankruptcy()

    elif current_screen == "trade window" and input_confirmation == True:
        trade_screen.input_management(user_input)

    input_confirmation = False
    user_input = ""