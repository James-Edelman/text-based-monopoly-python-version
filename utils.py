"""tools useful in multiple circumstances"""

from time import time
from os import system, name

import state
from better_iterator import better_iter

__required__ = ["game.bankruptcy"]
bankruptcy = None

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


def update_player_position(_pos: int, _action = "add" or "remove"):
    """
    updates the displayed segments where player is shown.
    action is either 'add' or 'remove', and the positions are 0-27
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

    layout = {
        _ : {0: "          ", 1: "    p    ", 2: "  p  p  ", 3: " p p p ", 4: "p pp p"},
        7 : {0: "    ()    ", 1: " p ()    ", 2: " p () p ", 3: "pp() p ", 4: "pp()pp"},
        22: {0: "    / /   ", 1: " p / /   ", 2: " p / /p ", 3: "pp/ /p ", 4: "pp/ pp"},
        36: {0: "  \\_|    ", 1: r"  \_| p ", 2: r"p\_| p ", 3: r"p\_|pp", 4: "ppp|p" },
        40: {0: " ║ ║ ║ ║ " , 1: " ║ p║ ║ " , 2: " p║ ║p " , 3: " pp║p " , 4: "pp pp" }
    }

    # determines what layout to retrieve
    if state.player_display[_pos][1] == True:
        order = layout[_][players_pos.count(_pos)]
    else:
        order =layout[_pos][players_pos.count(_pos)]

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
    state.player_display[_pos][0] = string


class parent_class:
    def input_management(self, user_input):
        """determines what action to perform with user input"""
    
    def online_management(self, command):
        """executes relevant logic for an online command"""

    def disconnect_management(self, quitter):
        """handles an online player leaving mid-game
        """ 
        if state.online_config.socket_type == "client":
            print(f"=== player {quitter} ({state.online_config.joined_clients[0][quitter]}) has gone bankrupt! ===\n\n    ", end ="")
        else:
            print(f"=== player {quitter} ({state.online_config.joined_clients[quitter][0]}) has gone bankrupt! ===\n\n    ", end="")
        bankruptcy(quitter, "disconnect")

    def __call__(self): pass 
    def __init_subclass__(self): self.__name = None
    def __eq__(self, value): return self.__name__ == value

    @property
    def __name__(self):
        # if name does not exist, it is found through globals
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

    # game version will get overwritten, so a copy is recorded to
    # compare with save version to make sure they're the same
    true_game_version = state.game_version
    
    # totally secure 😎
    for _line in savefile:
        exec(_line, globals())
   
    # this subtracts the time played on the save from the start time,
    # so the end-screen calculations reflect the extra time played

    state.start_time = time() - state.time_played

    for item in state.player.values():
        update_player_position(item["pos"])


    if state.game_version != true_game_version:
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
        if variables.property_data[i]["owner"] != None:
            save_file.write(f"variables.property_data[{i}].update({{'owner': {variables.property_data[i]['owner']},"
                            f"'upgrade state': {variables.property_data[i]['upgrade state']}}})\n")

    # the time is rounded to the nearest second
    save_file.write(f"time_played = {str(round(time() - variables.start_time))}\n")

    save_file.close()