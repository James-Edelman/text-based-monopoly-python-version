# importing the required functions for operating terminal
from ast import literal_eval
import os
from random import randint, shuffle
import sys
import math
import time
from time import sleep
import unicodedata
from better_iterator import better_iter, previous

# setting the terminal name
sys.stdout.write("\x1b]2;Text-Based Monopoly\x07")

# initialising variables
players_playing = 0
current_die_rolling = 0
dice_value = [None, 0, 0, 0]
dev_mode = False
house_total = 32
hotel_total = 12
time_played = 0
game_version = 0.6

# the players' icons can only appear in certain points, so this list will have the default and modified art for the game board
# the default space is blank but there are some special cases that are specified individually
# (1st item = default art | 2nd item = modified art | 3rd item = standard/irregular display type...
# ...4th-7th items if players 1-4 are on the current space | total numbers of players on the space)
player_display_location = [["          ", "          ", "regular", False, False, False, False, 0] for i in range(41)]

player_display_location[7] = ["    ()    ", "    ()    ", "irregular", False, False, False, False, 0]
player_display_location[22] = ["    / /   ", "    / /   ", "irregular", False, False, False, False, 0]
player_display_location[36] = ["  \_|    ", "  \_|    ", "irregular", False, False, False, False, 0]
player_display_location[40] = [" ║ ║ ║ ║ ", " ║ ║ ║ ║ ", "irregular", False, False, False, False, 0]

# all of the art for dice frames, used for the dice rolling animation
dice_image_frame = [[] for i in range(7)]

dice_image_frame[0] = ["│           │", "│           │", "│           │"]
dice_image_frame[1] = ["│           │", "│     o     │", "│           │"]
dice_image_frame[2] = ["│   o       │", "│           │", "│       o   │"]
dice_image_frame[3] = ["│  o     o  │", "│           │", "│     o     │"]
dice_image_frame[4] = ["│  o     o  │", "│           │", "│  o     o  │"]
dice_image_frame[5] = ["│  o     o  │", "│     o     │", "│  o     o  │"]
dice_image_frame[6] = ["│  o  o  o  │", "│           │", "│  o  o  o  │"]

doubles_art = [
    "✨    |¯¯¯\   /¯¯\  |¯||¯| |¯⁐¯\ |¯|   |¯¯¯| /¯¯¯|   ✨   ",
    "   ✨ | [) | | () | | || | | --⟨ | |__ | ⁐|_ \ ¯¯\ ✨     ",
    " ✨   |___/   \__/   \__/  |_⁐_/ |___| |___| |⁐⁐_/     ✨",
]

chance_art = [
    "✨     /¯¯¯| |¯| |¯|   /¯\   |¯¯\|¯|  /¯¯¯| |¯¯¯|   ✨  ",
    "   ✨ | (⁐⁐  | ¯¯¯ |  / ^ \  | \ \ | | (⁐⁐  | ⁐|_ ✨    ",
    " ✨    \___| |_|¯|_| /_/¯\_\ |_|\__|  \___| |___|     ✨",
]

community_chest_art = [
    "✨     /¯¯¯|  /¯¯\  |¯¯\/¯¯| |¯¯\/¯¯| |¯||¯| |¯¯\|¯| |¯¯¯| |¯¯¯¯¯| \¯\/¯/    /¯¯¯| |¯| |¯| |¯¯¯| /¯⁐⁐| |¯¯¯¯¯|   ✨  ",
    "   ✨ | (⁐⁐  | () | | \  / | | \  / | | || | | \ \ | ⁐| |⁐  ¯| |¯   \  /    | (⁐⁐  | ¯¯¯ | | ⁐|_ \__ \  ¯| |¯  ✨    ",
    " ✨    \___|  \__/  |_|\/|_| |_|\/|_|  \__/  |_|\__| |___|   |_|    /_/      \___| |_|¯|_| |___| |___/   |_|       ✨",
]

passed_go_art = [
    "✨    \¯\/¯/ /¯¯\  |¯||¯|    |¯¯¯\  /¯\   /¯⁐⁐| /¯⁐⁐| |¯¯¯| |¯¯¯\      /¯¯¯|   /¯¯\     ✨  ",
    "   ✨  \  / | () | | || |    | ⁐_/ / ^ \  \__ \ \__ \ | ⁐|_ | [) |    | (⁐¯¯| | () | ✨     ",
    " ✨    /_/   \__/   \__/     |_|  /_/¯\_\ |___/ |___/ |___| |___/      \___/   \__/       ✨",
]

player_turn_display = [[] for i in range(5)]

# art displaying the current turn
player_turn_display[1] = [" ___    ", "/__ |   ", " _| |_  ", "|_____| "]
player_turn_display[2] = [" _----_ ", "/__/  / ", " /  /___", "|______|"]
player_turn_display[3] = [" ______ ", "|____  \\", " |___ ⟨⁐", "|______/"]
player_turn_display[4] = ["__  __  ", "| || |_ ", "|___  _|", "   |_|  "]

