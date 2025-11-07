"""tools useful in multiple circumstances"""

from time import time
from os import system, name

import state
from better_iterator import better_dict, better_iter

__required__ = ["game.bankruptcy", "online.send_data"]
bankruptcy = None
send_data = None


class ReturnException(BaseException):
    """used to exit input logic during online games from sub functions,
    should only be caught at the highest level and then suppressed"""
    def __str__(self):
        """this error should not be displayed to the user.
        a function wanted to exit input logic but this error wasn't caught"""


def sleep(_time: int):
    """delays thread for inputted milliseconds"""
    start = time()
    _time = _time / 1000
    while time() - start < _time: pass


def clear_screen(sys: str | None = name):
    """do you really need a docstring for this?"""

    # developer mode disables screen clearing
    if state.dev_mode:  return

    if   sys == "nt"   : system("cls")
    elif sys == "posix": system("clear")
    else: raise Exception("bro what are you running this on??!!")


# I'm very proud of this use of typing hints
def create_prompts(
        prompts: list[str],
        prompt_state: list[bool] | None =  "default",
        spacing: list[int] | None = "default"
    ) -> list[str]:
    """
    creates ASCII art of buttons using given prompts.
    prompts should be a maximum of 12 characters long per button.

    prompt_state defaults to True, use False for dashed outline
    the default spacing is 4 spaces front, then 3 between buttons

    a blank prompt ('') leaves the space blank without an outline
    
    ╭───┬──────────────╮ <- True   ╭╴ ╶┬╴ ╶╴ ╶╴ ╶╴ ╶╴ ╮
    │ E │ example      │             U   unavailable
    ╰───┴──────────────╯  False -> ╰╴ ╶┴╴ ╶╴ ╶╴ ╶╴ ╶╴ ╯
    """

    button_list = ["", "", ""] # output list for the art
    num = len(prompts)

    # if "prompt_state" or "spacing" is left to default,
    # its size is dependent on the amount of prompts
    if prompt_state == "default":
        prompt_state = [True for i in range(num)]

    if spacing == "default":
        spacing = [3 for i in range(num)]
        spacing[0] = 4

    for i in range(num):
        for ii in range(spacing[i]):
            button_list[0] += " "
            button_list[1] += " "
            button_list[2] += " "

        # blank inputs leave space blank
        if prompts[i] == "":
            button_list[0] += "                    "
            button_list[1] += "                    "
            button_list[2] += "                    "
            continue

        extra_space = ""
        x = prompts[i][0].upper()

        # ensures buttons are the same length regardless of prompt length
        for ii in range(12 - len(prompts[i])): extra_space += " "

        if prompt_state[i] == True:
            button_list[0] += "╭───┬──────────────╮"
            button_list[1] += f"│ {x} │ {prompts[i]}{extra_space} │"
            button_list[2] += "╰───┴──────────────╯"
        else:
            button_list[0] += "╭╴ ╶┬╴ ╶╴ ╶╴ ╶╴ ╶╴ ╮"
            button_list[1] += f"  {x}   {prompts[i]}{extra_space}  "
            button_list[2] += "╰╴ ╶┴╴ ╶╴ ╶╴ ╶╴ ╶╴ ╯"
  
    return button_list


def update_player_position(_pos: int, _action = "add" or "remove"):
    """
    updates player_display where player is shown.
    action is either 'add' or 'remove', and the positions are 0-27

    'add' displays a player at the space, even if their position is
    something else, 'remove' updates a space properly
    """

    player_itr = better_iter(range(state.players_playing), start_index=-1)
    _ = None

    # records current player locations
    players_pos = []
    for item in state.player.items():
        players_pos.append(item[1]["pos"])

    # overrides player space with current space,
    # to ensure player is displayed spaces before actual location
    if _action == "add": players_pos[state.player_turn - 1] = _pos

    layout = better_dict({
        2: {
            0: "    \x1b[33m└┘\x1b[0m    ",
            1: " p \x1b[33m└┘\x1b[0m    ",
            2: " p \x1b[33m└┘\x1b[0m p ",
            3: "pp\x1b[33m└┘\x1b[0m p ",
            4: "pp\x1b[33m└┘\x1b[0mpp"
        },

        (7, 22): {
            0: "    \x1b[38;2;255;103;35m()\x1b[0m    ",
            1: " p \x1b[38;2;255;103;35m()\x1b[0m    ",
            2: " p \x1b[38;2;255;103;35m()\x1b[0m p ",
            3: "pp\x1b[38;2;255;103;35m()\x1b[0m p ",
            4: "pp\x1b[38;2;255;103;35m()\x1b[0mpp"
        },

        (17, 33, 38): {
            0: "         ",
            1: "   p    ",
            2: " p  p ",
            3: "p p p ",
            4: "pp pp"
        },

        28: {
            0: "    \x1b[94m/\\\x1b[0m    ",
            1: " p \x1b[94m/\\\x1b[0m    ",
            2: " p \x1b[94m/\\\x1b[0m p ",
            3: "pp\x1b[94m/\\\x1b[0m p ",
            4: "pp\x1b[94m/\\\x1b[0mpp",
        },

        36: {
            0: "    \x1b[38;2;245;77;201m__\x1b[0m    ",
            1: " p \x1b[38;2;245;77;201m__\x1b[0m    ",
            2: " p \x1b[38;2;245;77;201m__\x1b[0m p ",
            3: "pp\x1b[38;2;245;77;201m__\x1b[0m p ",
            4: "pp\x1b[38;2;245;77;201m__\x1b[0mpp"
        },

        40: {0: " ║ ║ ║ ║ " , 1: " ║ p║ ║ " , 2: " p║ ║p " , 3: " pp║p " , 4: "pp pp"}
    },

    {0: "          ", 1: "    p    ", 2: "  p  p  ", 3: " p p p ", 4: "p pp p"},
    )

    order = layout[_pos][players_pos.count(_pos)]

    string = ""

    # assembles string
    for char in order:
        if char != "p":
            string += char
        else:
            i = next(player_itr)
                
            # seeks the next player at that location
            while players_pos[i] != _pos: i = next(player_itr)

            string += state.player[i + 1]["char"]

    # updates display
    state.player_display[_pos] = string