community_chest_cards = [
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

property_data = [[] for i in range(28)]

# properties: name, type, street value, owner, # of upgrades, colour set group, rent, house 1, H2, H3, H4, hotel, house cost
# (note: colour set rent is double normal rent, isn't recorded. mortgage/unmortgage value based on street value; isn't recorded)
# stations/utilities: name, type, street value, owner
#                               0                  1       2   3  4  5  6   7    8     9     10    11    12
property_data[0]  = ["Old Kent Road"        , "property", 60 , 0, 0, 0, 2 , 10 , 30 , 90  , 160 , 250 , 50 ]
property_data[1]  = ["Whitechapel"          , "property", 60 , 0, 0, 0, 4 , 20 , 60 , 180 , 320 , 450 , 50 ]
property_data[2]  = ["Kings Cross Station"  , "station" , 200, 0, 0]
property_data[3]  = ["The Angel Islington"  , "property", 100, 0, 0, 1, 6 , 30 , 90 , 270 , 400 , 550 , 50 ]
property_data[4]  = ["Euston Road"          , "property", 100, 0, 0, 1, 6 , 30 , 90 , 270 , 400 , 550 , 50 ]
property_data[5]  = ["Pentonville Road"     , "property", 120, 0, 0, 1, 8 , 40 , 100, 300 , 450 , 600 , 50 ]
property_data[6]  = ["Pall Mall"            , "property", 140, 0, 0, 2, 10, 50 , 150, 450 , 625 , 750 , 100]
property_data[7]  = ["Electric Company"     , "utility" , 150, 0, 0]
property_data[8]  = ["Whitehall"            , "property", 140, 0, 0, 2, 10, 50 , 150, 450 , 625 , 750 , 100]
property_data[9]  = ["Northumberland Avenue", "property", 160, 0, 0, 2, 12, 60 , 180, 500 , 700 , 900 , 100]
property_data[10] = ["Marylebone Station"   , "station" , 200, 0, 0]
property_data[11] = ["Bow Street"           , "property", 180, 0, 0, 3, 14, 70 , 200, 550 , 750 , 950 , 100]
property_data[12] = ["Marlborough Street"   , "property", 180, 0, 0, 3, 14, 70 , 200, 550 , 750 , 950 , 100]
property_data[13] = ["Vine Street"          , "property", 200, 0, 0, 3, 16, 80 , 220, 600 , 800 , 1000, 100]
property_data[14] = ["Strand"               , "property", 220, 0, 0, 4, 18, 90 , 250, 700 , 875 , 1050, 150]
property_data[15] = ["Fleet Street"         , "property", 220, 0, 0, 4, 18, 90 , 250, 700 , 875 , 1050, 150]
property_data[16] = ["Trafalgar Square"     , "property", 240, 0, 0, 4, 18, 90 , 250, 700 , 875 , 1050, 150]
property_data[17] = ["Fenchurch St. Station", "station" , 200, 0, 0]
property_data[18] = ["Leicester Square"     , "property", 260, 0, 0, 5, 22, 110, 330, 800 , 975 , 1150, 150]
property_data[19] = ["Coventry Street"      , "property", 260, 0, 0, 5, 22, 110, 330, 800 , 975 , 1150, 150]
property_data[20] = ["Water Works"          , "utility" , 150, 0, 0]
property_data[21] = ["Piccadilly"           , "property", 280, 0, 0, 5, 24, 120, 360, 850 , 1025, 1200, 150]
property_data[22] = ["Regent Street"        , "property", 300, 0, 0, 6, 26, 130, 390, 900 , 1100, 1275, 200]
property_data[23] = ["Oxford Street"        , "property", 300, 0, 0, 6, 26, 130, 390, 900 , 1100, 1275, 200]
property_data[24] = ["Bond Street"          , "property", 320, 0, 0, 6, 28, 150, 450, 1000, 1200, 1400, 200]
property_data[25] = ["Liverpool St. Station", "station" , 200, 0, 0]
property_data[26] = ["Park Lane"            , "property", 350, 0, 0, 7, 35, 175, 500, 1100, 1300, 1500, 200]
property_data[27] = ["Mayfair"              , "property", 400, 0, 0, 7, 50, 200, 600, 1400, 1700, 2000, 200]

# this converts the player's position into the corresponding property number on the list
return_number_from_pos = {1:0, 3:1, 5:2, 6:3, 8:4, 9:5, 11:6, 12:7, 13:8, 14:9, 15:10, 16:11, 18:12, 19:13, 21:14,
                          23:15, 24:16, 25:17, 26:18, 27:19, 28:20, 29:21, 31:22, 32:23, 34:24, 35:25, 37:26, 39:27}



############################## CREATE ACTION PROMPTS ##############################

# this creates the icons showing available actions
def create_button_prompts(prompts = ["", "", "", ""], prompt_state = "default", spacing = "default"):

    # creating the output list for the art
    button_list = ["", "", "", ""]
    extra_space = ["", ""]
    num = 0

    #checking how many prompts to iterate through
    for i in prompts:
        num += 1

    # if "prompt_state" or "spacing" is left to default, its size is dependant on the amount of prompts
    if prompt_state == "default":
        prompt_state = []
        for i in range(num):
            prompt_state.append(True)

    if spacing == "default":
        spacing = [4]
        for i in range(num - 1):
            spacing.append(3)

    # cycles through the amount of prompts for the top layer 
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
        for ii in range(math.floor((12 - len(prompts[i]))/ 2)): extra_space[0] += " "

        # if an additional space is needed (instead of an extra 1 on each side) it is added to the right
        if len(prompts[i]) % 2 == 1:
            extra_space[1] = " "

        for ii in range(spacing[i]): button_list[2] += " "

        if prompts[i] == "":
            button_list[2] += "                  "
        elif prompt_state[i] == True:

            # centering the text with the extra space
            button_list[2] += f"|{extra_space[0]} [{prompts[i][0]}]{prompts[i][1:]}{extra_space[1]} {extra_space[0]}|"
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




############################## PLAYER LOCATION UPDATE ##############################

# this is updating the player_display_location list with the player's icon at the correct location, and will appear when the board is refreshed
def update_player_position(_pos, _action = "add"):
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
    # it is dependent on the order not to overuse "next(player_itr):
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
    if player_display_location[_pos][2] == "regular":

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
        # since all four characters are at the same spot, they are just added to the string
        elif player_display_location[_pos][7] == 4:
            update_displayed_art("p pp p")

    #################### IRREGULAR SPACES ####################

    elif player_display_location[_pos][2] == "irregular":

        ########## |    ()    | [chance @ space 7] ##########
        if _pos == 7:
            if player_display_location[_pos][7] == 1:

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
                update_displayed_art(" \_| p p")

            # (layout for reference : |💎\_| 💎 |)
            elif player_display_location[_pos][7] == 2:
                update_displayed_art("p\_| p ")

            # (layout for reference : |💎\_|💎💎|)
            elif player_display_location[_pos][7] == 3:
                update_displayed_art("p\_|pp")

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




############################## PLAYER RAN OUT OF MONEY ##############################n

# this function is called when a player is in debt, and displays the properties that they own, and the amount that they owe
def player_is_broke(_player, _debt):
    
    player_has_properties = False

    for i in range(28):
        if property_data[i][3] == _player:
            player_has_properties = True

    if player_has_properties == True:
        if dev_mode != True:
            os.system("cls")
       
        global current_screen
        global entered_number
        global conversion_dictionary

        current_screen = "raise_money_screen"
        entered_number = False

        # this makes sure that the text is centered by adding extra space if the debt is a different length than 4 digits
        extra_space = ""
        for i in range( 4 - len(str(_debt))):
            extra_space += " "

        print()
        print("    ╔════════════════════════════════════════════════════════════════╗")
        print("    ║                                                                ║")
        print("    ║                             NOTICE:                            ║")
        print("    ║                                                                ║")
        print(f"    ║{extra_space}             You are ${_debt} in debt! raise ${_debt} by              {extra_space}║")
        print("    ║      [M]ortgaging properties (for half of street vaule),       ║")
        print("    ║      [S]elling houses/hotels (for half build price), or by     ║")
        print("    ║         [T]rading with other players (without houses).         ║")
        print("    ║                                                                ║")
        print("    ║       start by entering the property number on the left.       ║")
        print("    ║                                                                ║")
        print("    ╚════════════════════════════════════════════════════════════════╝")

    
    else:
        print()
        print("    ╔════════════════════════════════════════════════════════════════╗")
        print("    ║                                                                ║")
        print("    ║                      PLAYER ELIMINATED :(                      ║")
        print("    ║                                                                ║")
        print("    ║        you don't have any properties to repay your debt,       ║")
        print("    ║            so you are bankrupt and out of the game.            ║")
        print("    ║                                                                ║")
        print("    ║    Now's a great opportunity to go outside and touch grass!    ║")
        print("    ║                                                                ║")
        print("    ║                             [enter]                            ║")
        print("    ╚════════════════════════════════════════════════════════════════╝")
        
        # updates the player's status to "bankrupt" and removes them from play
        player[_player]["status"] = "bankrupt"
        current_screen = "bankruptcy"




############################## DISPLAY INDIVIDUAL PROPERTY ##############################

def display_property_list(_player, clear = True):
    if clear == True:
        os.system("cls")

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
        if property_data[i][3] == player[_player]["char"]:
            sleep(0.15)
            _count += 1
            print(f"    ║     {_count} | {property_data[i][0]}", end = "")
                
            conversion_dictionary[_count] = i

            for ii in range(22 - len(property_data[i][0])):
                print(" ", end = "")
            print("|                        ║")
            stations_displayed = True

    # displays an extra blank line to separate the stations from the other cards
    if stations_displayed == True:
        print("    ║                                                                ║")
       

    for i in [7, 20]:
        if property_data[i][3] == player[_player]["char"]:
            sleep(0.15)
            _count += 1
            print(f"    ║     {_count} | {property_data[i][0]}", end = "")
                
            conversion_dictionary[_count] = i

            for ii in range(22 - len(property_data[i][0])):
                print(" ", end = "")
            print("|                        ║")
            utilities_displayed = True

    if utilities_displayed == True:
        print("    ║                                                                ║")

    for i in range(27):
        if property_data[i][3] == player[_player]["char"] and property_data[i][1] == "property":
            sleep(0.15)
            _count += 1
            conversion_dictionary[_count] = i
            if _count >= 10:
                print(f"    ║     {_count} | {property_data[i][0]}", end = "")
            else:
                print(f"    ║     {_count}  | {property_data[i][0]}", end = "")

            for ii in range(22 - len(property_data[i][0])):
                print(" ", end = "")

            print(f"│ ${property_data[i][2]}", end = "")
            if property_data[i][2] < 100:
                print(" ", end = "")

            if property_data[i][1] == "property" and property_data[i][4] != 0:
                print(f" | ${property_data[i][12]}", end = "")
                if property_data[i][12] < 100:
                    print(" ", end = "")
                    
                print(" × ", end = "")
                if property_data[i][4] == 5:
                    print("🏠🏠🏠🏠 🏨     ║")

                else:
                    x = ""
                    for ii in range(property_data[i][4]):
                        x += "🏠"
                    print(f"{x}", end = "")
                    for ii in range(16 - (2 * len(x))):
                        print(" ", end = "")
                    print("║")
            else:
                print("|                        ║")
    print("    ║                                                                ║")
    print("    ╚════════════════════════════════════════════════════════════════╝")
    print("    ", end="")




############################## DISPLAY INDIVIDUAL PROPERTY ##############################

def display_property(_prop_num, is_auction = False):
    global current_screen

    if is_auction == True:
        current_screen = "bidding"
    else:
        current_screen = "property"

    # station cards
    if _prop_num in [2, 10, 17, 25]:

        # while in an auction, player bids will appear to the side of the title deed, so a check is added
        if is_auction in [True, "finished"]:
            print("    ┌──────────────────────────────┐      ╔════════════════════════════════════════════════════════════════╗")
            print("    │                              │      ║                                                                ║")
            print("    │    /¯¯¯¯¯\           _______ │      ║                             NOTICE:                            ║")
            print("    │    \     /          /      / │      ║                                                                ║")
            print("    │     \   /          |      /  │      ║   you can bid more than your current cash, and go into debt.   ║")
            print("    │     |   |___________\    |   │      ║  however, at the end you will still have to find enough money  ║")
            print("    │  /¯¯¯                    |   │      ║                                                                ║")
            print("    │ |                         \  │      ╚════════════════════════════════════════════════════════════════╝")
        else:
            print("    ┌──────────────────────────────┐")
            print("    │                              │")
            print("    │    /¯¯¯¯¯\           _______ │")
            print("    │    \     /          /      / │")
            print("    │     \   /          |      /  │")
            print("    │     |   |___________\    |   │")
            print("    │  /¯¯¯                    |   │")
            print("    │ |                         \  │")

        print("    │  \__  _____  __________  __\ │")

        if bid_number >= 1:
            extra_space[0] = ""
            for i in range(4 - len(str(player_bids[bid_order[0]]) )):
                extra_space[0] += " "

            print("    │    /  |  /    \      /    \  │      ╔═════════════════════╗") 
            print(f"    │   /   | |      |    |      | │      ║ Player {bid_order[0]} bid: ${player_bids[bid_order[0]]} {extra_space}║ ✨ TOP BID ✨")
            print("    │  /___/   \____/      \____/  │      ╚═════════════════════╝")
        else:
            print("    │    /  |  /    \      /    \  │") 
            print("    │   /   | |      |    |      | │")
            print("    │  /___/   \____/      \____/  │")


        # This centers the station name by adding extra whitespace for every character less than the maximum possible length (21)
        extra_space[0] = ""
        for ii in range(math.floor((21 - len(property_data[_prop_num][0])) /2)):
            extra_space[0] += " "
            
        # since the upper code can only add two spaces, if the difference between the maximum length and actual length is odd (so the value is even)...
        # ...an extra space is added to the left of the name to center it properly
        extra_space[1] = ""
        if len(property_data[_prop_num][0]) % 2 == 0:
            extra_space[1] = " "

        if bid_number >= 2:
            print("    │                              │      ╔═════════════════════╗")
        
            # since displaying the bids requires extra space to centre, there is yet another extra_space variable
            extra_extra_space = ""
            for i in range(4 - len(player_bids[bid_order[1]])):
                extra_extra_space += " "

            print(f"    │{extra_space[0]}    {property_data[_prop_num][0]}     {extra_space[0]}│      ║ Player {bid_order[1]} bid: ${player_bids[bid_order[1]]} {extra_extra_space}║")
            print(f"    │                              │      ╚═════════════════════╝")

        else:
            print("    │                              │")
            print(f"    │{extra_space}    {property_data[_prop_num][0]}     {extra_space}│")
            print(f"    │                              │")

        if bid_number >= 3:
            extra_space = ""
            for i in range(4 - len(player_bids[bid_order[2]])):
                extra_space += " "
            print("    │ RENT                    $25  │      ╔═════════════════════╗")
            print(f"    │                              │      ║ Player {bid_order[2]} bid: ${player_bids[bid_order[2]]} {extra_space}║")
            print("    │ If 2 stations are owned $50  │      ╚═════════════════════╝")
        else:
            print("    │ RENT                    $25  │")
            print("    │                              │")
            print("    │ If 2 stations are owned $50  │")

        if bid_number >= 4:
            extra_space = ""
            for i in range(4 - len(player_bids[bid_order[3]])):
                extra_space += " "
            print("    │                              │      ╔═════════════════════╗")
            print(f"    │ If 3 stations are owned $100 │      ║ Player {bid_order[3]} bid: ${player_bids[bid_order[3]]} {extra_space}║")
            print("    │                              │      ╚═════════════════════╝")

        else: 
            print("    │                              │")
            print("    │ If 3 stations are owned $100 │")
            print("    │                              │")
        print("    │ If 4 stations are owned $200 │")
        print("    │                              │")
        print("    │                              │")
        print("    └──────────────────────────────┘")

    # electric company
    elif _prop_num == 7:

        # because electric company and water works are so different from the other cards, they have their own art

        if is_auction in [True, "finished"]:
            print("    ┌──────────────────────────────┐      ╔════════════════════════════════════════════════════════════════╗")
            print("    │             ____             │      ║                                                                ║")
            print("    │ __       /¯¯    ¯¯\       __ │      ║                             NOTICE:                            ║")
            print("    │   ¯¯--  /  _    _  \  --¯¯   │      ║                                                                ║")
            print("    │        |   \\\  //   |        │      ║   you can bid more than your current cash, and go into debt.   ║")
            print("    │  ----  |    \\\//    |  ----  │      ║  however, at the end you will still have to find enough money  ║")
            print("    │         \    \/    /         │      ║                                                                ║")
            print("    │   __--   |   ||   |   --__   │      ╚════════════════════════════════════════════════════════════════╝")

        else:
            print("    ┌──────────────────────────────┐")
            print("    │             ____             │")
            print("    │ __       /¯¯    ¯¯\       __ │")
            print("    │   ¯¯--  /  _    _  \  --¯¯   │")
            print("    │        |   \\\  //   |        │")
            print("    │  ----  |    \\\//    |  ----  │")
            print("    │         \    \/    /         │")
            print("    │   __--   |   ||   |   --__   │")

        print("    │ ¯        \   ||   /       ¯  │")

        if bid_number >= 1:
            extra_space = ""
            for i in range(4 - len(str(player_bids[bid_order[0]]))):
                extra_space += " "
            print("    │        /  \======/  \        │      ╔═════════════════════╗")
            print(f"    │     /     |======|     \     │      ║ Player {bid_order[0]} bid: ${player_bids[bid_order[0]]} {extra_space}║ ✨ TOP BID ✨")
            print("    │           |======|           │      ╚═════════════════════╝")

        else:
            print("    │        /  \======/  \        │")
            print("    │     /     |======|     \     │")
            print("    │           |======|           │")

        if bid_number >= 2:
            extra_space = ""
            for i in range(4 - len(str(player_bids[bid_order[1]]))):
                extra_space += " "
            print("    │            ¯¯¯¯¯¯            │      ╔═════════════════════╗")
            print(f"    │       Electric Company       │      ║ Player {bid_order[1]} bid: ${player_bids[bid_order[1]]} {extra_space}║")
            print("    │                              │      ╚═════════════════════╝")
        else:
            print("    │            ¯¯¯¯¯¯            │")
            print("    │       Electric Company       │")
            print("    │                              │")

        if bid_number >= 3:
            extra_space = ""
            for i in range(4 - len(str(player_bids[bid_order[2]]))):
                extra_space += " "
            print("    │   If one utility is owned,   │      ╔═════════════════════╗")
            print(f"    │    rent is 2 times amount    │      ║ Player {bid_order[2]} bid: ${player_bids[bid_order[2]]} {extra_space}║")
            print("    │        shown on dice         │      ╚═════════════════════╝")
        else:
            print("    │   If one utility is owned,   │")
            print("    │    rent is 2 times amount    │")
            print("    │        shown on dice         │")

        if bid_number >= 4:
            extra_space = ""
            for i in range(4 - len(str(player_bids[bid_order[3]]))):
                extra_space += " "
            print("    │                              │      ╔═════════════════════╗")
            print(f"    │                              │      ║ Player {bid_order[3]} bid: ${player_bids[bid_order[3]]} {extra_space}║")
            print("    │ If both utilities are owned, │      ╚═════════════════════╝")
        else:
            print("    │                              │")
            print("    │                              │")
            print("    │ If both utilities are owned, │")

        print("    │    rent is 4 times amount    │")
        print("    │        shown on dice         │")
        print("    │                              │")
        print("    └──────────────────────────────┘")

    elif _prop_num == 20:
        if is_auction in [True, "finished"]:
            print("    ┌──────────────────────────────┐      ╔════════════════════════════════════════════════════════════════╗")
            print("    │                              │      ║                                                                ║")
            print("    │           ()━╤╤━()           │      ║                             NOTICE:                            ║")
            print("    │      /¯\     /\              │      ║                                                                ║")
            print("    │     | ( —————┴┴————————╮     │      ║   you can bid more than your current cash, and go into debt.   ║")
            print("    │      \_/—————————————╮ │     │      ║  however, at the end you will still have to find enough money  ║")
            print("    │                      │ │     │      ║                                                                ║")
            print("    │                      |_|     │      ╚════════════════════════════════════════════════════════════════╝")
        else:
            print("    ┌──────────────────────────────┐")
            print("    │                              │")
            print("    │           ()━╤╤━()           │")
            print("    │      /¯\     /\              │")
            print("    │     | ( —————┴┴————————╮     │")
            print("    │      \_/—————————————╮ │     │")
            print("    │                      │ │     │")
            print("    │                      |_|     │")

        print("    │                              │")

        if bid_number >= 1:
            extra_space = ""
            for i in range(4 - len(str(player_bids[bid_order[0]]))):
                extra_space += " "

            print("    │                              │      ╔═════════════════════╗")
            print(f"    │         Water Works          │      ║ Player {bid_order[0]} bid: ${player_bids[bid_order[0]]} {extra_space}║ ✨ TOP BID ✨")
            print("    │                              │      ╚═════════════════════╝")
        else:
            print("    │                              │")
            print("    │         Water Works          │")
            print("    │                              │")

        if bid_number >= 2:
            extra_space = ""
            for i in range(4 - len(str(player_bids[bid_order[1]]))):
                extra_space += " "
            print("    │                              │      ╔═════════════════════╗")
            print(f"    │   If one utility is owned,   │      ║ Player {bid_order[1]} bid: ${player_bids[bid_order[1]]} {extra_space}║")
            print("    │    rent is 2 times amount    │      ╚═════════════════════╝")
        else:
            print("    │                              │")
            print("    │   If one utility is owned,   │")
            print("    │    rent is 2 times amount    │")

        if bid_number >= 3:
            extra_space = ""
            for i in range(4 - len(str(player_bids[bid_order[2]]))):
                extra_space += " "
            print("    │        shown on dice         │      ╔═════════════════════╗")
            print(f"    │                              │      ║ Player {bid_order[2]} bid: ${player_bids[bid_order[2]]} {extra_space}║")
            print("    │                              │      ╚═════════════════════╝")
        else:
            print("    │        shown on dice         │")
            print("    │                              │")
            print("    │                              │")

        if bid_number >= 4:
            extra_space = ""
            for i in range(4 - len(str(player_bids[bid_order[3]]))):
                extra_space += " "
            print("    │ If both utilities are owned, │      ╔═════════════════════╗")
            print(f"    │    rent is 4 times amount    │      ║ Player {bid_order[3]} bid: ${player_bids[bid_order[3]]} {extra_space}║")
            print("    │        shown on dice         │      ╚═════════════════════╝")
        else:
            print("    │ If both utilities are owned, │")
            print("    │    rent is 4 times amount    │")
            print("    │        shown on dice         │")
        print("    │                              │")
        print("    │                              │")
        print("    │                              │")
        print("    └──────────────────────────────┘")

    else:
        notice = ["      ║                                                                ║",
          "      ║                             NOTICE:                            ║",
          "      ║                                                                ║",
          "      ║   you can bid more than your current cash, and go into debt.   ║"]

        def display_bidding_notice(_i_value, _is_auction):
            if _is_auction in [True, "finished"]:
                print(notice[_i_value], end = "")
            print()

        extra_space = [0, 0, 0]

        if is_auction in [True, "finished"]:
            print("    ┌──────────────────────────────┐      ╔════════════════════════════════════════════════════════════════╗")
        else:
            print("    ┌──────────────────────────────┐")

        # this checks what colour set the property is in and adjusts the colour of the printed title deed
        if property_data[_prop_num][5] == 0:
            for i in range(4):
                print("    │ 🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫 │", end = "") # brown
                display_bidding_notice(i, is_auction)

        # light blue (set 1) and dark blue (set 7)set use the same colour
        elif property_data[_prop_num][5] in [1, 7]:
            for i in range(4):
                print("    │ 🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦 │", end = "") # blue
                display_bidding_notice(i, is_auction)
        
        elif property_data[_prop_num][5] == 2:
            for i in range(4):
                print("    │ 🟪🟪🟪🟪🟪🟪🟪🟪🟪🟪🟪🟪🟪🟪 │", end = "") # purple (there's no pink square emoji)
                display_bidding_notice(i, is_auction)

        elif property_data[_prop_num][5] == 3:
            for i in range(4):    
                print("    │ 🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧 │", end = "") # orange
                display_bidding_notice(i, is_auction)

        elif property_data[_prop_num][5] == 4:
            for i in range(4):
                print("    │ 🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥 │", end = "") # red
                display_bidding_notice(i, is_auction)

        elif property_data[_prop_num][5] == 5:
            for i in range(4):
                print("    │ 🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨 │", end = "") # yellow
                display_bidding_notice(i, is_auction)

        else:
            for i in range(4):
                print("    │ 🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩 │", end = "") # green
                display_bidding_notice(i, is_auction)

        if is_auction in [True, "finished"]:
            print("    │                              │      ║  however, at the end you will still have to find enough money  ║")
        else:
            print("    │                              │")

        # see the same code for the stations
        extra_space[0] = ""
        extra_extra_space = ""
        for ii in range(math.floor((21 - len(property_data[_prop_num][0])) /2)):
            extra_space[0] += " "

        if len(property_data[_prop_num][0]) % 2 == 0:
            extra_extra_space = " "

        if is_auction in [True, "finished"]:
            print(f"    │{extra_space[0]}{extra_extra_space}    {property_data[_prop_num][0]}     {extra_space[0]}│      ║                                                                ║")
            print("    │                              │      ╚════════════════════════════════════════════════════════════════╝")
        else:
            print(f"    │{extra_space[0]}{extra_extra_space}    {property_data[_prop_num][0]}     {extra_space[0]}│")
            print("    │                              │")

        # these just add an extra 1-2 spaces if depending on the length, for rent, colour set rent and all the other stats
        extra_space[0] = ""
        for ii in range(2 - len(str(property_data[_prop_num][6]))):
            extra_space[0] += " "

        print(f"    │ Rent                   ${property_data[_prop_num][6]}{extra_space[0]}   │")


        extra_space[0] = ""
        for ii in range(3 - len(str(property_data[_prop_num][6] * 2))):
            extra_space[0] += " "

        extra_space[1] = ""
        for ii in range(3 - len(str(property_data[_prop_num][7]))):
            extra_space[1] += " "

        if bid_number >= 1:
            print(f"    │ Rent with colour set   ${(property_data[_prop_num][6] * 2)}{extra_space[0]}  │      ╔═════════════════════╗")
                        
            extra_extra_space = ""
            for i in range(4 - len(str(player_bids[bid_order[0]]))):
                extra_extra_space += " "

            print(f"    │                              │      ║ Player {bid_order[0]} bid: ${player_bids[bid_order[0]]} {extra_extra_space}║ ✨ TOP BID ✨")
            print(f"    │ Rent with 🏠           ${property_data[_prop_num][7]}{extra_space[1]}  │      ╚═════════════════════╝")

        else:
            print(f"    │ Rent with colour set   ${(property_data[_prop_num][6] * 2)}{extra_space[0]}  │")
            print("    │                              │")
            print(f"    │ Rent with 🏠           ${property_data[_prop_num][7]}{extra_space[1]}  │")
            

        extra_space[0] = ""
        for ii in range(3 - len(str(property_data[_prop_num][8]))):
            extra_space[0] += " "

        extra_space[1] = ""
        for ii in range(4 - len(str(property_data[_prop_num][9]))):
            extra_space[1] += " "

        extra_space[2] = ""
        for ii in range(4 - len(str(property_data[_prop_num][10]))):
            extra_space[2] += " "

        if bid_number >= 2:

            print(f"    │ Rent with 🏠🏠         ${property_data[_prop_num][8]}{extra_space[0]}  │      ╔═════════════════════╗")

            extra_extra_space = ""
            for i in range(4 - len(str(player_bids[bid_order[1]]))):
                extra_extra_space += " "

            print(f"    │ Rent with 🏠🏠🏠       ${property_data[_prop_num][9]}{extra_space[1]} │      ║ Player {bid_order[1]} bid: ${player_bids[bid_order[1]]} {extra_extra_space}║")
            print(f"    │ Rent with 🏠🏠🏠🏠     ${property_data[_prop_num][10]}{extra_space[2]} │      ╚═════════════════════╝")
        
        else:

            print(f"    │ Rent with 🏠🏠         ${property_data[_prop_num][8]}{extra_space[0]}  │")
            print(f"    │ Rent with 🏠🏠🏠       ${property_data[_prop_num][9]}{extra_space[1]} │")
            print(f"    │ Rent with 🏠🏠🏠🏠     ${property_data[_prop_num][10]}{extra_space[2]} │")


        extra_space[0] = ""
        for ii in range(4 - len(str(property_data[_prop_num][11]))):
            extra_space[0] += " "

        if bid_number >= 3:
            print("    │                              │      ╔═════════════════════╗")

            extra_extra_space = ""
            for i in range(4 - len(str(player_bids[bid_order[2]]))):
                extra_extra_space += " "

            print(f"    │ Rent with 🏠🏠🏠🏠 🏨  ${property_data[_prop_num][11]}{extra_space[0]} │      ║ Player {bid_order[2]} bid: ${player_bids[bid_order[2]]} {extra_extra_space}║")
            print("    │                              │      ╚═════════════════════╝")
        
        else:
            print("    │                              │")
            print(f"    │ Rent with 🏠🏠🏠🏠 🏨  ${property_data[_prop_num][11]}{extra_space[0]} │")
            print("    │                              │")
        
        extra_space[0] = ""
        for ii in range(4 - len(str(property_data[_prop_num][12]))):
            extra_space[0] += " "


        if bid_number >= 4:
            print("    │ ---------------------------- │      ╔═════════════════════╗")

            extra_extra_space = ""
            for i in range(4 - len(str(player_bids[bid_order[3]]))):
                extra_extra_space += " "
        
            print(f"    │ House/hotel cost       ${property_data[_prop_num][12]}{extra_space[0]} │      ║ Player {bid_order[3]} bid: ${player_bids[bid_order[3]]} {extra_extra_space}║")
            print("    │                              │      ╚═════════════════════╝")
        else:
            print("    │ ---------------------------- │")
        
            print(f"    │ House/hotel cost       ${property_data[_prop_num][12]}{extra_space[0]} │")
            print("    │                              │")


        extra_space[0] = ""
        for ii in range(4 - len(str(property_data[_prop_num][2]))):
            extra_space[0] += " "

        print(f"    │ Street value           ${property_data[_prop_num][2]}{extra_space[0]} │")

        extra_space[0] = ""
        for ii in range(3 - len(str(int(property_data[_prop_num][2] / 2)))):
            extra_space[0] += " "                                                                
        print(f"    │ mortgage value         ${int(property_data[_prop_num][2] / 2)}{extra_space[0]}  │")

        print("    └──────────────────────────────┘")

    if is_auction == True and player_bids[player_turn] == 0:
        print(f"\n    === player {player_turn} place a bid or [Skip] ===")

    elif is_auction == True:
        print(f"\n    === player {player_turn} either raise your bid or [S]kip ===")

    elif is_auction == "finished":
        print(f"\n    === player {player_turn} has won the bid, press [Enter] to continue ===")

    print("\n    ", end = "")




############################## CHANCE CARDS ##############################

class chance_cards_class():
    """contains all actions related to chance card management"""

    def __init__(self):

        # note: the numbers at the start are for saving the arrangement of the shuffled cards
        self.cards = [
                      "0 Advance to go (collect $200)",
                      "1 Advance to Trafalgar Square. If you pass go, collect $200",
                      "2 Advance to Pall Mall. If you pass go, collect $200",
                      "3 Advance to the nearest utility. If unowned, you may buy it from the bank. If owned, throw the dice and pay owner 10x dice roll",
                      "4 Advance to the nearest station. If unowned, you may buy it from the bank. If owned, pay owner twice the rental to which they are otherwise",
                      "4 Advance to the nearest station. If unowned, you may buy it from the bank. If owned, pay owner twice the rental to which they are otherwise",
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

        drawn_card = self.cards_value[self.index]

        if drawn_card == 0:
            player[player_turn]["last pos"] = player[player_turn]["pos"]
            player[player_turn]["pos"] = 0
            player[player_turn]["$$$"] += 200

        elif drawn_card == 1:
            player[player_turn]["last pos"] = player[player_turn]["pos"]
            player[player_turn]["pos"] = 24

            if player[player_turn]["last pos"] > 24:
                player[player_turn]["$$$"] += 200

        elif drawn_card == 3:

            # this moves the player to waterworks if between electricity company and waterworks, otherwise moves to electricity company
            player[player_turn]["last pos"] = player[player_turn]["pos"]
            if player[player_turn]["pos"] >= 12 and player[player_turn]["pos"] < 28:
                player[player_turn]["pos"] = 28

            elif player[player_turn]["pos"] >= 28:
                player[player_turn]["pos"] = 12
                player[player_turn]["$$$"] += 200

            else:
                player[player_turn]["pos"] = 12

        elif drawn_card == 4:
            player[player_turn]["last pos"] = player[player_turn]["pos"]

            # rounds the player to the nearest station
            player[player_turn]["pos"] = math.ceil(player[player_turn]["pos"] / 10) * 10 + 5

            if player[player_turn]["pos"] >= 40:
                player[player_turn]["pos"] -= 40

            if player[player_turn]["pos"] == 5:
                player[player_turn]["$$$"] += 200

        elif drawn_card == 5:
            player[player_turn]["$$$"] += 50

        elif drawn_card == 6:
            player[player_turn]["has jail pass"] += 1

        elif drawn_card == 7:
            player[player_turn]["last pos"] = player[player_turn]["pos"]
            player[player_turn]["pos"] -= 3

        elif drawn_card == 8:
            player[player_turn]["last pos"] = player[player_turn]["pos"]
            player[player_turn]["pos"] = 40
            doubles_rolled = 0

        elif drawn_card == 9:
            player[player_turn]["$$$"] -= ((player[player_turn]["house total"] * 25) + (player[player_turn]["hotel total"] * 100))
            if player[player_turn]["$$$"] < 0:
                player_is_broke(player_turn, abs(player[player_turn]["$$$"]))

        elif drawn_card == 10:
            player[player_turn]["last pos"] = player[player_turn]["pos"]
            player[player_turn]["pos"] = 5

        elif drawn_card == 11:
            player[player_turn]["last pos"] = player[player_turn]["pos"]
            player[player_turn]["pos"] = 39

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

        update_player_position(player[player_turn]["pos"])
        update_player_position(player[player_turn]["last pos"], "remove")

chance = chance_cards_class()




############################## C.C. CARDS ##############################

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

        drawn_card = self.cards_value[self.index]
        if drawn_card == 0:
            player[player_turn]["last pos"] = player[player_turn]["pos"]
            player[player_turn]["pos"] = 0
            player[player_turn]["$$$"] += 200

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

community_chest = community_chest_cards_class()




############################## BOARD FUNCTIONALITY ##############################

def player_action(_pos):
    global current_action
    global current_screen
    global player

    # chance + C.C card actions
    if _pos in [7, 22, 36]:
        current_action = "chance"
        current_screen = "game_notice"
        print(chance.draw_card())

    elif _pos in [2, 17, 33]:
        current_action = "community chest"
        current_screen = "game_notice" 
        print(community_chest.draw_card())

    # income & super tax
    elif _pos == 4:
        player[player_turn]["$$$"] -= 200

    elif _pos == 38:
        player[player_turn]["$$$"] -= 100

    # go to jail space
    elif _pos == 30:
        player[player_turn]["last pos"] = player[player_turn]["pos"]
        player[player_turn]["pos"] = 40
        update_player_position(40)
        update_player_position(player[player_turn]["last pos"], "remove")

    elif _pos not in [0, 10, 20, 40]:
        _prop = return_number_from_pos[player[player_turn]["pos"]]
        _owner = property_data[_prop][3]
        if property_data[_prop][3] == 0:
            current_action = "property"
        else:
            if property_data[_prop][4] in [2, 3, 4, 5, 6]: # upgrade 1 is for colour sets
                player[player_turn]["$$$"] -= property_data[_prop][property_data[_prop][4] + 5]
                player[_owner]["$$$"] += property_data[_prop][property_data[_prop][4] + 5]
            elif property_data[_prop][4] == 1:

                player[player_turn]["$$$"] -= property_data[_prop][6] * 2
                player[_owner]["$$$"] += property_data[_prop][6] * 2

            elif property_data[_prop][4] == 0: 
                player[player_turn]["$$$"] -= property_data[_prop][6]
                player[_owner]["$$$"] += property_data[_prop][6]

            if player[player_turn]["$$$"] < 0:
                player_is_broke(player_turn, abs(player[player_turn]["$$$"]))
                   



############################## HOMESCREEN ##############################

def homescreen():
    if dev_mode == False:
        os.system("cls")

    # the 'current_screen' variable is used for user input, to make sure that the correct output happens
    global current_screen
    current_screen = "home_screen"

    # displaying the main menu
    print("")
    print(        "       ___  ___        _____     ____  ____     _____      _____      _____     ____     ___  ___"    )
    print(        "      /   \/   \      /     \    |    \|  |    /     \    |  _  \    /     \    |  |     \  \/  / │ coded by:")
    print(        "     /  /\  /\  \    |  (_)  |   |  \  \  |   |  (_)  |   |  ___/   |  (_)  |   |  |__    \_  _/  │ James E.")
    print(        "    /__/  \/  \__\    \_____/    |__|\____|    \_____/    |__|       \_____/    |_____|    |__|   │ 2024, 2025"    )
    print("")
    print("")
    saved_game = False
    try:
        x = open("save_file.james", encoding = "utf-8")
    except:
        pass
    else:
        x.close()
        saved_game = True
    for i in create_button_prompts(["Start game", "Continue", "Online"], [True, saved_game, True]):
        print(i)
    print("")
    print("    ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────")
    print("")
    print("    ", end = "")

homescreen()




############################## DICE ROLL ##############################

def dice_roll_animation():

    global current_die_rolling
    global dice_countdown
    global dice_value
    global player_turn
    global player
    global player_roll_itr
    global doubles_rolled

    dice_countdown -= 1

    if current_die_rolling == 1:
        print("┌───────────┐")
        print("    │           │")

        # this generates a random number between 1 and 6, and if it is the same as the previous dice roll, it will generate a new number
        # when the same dice face is shown twice in a row, it has a flickering effect or appears frozen, so this code prevents that
        x = randint(1, 6)
        while dice_value[1] == x:
                x = randint(1, 6)
        dice_value[1] = x

        # this is the dice rolling animation
        for i in range(3):
                print(f"    {dice_image_frame[dice_value[1]][i]}")

        print("    │           │")
        print("    └───────────┘")

    elif current_die_rolling == 2:
        print("┌───────────┐   ┌───────────┐")
        print("    │           │   │           │")

        x = randint(1, 6)
        while dice_value[2] == x:
            x = randint(1, 6)
        dice_value[2] = x

        # since the 'doubles' text is next to the dice and not under them, the calculations need to be performed while the lines are getting printed
        # it only is done when the dice are finished rolling, or otherwise it will appear while the dice are rolling
        # different text appears if doubles are rolled to escape jail
        if dice_value[2] == dice_value[1] and dice_countdown == 0:
            for i in range(3):
                print(f"    {dice_image_frame[dice_value[1]][i]}   {dice_image_frame[dice_value[2]][i]}", end="", )
                if player[player_turn]["pos"] != 40:
                    print(f"      {doubles_art[i]}")
                else:
                    print(f"      {[i]}")

            # this is the counter that makes sure that sends the player to jail if they roll 3 doubles
            doubles_rolled += 1
        else:
            for i in range(3):
                print(f"    {dice_image_frame[dice_value[1]][i]}   {dice_image_frame[dice_value[2]][i]}")

        print("    │           │   │           │")
        print("    └───────────┘   └───────────┘")
        print("")

    if dice_countdown == 0 and current_die_rolling == 1:
        current_die_rolling = 2
        dice_countdown = 7

    elif dice_countdown == 0:

        current_die_rolling = 3

        # this is updating the player's last position, so that the player's icon can be removed from the board
        player[player_turn]["last pos"] = player[player_turn]["pos"]

        if doubles_rolled == 3:

            # 40 is the value for jail
            player[player_turn]["pos"] = 40

            # makes sure that the player can't continue their turn once in jail
            doubles_rolled = 0

        elif player[player_turn]["pos"] != 40:

            # this is adding the dice roll's value to the player's position
            player[player_turn]["pos"] = (player[player_turn]["pos"] + dice_value[1] + dice_value[2])

            # this makes sure that the player's position is within the board's range (unless they got sent to jail)
            if player[player_turn]["pos"] >= 40:
                player[player_turn]["pos"] -= 40

        # this is if a player is attempting to escape jail
        elif dice_value[1] == dice_value[2]:

            # moving the player to just visiting
            player[player_turn]["pos"] = 10

        else:
            player[player_turn]["status"] = "jail"
            player[player_turn]["jail time"] += 1

        # giving the player some time to check their dice roll
        print("    === [Enter] to continue ===")
        print("\n    ", end = "")
        input()

        if dice_value[1] != dice_value[2]:
            doubles_rolled = 0
        player_roll_itr = iter(range(dice_value[1] + dice_value[2]))




############################## GAME SCREEN ##############################

def refresh_board():
    global current_screen
    global passed_go

    current_screen = "game"
    if dev_mode == False:
        os.system("cls")

    # some of the emojis don't display properly in VS, distorting the board, but looks normal in terminal
    print("")
    print("     ________________ __________ __________ __________ __________ __________ __________ __________ __________ __________ ________________")
    print("    |                |   $220   |  __()_   |   $220   |   $240   |   $200 __|   $260   |   $260   |   $150   |   $280   |   GO TO JAIL   |")
    print(f"    |  FREE PARKING  |          |  \__ \   |          |          |_()_()_| /|          |          |{player_display_location[28][1]}|          |     {player_display_location[30][1]} |")
    print(f"    |      ____      |{player_display_location[21][1]}|{player_display_location[22][1]}|{player_display_location[23][1]}|{player_display_location[24][1]}|\  ____ _)|{player_display_location[26][1]}|{player_display_location[27][1]}|    /\    |{player_display_location[29][1]}|  /¯¯¯¯\        |")
    print("    |     /[__]\     |          |  / /  /\ |          |          |/__)  /_\ |          |          |   /  \   |          | | (¯¯)/¯¯¯¯\   |")
    print(f"    |    |_ () _|    |          |  \ ‾-‾ / |  Fleet   |Trafalgar |{player_display_location[25][1]}|Leicester | Coventry |  |    |  |          |  \_¯¯| (¯¯) |  |")
    print("    |     U----U     |  Strand  |   ‾---‾  |  Street  |  Square  |Fenchurch |  Square  |  Street  |   \__/   |Piccadilly|    \/ \_¯¯_/   |")
    print(f"    |   {player_display_location[20][1]}   |🟥🟥🟥🟥🟥|  CHANCE  |🟥🟥🟥🟥🟥|🟥🟥🟥🟥🟥| Station  |🟨🟨🟨🟨🟨|🟨🟨🟨🟨🟨|WaterWorks|🟨🟨🟨🟨🟨|     O   \/     |")
    print("    |________________|🟥🟥🟥🟥🟥|__________|🟥🟥🟥🟥🟥|🟥🟥🟥🟥🟥|__________|🟨🟨🟨🟨🟨|🟨🟨🟨🟨🟨|__________|🟨🟨🟨🟨🟨|______O_O_______|")
    print("    |            🟧🟧|                                                                                                  |🟩🟩            |")
    print("    |Vine Street 🟧🟧|                                                                                                  |🟩🟩 Regent St. |")
    print(f"    |    $200    🟧🟧|     _____     __          ___    __   ___   ______     ______       {player_turn_display[player_turn][0]}                     |🟩🟩    $300    |")
    print(f"    | {player_display_location[19][1]} 🟧🟧|    |  _  \   |  |        /   \   \  \/  /  |  ____|   |  __  \      {player_turn_display[player_turn][1]}                     |🟩🟩 {player_display_location[31][1]} |")
    print(f"    |____________🟧🟧|    |  ___/   |  |__     /  ^  \   \_  _/   |  __|_    |      /      {player_turn_display[player_turn][2]}                     |🟩🟩____________|")
    print(f"    |Marlborough 🟧🟧|    |__|      |_____|   /__/¯\__\   |__|    |______|   |__|\__\      {player_turn_display[player_turn][3]}                     |🟩🟩            |")
    print("    |   Street   🟧🟧|                                                                                                  |🟩🟩 Oxford St. |")
    print("    |   $180     🟧🟧|      ____       _____      __                                                                    |🟩🟩    $300    |")
    print(f"    | {player_display_location[18][1]} 🟧🟧|     /  __|     /     \    |  |                                                                   |🟩🟩 {player_display_location[32][1]} |")
    print("    |____________🟧🟧|    |  |_  |   |  (_)  |   |__|                                                                   |🟩🟩____________|")
    print("    | COMUNITY CHEST |     \____/     \_____/    (__)                                                                   | COMUNITY CHEST |")
    print(f"    |   {player_display_location[17][1]}   |                                                                                                  |   {player_display_location[33][1]}   |")
    
    # this checks if the players owns any properties, and greys out the button otherwise
    button_states = [None, None, None, True]

    for i in range(28):
        if property_data[i][3] == player_turn:
            button_states[1] = True
            break

    # similar checks are performed for the other buttons
    if dice_rolled == False:
        button_states[0] = True
    else:
        button_states[0] = False

    if current_action == None and dice_rolled == True:
        button_states[2] = True
    else:
        button_states[2] = False

    button_list = create_button_prompts(["Roll dice","Properties", "End turn", "Save & Exit"], button_states)
    print(f"    |  💰  💵  🪙    |{button_list[0]}             |  💰  💵  🪙    |")
    print(f"    |💵  🪙  💰  💵  |{button_list[1]}             |💵  🪙  💰  💵  |")
    print(f"    |________________|{button_list[2]}             |________________|")
    print(f"    |            🟧🟧|{button_list[3]}             |🟩🟩            |")


    print("    | Bow Street 🟧🟧|                                                                                                  |🟩🟩  Bond St.  |")
    if current_action == "property" and player[player_turn]["$$$"] >= property_data[return_number_from_pos[player[player_turn]["pos"]]][2]:  
        print("    |   $180     🟧🟧|     ________________     ________________                                                        |🟩🟩    $320    |")
        print(f"    | {player_display_location[16][1]} 🟧🟧|    |                |   |                |                                                       |🟩🟩 {player_display_location[34][1]} |")
        print("    |____________🟧🟧|    | [B]uy property |   |   [A]uction    |                                                       |🟩🟩____________|")
        print("    |$ |\⁔   Mar'bone|    |________________|   |________________|                                                       | Lv'rpool|∖↙() $|")
    
    elif current_action == "property":  
        print("    |   $180     🟧🟧|       __  __  __  __     ________________                                                        |🟩🟩    $320    |")
        print(f"    | {player_display_location[16][1]} 🟧🟧|    |                    |                |                                                       |🟩🟩 {player_display_location[34][1]} |")
        print("    |____________🟧🟧|      [B]uy property |   |   [A]uction    |                                                       |🟩🟩____________|")
        print("    |$ |\⁔   Mar'bone|    |  __  __  __  __    |________________|                                                       | Lv'rpool|∖↙() $|")

    else:
        print("    |   $180     🟧🟧|                                                                                                  |🟩🟩    $320    |")
        print(f"    | {player_display_location[16][1]} 🟧🟧|                                                                                                  |🟩🟩 {player_display_location[34][1]} |")
        print("    |____________🟧🟧|                                                                                                  |🟩🟩____________|")
        print("    |$ |\⁔   Mar'bone|                                                                                                  | Lv'rpool|∖↙() $|")
    print("    |2 ¯| |◁ Station |                                                                                                  | Station |‿ |  2|")
    print(f"    |0 () |{player_display_location[15][1]}|                                                                                                  |{player_display_location[35][1]}| () 0|")
    print("    |0  | ⁀|         |                                                                                                  |         ▷|‿|__0|")
    print("    |__()↗∖|_________|                                                                                                  |_____________\|_|")
    print("    |Northumb'nd 🟪🟪|                                                                                                  |      _  CHANCE |")
    print("    |   Avenue   🟪🟪|                                                                                                  |    /‾_‾\|‾|    |")
    print("    |    $160    🟪🟪|                                                                                                  |   | | \_  | () |")
    print(f"    | {player_display_location[14][1]} 🟪🟪|                                                                                                  |    \_\{player_display_location[36][1]}|")
    print("    |____________🟪🟪|                                                                                                  |________________|")
    print("    |            🟪🟪|                                                                                                  |🟦🟦            |")
    print("    | Whitehall  🟪🟪|                                                                                                  |🟦🟦 Park Lane  |")    

    extra_space = ""

    # this checks if 4 players are playing, and displays the players' money descending from here. The first player will always be at the top as it is based on "players_playing"
    # it will always do 2 players, but if "players_playing - 2" provides a valid player (1, or 2) then it displays that, and another check at the top if there are four players ("players_playing - 3")
    # note that the "player" dictionary starts from 1
    if players_playing - 3 > 0:
        extra_space = ""
        for i in range(12 - len(str(player[players_playing - 3]["$$$"]))):
            extra_space += " "

        print(f"    |   $140     🟪🟪|                                                                                  player {players_playing - 3} | {player[players_playing - 3]['char']}   |🟦🟦    $350    |")
        print(f"    | {player_display_location[13][1]} 🟪🟪|                                                                                  ${player[players_playing - 3]['$$$']}{extra_space}   |🟦🟦 {player_display_location[37][1]} |")
    else:
        print(f"    |   $140     🟪🟪|                                                                                                  |🟦🟦    $350    |")
        print(f"    | {player_display_location[13][1]} 🟪🟪|                                                                                                  |🟦🟦 {player_display_location[37][1]} |")
    print("    |____________🟪🟪|                                                                                                  |🟦🟦____________|")


    if players_playing - 2 > 0:
        extra_space = ""
        for i in range(12 - len(str(player[players_playing - 2]["$$$"]))):
            extra_space += " "

        print(f"    | Electric Co.   |                                                                                  player {players_playing - 2} | {player[players_playing - 2]['char']}   | ∖  ⁄ SUPER TAX |")
        print(f"    | $150       |\  |                                                                                  ${player[players_playing - 2]['$$$']}{extra_space}   |- 💎 -   - $100 |")
    else:
        print(f"    | Electric Co.   |                                                                                                  | ∖  ⁄ SUPER TAX |")
        print(f"    | $150       |\  |                                                                                                  |- 💎 -   - $100 |")

    print(f"    |          __| \ |                                                                                                  |/¯¯¯¯\{player_display_location[38][1]}|")
    
    extra_space = ""
    for i in range(12 - len(str(player[players_playing - 1]["$$$"]))):
        extra_space += " "

    print(f"    |{player_display_location[12][1]}\ |¯¯ |                                                                                  player {players_playing - 1} | {player[players_playing - 1]['char']}   | (⁐⁐) |         |")   
    print(f"    |___________\|___|                                                                                  ${player[players_playing - 1]['$$$']}{extra_space}   |\____/__________|")
    

    print(f"    |            🟪🟪|                                                                                                  |🟦🟦            |")


    extra_space = ""
    for i in range(12 - len(str(player[players_playing]["$$$"]))):
        extra_space += " "

    print(f"    | Pall Mall  🟪🟪|                                                                                  player {players_playing} | {player[players_playing]['char']}   |🟦🟦   Mayfair  |")
    print(f"    |   $140     🟪🟪|                                                                                  ${player[players_playing]['$$$']}{extra_space}   |🟦🟦    $400    |")

    print(f"    | {player_display_location[11][1]} 🟪🟪|                                                                                                  |🟦🟦 {player_display_location[39][1]} |")
    print("    |____________🟪🟪|__________ __________ __________ __________ __________ __________ __________ __________ __________|🟦🟦____________|")
    print("    |      | ║ ║ ║ ║ |🟦🟦🟦🟦🟦|🟦🟦🟦🟦🟦|  CHANCE  |🟦🟦🟦🟦🟦|  King's  |          |🟫🟫🟫🟫🟫| COMUNITY |🟫🟫🟫🟫🟫|  ____    ____  |")
    print("    |   J  | J A I L |🟦🟦🟦🟦🟦|🟦🟦🟦🟦🟦|  _---_   |🟦🟦🟦🟦🟦|  Cross   |  INCOME  |🟫🟫🟫🟫🟫|   CHEST  |🟫🟫🟫🟫🟫| /  __|  /    \ |")
    print(f"    |   U  | ║ ║ ║ ║ |Pent'ville|  Euston  | / _-_ \  |The Angel |{player_display_location[5][1]}|   TAX    |whitechp'l|{player_display_location[2][1]}| Old Kent ||  |_ ‾||  ()  ||")
    print(f"    |   S  |{player_display_location[40][1]}|   Road   |   Road   | \/  / /  |Islington | \¯/___(¯/|          |   Road   |          |   Road   | \____/  \____/ |")
    print(f"    |   T  |_║_║_║_║_|          |          |   / /_   |          |( _______\|    🔷    |          |🪙  💰  💵|          |{player_display_location[0][1]}____  |")
    print(f"    |   {player_display_location[10][1]}   |{player_display_location[9][1]}|{player_display_location[8][1]}|   \___\  |{player_display_location[6][1]}|/_| () () |{player_display_location[4][1]}|{player_display_location[3][1]}|  💵  💰  |{player_display_location[1][1]}|  /|-----/   /  |")
    print(f"    |    VISITING    |   $120   |   $100   |{player_display_location[7][1]}|   $100   |   $200   | PAY $200 |   $ 60   |💰  🪙  💵|   $ 60   |  \|-----\___\  |")
    print("    |________________|__________|__________|__________|__________|__________|__________|__________|__________|__________|________________|")
    print()

    if dev_mode == True:
        print("    === devmode commands ===")
        print()
        print("    \"gotojail\"")
        print("    \"setplayerpos\"")
        print("    \"editplayerdict\"")
        print("    \"showplayerdict\"")
        print("    \"setdiceroll\"")
        print("    \"bankruptcy\"")
        print("    \"propertybid\"")
        print("    \"showproplist\"")
        print("    \"showchangedprops\"")
        print("    \"setplayerprops\"")
        print()
        
    if passed_go == True:
        for i in range(3):
            print(f"    {passed_go_art[i]}")
        passed_go = False

    print("    ", end="")




############################## NEW GAME SETUP ##############################

def new_game():
    global player_turn
    global current_screen
    global current_die_rolling
    global player_display_location
    global doubles_rolled
    global passed_go
    global dice_rolled
    global current_action
    global start_time

    dice_rolled = False
    doubles_rolled = 0
    current_die_rolling = 0
    player_turn = 1
    current_screen = "game_notice"
    passed_go = False
    current_action = None
         
    # updating the board so all players are on start
    for i in range(players_playing):
        player_display_location[0][i + 3] = True

    player_display_location[0][7] = players_playing - 1
    update_player_position(0)

    start_time = time.time()

    display_game_notice()

def display_game_notice():
    global current_screen
    current_screen = "game_notice"

    if dev_mode == False:
        os.system("cls")

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




############################## PLAYER SELECT ##############################

def new_game_select():
    if dev_mode == False:
        os.system("cls")

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

        if player_turn == int(players_playing) + 1:

            # 'player_turn' is set to 0 so that nothing else is displayed
            player_turn = 0
            name_detection = False
            new_game()

        elif player_turn == 1:
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




############################## CONTINUE SAVED GAME ##############################

def read_save(_file, _encoding = "utf-8"):
    testfile = open(_file, encoding = _encoding)

    # game version will get overwritten, so a copy is recorded to compare with save version to make sure they're the same
    true_game_version = game_version

    # each line contains a single variable, except the warning at the top, 
    # but it doesn't contain an "=" so the rest of the code is not triggered.
    for _line in testfile:
        _var = ""

        # this goes through the line and adds it to the variable name until the "=", then the rest is converted to a value
        for _count in range(len(_line.strip())):
            if _line[_count + 1] != "=":
                _var += _line[_count]
            else: 
                
                # the only exception would be if it is an iterator ("i[1, 2, 3, 4]"), so the extra character is skipped
                try:
                    _value = literal_eval(_line[_count + 3:].strip())
                except:
                    _value = iter(literal_eval(_line[_count + 4:].strip()))
                globals()[_var] = _value
                break      
   
    # this subtracts the time played on the save from the start time so the end-screen calculations reflect the extra time played
    start_time = time.time() - time_played

    if game_version != true_game_version:
        raise Exception("=== save is not the same version as game")




############################## SAVING VARIABLES TO SAVE FILE ##############################

def save_game_to_file(*variables):
    try:
        save_file = open("save_file.james", "w", encoding="utf-8")
    except:
        save_file = open("save_file.james", "x", encoding="utf-8")

    save_file.write("Wonder what happens if you mess with the save? stuff around and find out\n\n")

    for var in variables:
        var_type = type(eval(var)).__name__

        # strings have quotation marks added as otherwise determining type would be difficult
        if var_type == "str":
            save_file.write(f"{var} = \"{eval(var)}\"\n") 
        elif "iterator" in var_type:
            _list = []
            for i in eval(var):
                _list.append(i)
            save_file.write(f"{var} = i{_list}\n")
        else:
            save_file.write(f"{var} = {eval(var)}\n")

    # since only modified properties are saved, they have their own check
    for i in range(28):
        if property_data[i][3] != 0:
            save_file.write(f"property_data[{i}] = {property_data[i]}\n")

    # the time is rounded to the nearest second 
    save_file.write(f"time_played = {str(round(time.time() - start_time))}\n")

    save_file.close()




############################## INPUT DETECTION ##############################

while True:

    # the reason for this check is that detecting user input pauses the program, and so I disable it for the animations
    if current_die_rolling == 0:
        user_input = input()
        input_confirmation = True
    else:
        if current_die_rolling != 3:
             sleep(0.25)
             refresh_board()
             dice_roll_animation()

        if current_die_rolling == 3:

            # the code is bypassed if the player goes to jail, and the character is instantly teleported
            if player[player_turn]["pos"] == 40:
                update_player_position(40, "add")
                update_player_position(player[player_turn]["last pos"], "remove")
                current_die_rolling = 0
            else:

                # this code will try to move the player's icon forward one space
                try:
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
                    sleep(0.5)
                    refresh_board()

                # the only exception would be once the iterator has ran out...
                # ...so the player is at the correct spot and the board will stop being refreshed
                except:
                        
                    # this can only happen once the player passes go and their position is re-counted from zero
                    # done before player action since chance cards can move you back three spaces, making pos < last pos
                    if player[player_turn]["pos"] < player[player_turn]["last pos"]:
                        player[player_turn]["$$$"] += 200
                        passed_go = True

                    player_action(player[player_turn]["pos"])
                   
                    current_die_rolling = 0
                    if doubles_rolled in [0, 3]:
                        dice_rolled = True

    # home screen commands
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

            # this is in dedication to Nick Tho, who always uses his phone with night-shift enabled at the maximum intensity
            # changes the background to yellow
            os.system('echo -e "\033[43;37m"')
            homescreen()

            print("=== Nick Tho always uses night-shift on maxium intensity, I'm not trying to be racist ===\n\n")
            for i in create_button_prompts(["I'm offended", "Makes sense"]):
                print(i)
            current_action = "nicktho"

        elif user_input in ["i", "I"] and current_action == "nicktho":
            print("\n    === get over it. ===\n\n    ", end = "")

        elif user_input in ["m", "M"] and current_action == "nicktho":
            print("\n    === wow thank you for understanding and not overreacting. ===\n\n    ", end = "")

        else:
            print("    === command not recognised === ")
            print("\n    ", end = "")

    # player select commands
    elif current_screen == "player_select" and input_confirmation == True:
        if user_input in ["2", "3", "4"]:

            players_playing = int(user_input)
            player_turn = 1
            name_detection = True

            player = {}

            for i in range(players_playing):

                # the reason for "[i + 1]" is so that the players start at 1, not 0
                player[i + 1] = {
                    "char": "",
                    "$$$": 1500,
                    "pos": 0,

                    # this is so that the player's icon can be removed from the board
                    "last pos": 0,
                    
                    # not a bool since the player could get 2 get out of jail free cards
                    "has jail pass": 0,
                    "jail time": 0,
                    "house total": 0,
                    "hotel total": 0,
                    "status": "playing",

                    # seperate to the game version for online games
                    "version": game_version
                    }
            new_game_select()

        elif user_input in ["b", "B"]:
            name_detection == False
            players_playing = 0
            homescreen()

        # recording entered names
        elif name_detection == True:

            # it is important to know if the character being inputted is one or two characters and act accordingly...
            #  ...as having the width be too long or short distorts the board
            def char_width(char):
                width = unicodedata.east_asian_width(char)

                # this makes sure that only the full/double width info is returned as there are a few more widths (they aren't necessary for this program)
                return width in ("F", "W")

            # this counts the character width inputted, enforces 2 characters width
            x = 0
            for i in user_input:
                if char_width(i) == True:
                    x += 2
                else:
                    x += 1
            
            if user_input in ["  ", r"\\"]:
                print("\n    === nice try. ===\n\n    ", end = "")

            if x == 2:

                player[player_turn]["char"] = user_input
                player_turn += 1
                new_game_select()

            elif x > 2:
                print("    === icon too large, try a different icon (eg: '😊' or 'JE') ===")
                print()
                print("    ", end="")

            else:
                print("    === icon too small, try a different icon (eg: '😊' or 'JE') ===")
                print()
                print("    ", end="")
        else:
            print("    === command not recognised === ")
            print("\n    ", end = "")

    # player notice acknowledgment
    elif current_screen == "game_notice" and input_confirmation == True:
        refresh_board()
        
        if current_action == "chance":
            current_action = None
            chance.perform_action()
        elif current_action == "community chest":
            current_action = None
            community_chest.perform_action()

    elif current_screen == "save_notice" and input_confirmation == True:
        homescreen()

    # game commands (the 'user_input != ""' is for when the dice are rolling, since the input is skipped and reset to nothing)
    elif current_screen == "game" and input_confirmation == True:
        if user_input in ["r", "R"]:
            if dice_rolled == False:
                dice_countdown = 7

                # 0 = dice not rolling; 1 = first dice rolling; 2 = second dice rolling; 3 = updating player position
                current_die_rolling = 1
                refresh_board()
            else:
                print("    === you've already rolled ===")
                print()
                print("    ",end = "")

        elif user_input in ["e", "E"]:
            if dice_rolled == False:
                print("    === roll dice first ===")
                print()
                print("    ", end = "")

            else: 
                player_turn += 1
                dice_rolled = False
                doubles_rolled = 0
                while player[player_turn]["status"] == "bankrupt":
                    player_turn += 1
                    if player_turn > players_playing:
                        player_turn = 1
                   
                refresh_board()
                
        elif user_input in ["s", "S"]:

            save_game_to_file("game_version", "players_playing", "player_turn",
                              "doubles_rolled", "dev_mode", "dice_rolled", "dice_rolled",
                              "current_action", "player", "chance.cards_value", 
                              "chance.index"," community_chest.cards_value", "community_chest.index")
            current_screen = "save_notice"
            print("\n    === game saved. [Enter] to return to the main menu ===\n\n    ", end = "")

        elif user_input in ["b", "B"] and current_action == "property":
            player[player_turn]["$$$"] -= property_data[return_number_from_pos[player[player_turn]["pos"]]][2]
            property_data[return_number_from_pos[player[player_turn]["pos"]]][3]  = player_turn
            player[player_turn]["total properties"] += 1

            if property_data[return_number_from_pos[player[player_turn]["pos"]]][1] == "utility":
                player[player_turn]["utilities owned"] += 1

            elif property_data[return_number_from_pos[player[player_turn]["pos"]]][1] == "station":
                player[player_turn]["stations owned"] += 1


            current_action = None

        elif user_input in ["a", "A"] and current_action == "property":

            # since bidding will require 'player_turn' to change, this stores the proper player turn
            true_player_turn = player_turn
            bid_number = 0

            # making a dictionary to store players' bids, and making sure that only numbers are inputted
            player_bids = {1 : 0, 2 : 0, 3 : 0, 4 : 0}
            skipped_bids = 0

            auctioned_property = return_number_from_pos[player[player_turn]["pos"]]

            display_property(auctioned_property, is_auction = True)

        elif user_input == "gotojail" and dev_mode == True:

            player[player_turn]["last pos"] = player[player_turn]["pos"]
            player[player_turn]["pos"] = 40

            update_player_position(40)
            update_player_position(player[player_turn]["last pos"], "remove")

            player_turn += 1
            if player_turn > players_playing:
                player_turn = 1

            refresh_board()

        elif user_input == "setplayerpos" and dev_mode == True:
            x = input("    === which player ([1/2/3/4]): ")
            xx = input("    === set pos (!!!warning: not entering a number will cause funky stuff to happen to the code!!!): ")
            player[int(x)]["last pos"] = player[int(x)]["pos"]
            player[int(x)]["pos"] = int(xx)
            update_player_position(int(xx))
            update_player_position(player[int(x)]["last pos"], "remove")
            refresh_board()
            player_action(int(xx))

        elif user_input == "showplayerdict" and dev_mode == True:
            for i in player:
                print(f"{i}: {player[i]}")

        elif user_input == "setdiceroll" and dev_mode == True:
            x = input("    === first dice value: ")
            xx = input("    === second dice value: ")
            dice_value[1] = int(x)
            dice_value[2] = int(xx)
            current_die_rolling = 3
            dice_countdown = 1
            dice_roll_animation()
           
        elif user_input == "bankruptcy" and dev_mode == True:
            x = input("    === which player: ")
            xx = input("    === debt: ")
            player_is_broke(int(x), int(xx))

        elif user_input ==  "editplayerdict" and dev_mode == True:
            print("    === Please edit position using the 'setplayerpos' and 'gotojail' command ===")
            x = input("    === which player: ")
            xx = input("    === which key: ")
            xxx = input("    === what value: ")
            try:
                player[int(x)][xx] = int(xxx)
            except:
                player[int(x)][xx] = xxx

        elif user_input == "propertybid" and dev_mode == True:
            auctioned_property = int(input("    === enter property number: "))
            true_player_turn = player_turn
            bid_number = 0

            # making a dictionary to store players' bids, and making sure that only numbers are inputted
            player_bids = {1 : 0, 2 : 0, 3 : 0, 4 : 0}
            skipped_bids = 0
            display_property(auctioned_property, is_auction = True)

        elif user_input == "showproplist" and dev_mode == True:
            for i in property_data:
                print(i)

        elif user_input == "showchangedprops" and dev_mode == True:
            for i in property_data:
                if i[3] != 0:
                    print(i)

        elif user_input == "setplayerprops" and dev_mode == True:
            x = int(input("    === what player: "))
            xx = input("    === what property (commands: 'all', 'done'): ")
            while xx != "done":
                if xx == "all":
                    for i in range(28):
                        property_data[i][3] = x
                else:
                    property_data[int(xx)][3] = i
                xx = input("    === what property (commands: 'all', 'done'): ") 
            refresh_board()

        else:
            print("    === command not recognised ===")
            print("\n    ", end = "")

    elif current_screen == "bidding" and input_confirmation == True:

        try:
            int(user_input)
        except:
            if user_input in ["s", "S"]:
                skipped_bids += 1
                if skipped_bids == players_playing - 1 and bid_number >= bid_number - 1:
                    display_property(auctioned_property, is_auction = "finished")

                    player[player_turn]["$$$"] -= property_data[auctioned_property][2]
                    refresh_board()

            else:
                print("    === command not recognised. Please enter a number or [S]kip ===")
                print("\n    ", end = "")
        else:
            if int(user_input) > player_bids[player_turn]:
                player_bids[player_turn] = int(user_input)
                player_turn += 1
                bid_number += 1
                skipped_bids = 0

                # Sorts the dictionary based on values (created with GitHub Copilot)
                player_bids = dict(sorted(player_bids.items(), key = lambda item: item[1], reverse = True))

                # creates a list of the order of bids, so i can refer to the dictionary sequentially, instead of by player number
                bid_order = []
                for i in player_bids.keys():
                    bid_order.append(i)


                if player_turn > players_playing:
                    player_turn = 1

                if bid_number > players_playing:
                    bid_number = players_playing


                display_property(auctioned_property, is_auction = True)
            else:
                print(f"\n    === player {player_turn} either raise your bid or [S]kip ===")
                print("\n    ", end = "")

    # bankruptcy screen commands
    elif current_screen == "raise_money_screen" and input_confirmation == True:

        # makes sure that the user entered a number, than makes sure that the player owns that property
        try:
            x = int(user_input)
        except:
            print("    === command not recognised. please enter the number to the left of the desired property ===")
            print("\n    ", end = "")
        else:
            if property_data[int(return_number_from_pos[user_input])][3] == player[player_turn]["pos"]:
                display_property(int(user_input))
            else:
                print("    === you don't own that property. please enter the number to the left of the desired property ===")

    elif current_screen == "bankruptcy" and input_confirmation == True:
        _count = 0

        # this is checking how many players remain after a bankruptcy
        for i in range(players_playing):
            if player[i + 1]["status"] == "playing":
               _count += 1

        # if only one player remains, then the game finished screen is displayed
        if _count == 1:

            # total amount of seconds played
            _total = round(time.time() - start_time)

            # bit of simple math that converts a integer of seconds played into Xh Ym Zs format
            _hours = math.floor(_total/3600)
            _remainder = _total % 3600
            _minutes = math.floor(_remainder / 60)
            _seconds = _remainder % 60

            _length = len(str(_hours)) + len(str(_minutes)) + len(str(_seconds))

            # see 'display_property' for comments (this just centers the code)
            extra_space = ""
            for ii in range(math.floor((6 - _length) / 2)):
                extra_space += " "

            extra_extra_space = ""
            if _length % 2 == 1:
                extra_extra_space = " "

            if dev_mode == False:
                os.system('cls')
            print("    ╔════════════════════════════════════════════════════════════════╗")
            print("    ║                                                                ║")
            print("    ║                       CONGRADULATIONS :)                       ║")
            print("    ║                                                                ║")
            print("    ║                     You have won the game!                     ║")
            print(f"    ║{extra_space}                 you spent {_hours}h {_minutes}m {_seconds}s to do it                 {extra_extra_space}{extra_space}║")
            print("    ║                                                                ║")
            print("    ║           was this really the best use of your time?           ║")
            print("    ║                                                                ║")
            print("    ╚════════════════════════════════════════════════════════════════╝")
            print("\n    ", end = "")
            sys.exit()

    input_confirmation = False
    user_input = ""