class parent_class:
    """all other classes that print to terminal should inherit this"""
    def input_management(self, user_input):
        """determines what action to perform with user input"""
        if not state.online_config.is_trade_request:
            return

        # if the player accepts an online trade request
        if user_input in ["a", "A"]:
            send_data(f"whisper:{state.online_config.trade_requester}:accept trade")
            state.trade_screen.player_1["player"] = int(state.online_config.trade_requester)
            state.trade_screen.player_2["player"] = state.online_config.player_num
            state.trade_screen.curr_player = state.trade_screen.player_2
            state.trade_screen.is_trade = True

            state.trade_screen.display_trade_window()
        else:
            send_data(f"whisper:{state.online_config.trade_requester}:decline trade")
            if user_input not in ["d", "D"]:
                print("\n    === I'll take that as no ===\n\n    ",end="")
            else:
                print("\n === trade declined ===\n\n    ", end="")

        state.online_config.trade_requester = None
        state.online_config.is_trade_request = False
        raise ReturnException

    def online_management(self, command):
        """executes relevant logic for an online command"""

    def disconnect_management(self, quitter):
        """handles an online player leaving mid-game
        """ 
        print(f"=== player {quitter} ({state.online_config.joined_clients[quitter - 1][0]}) has left the game! ===\n\n    ", end ="")

        bankruptcy(quitter, "disconnect")

    def __call__(self): pass 
    def __init_subclass__(self): self.__name = None
    def __eq__(self, value): return self.__name__ == value

    @property
    def __name__(self):
        # if name does not exist, it is found in globals
        if not self.__name:
            for item in state.__dict__.items():
                if id(item[1]) == id(self):
                    self.__name = item[0]
                    break
                
        return self.__name
    

def read_save(
        _file: str | None = "save_file.james",
        _encoding: str | None = "utf-8"):
    """reads save_file.james as python code"""
    savefile = open(_file, encoding = _encoding)

    # totally secure 😎
    for _line in savefile:
        exec(_line, globals())
   
    # this subtracts the time played on the save from the start time,
    # so the end-screen calculations reflect the extra time played

    state.start_time = time() - time_played # type: ignore

    for item in state.player.values():
        update_player_position(item["pos"])


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
        if state.property_data[i]["owner"] != None:
            save_file.write(f"variables.property_data[{i}].update({{'owner': {state.property_data[i]['owner']},"
                            f"'upgrade state': {state.property_data[i]['upgrade state']}}})\n")

    # the time is rounded to the nearest second
    save_file.write(f"time_played = {str(round(time() - state.start_time))}\n")

    save_file.close()


def repair_property_states(properties: list[int] | None = None):
    """determines if given properties are in a colour set, adjusts
    upgrade state to match if there are inconsistencies.
    resets properties with no owners.

    if argument is provided, only given properties will be checked,
    otherwise, all properties in state.property_data are checked
    
    doesn't change upgraded or mortgaged properties (states -1, 3-8)"""

    # goes through entirety of property data
    if properties == None:
        properties = state.property_data
    else:

        # gets the indexes and retrieve associated properties
        properties.sort()
        buffer = properties
        properties = []
        for index in buffer:
            properties.append(state.property_data[index])

    colour_set = []
    owners = []
    for prop in properties:

        # unpurchased/returned to bank properties should be upgraded
        if prop["owner"] == None:
            prop["upgrade state"] = 0

        # owned properties should NOT have unpurchased value (0)
        elif prop["upgrade state"] == 0:
            prop["upgrade state"] = 1

        #  stations and utilities don't require colour set logic
        if prop["type"] != "property":
            continue

        colour_set.append(prop)
        owners.append(prop["owner"])
        
        # brown and dark blue only have two properties in the colour set
        # this repeats the loop until a full colour set is in the list
        if not (len(colour_set) == 2 and prop["colour set"] in [0, 7]) and not len(colour_set) == 3:
            continue

        # if the list contains multiple different values
        # (if multiple people own properties in a colour set)
        if owners.count(owners[0]) != len(owners):

            # all purchased properties are set to default, unless mortgaged
            for prop in colour_set:
                if prop["upgrade state"] == 2 and prop["owner"] != None:
                    prop["upgrade state"] = 1

        # if none of the properties are owned, skips following
        elif owners[0] != None:
            for prop in colour_set:
                if prop["upgrade state"] == 1:
                    prop["upgrade state"] = 2

        # after logic has been performed, both lists are cleared and
        # loop repeats until all properties have been tested
        colour_set.clear()
        owners.clear()