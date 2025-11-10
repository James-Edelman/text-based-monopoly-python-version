"""functions to start/operate online games, and communicate between players"""

from socket import socket, gethostname, gethostbyname, AF_INET, SOCK_STREAM
from os import system, name, getpid
from time import time
import asyncio
from wcwidth import wcswidth
from better_iterator import better_iter

import utils
from utils import repair_property_states, sleep, update_player_position, create_prompts, clear_screen, ReturnException
import state

__required__ = ["game.bankruptcy"]

bankruptcy = None

type decorator = function
def coro_protection(coro) -> decorator:
    """decorator. suppresses CancelledError once coroutine canceled"""
    async def sub(*args, **kwards):
        try:
            await coro(*args, **kwards)
        except asyncio.CancelledError:
            return

    sub.__name__ = coro.__name__
    return sub


def sanitise(message: str, characters = {"%": "#"}):
    """replaces desired characters using dictionary (key becomes value)
    ensure multiple characters are not replaced with the same one"""

    message = message.replace("\\", "\\\\")

    # ensures forbidden characters are substituted
    for item in characters.items():
        message = message.replace(item[0], "\\" + item[1])

    return message


def unsanitise(message: str, characters = {"%": "#"}):
    """converts sanitised string back to original 
    make sure to use same dictionary used in sanitise function"""
    swap = {}
    for item in list(characters.items()):
        swap.update({item[1]: item[0]})
    characters = swap

    # ensure literal backslashes don't cause KeyError
    characters.update({"\\": "\\"})
    del swap

    restored = []
    i = 0

    # goes through message, replaces control characters
    while i < len(message):
        if message[i] == "\\":
            try: char = message[i+1]
            except IndexError: break

            restored.append(characters[char])
            i += 1
        else:
            restored.append(message[i])
        i += 1
    restored = ''.join(restored)
    return restored


def send_data(data: str):
    """sends message to correct socket. appends ID to end of message
    format: type : arg1 : arg2 : arg3 ... : senderID %

    start with whisper:[target]: to send message to specific player
    """

    # % is used as message terminator,
    # it is replaced by '\#' within messages
    data = sanitise(data)

    if state.online_config.socket_type == "host":

        # determines receiver, only sends message to specific socket
        if data.startswith("whisper"):
            parts = data.split(":")
            msg = data.removeprefix(f"whisper:{parts[1]}:")
            state.online_config.joined_clients[int(parts[1]) - 1][3].sendall(f"{msg}:1%".encode()) # host is always 1
            return

        # host sends message to all clients
        for item in state.online_config.joined_clients:
            if not item[4]: # if socket is activated
                continue
            try:
                item[3].sendall(f"{data}:{state.online_config.player_num}%".encode())
            except (ConnectionError, ConnectionAbortedError, ConnectionResetError, ConnectionRefusedError):
                state.online_config.handle_client_quit(item[2])

    elif state.online_config.socket_type == "client":
        state.online_config.socket.sendall(f"{data}:{state.online_config.player_num}%".encode())


async def receive_data():
    """gets data sent from other players in an online game"""

    def action(arg: str):
        """online commands that don't differ between client and host"""

        match arg:

            # after a player has finished rolling
            case "turnfinished":
                _, player_change, money_change, _ = online_input.split(":")
                money_change = eval(money_change)
                
                for i in range(state.players_playing):
                    state.player[i + 1]["$$$"] = money_change[i]
                
                # ensures player is sent to jail across all users
                if player_change == 40:
                    state.player_action.send_to_jail()
                else:
                    state.player[state.player_turn]["last pos"] = state.player[state.player_turn]["pos"]
                    state.player[state.player_turn]["pos"] = int(player_change)

                    update_player_position(state.player[state.player_turn]["pos"])
                    update_player_position(state.player[state.player_turn]["last pos"], "remove")

                state.refresh_board.end_turn_logic()

                # alerts user of turn change
                if state.current_screen == state.refresh_board:
                    state.refresh_board()
                if state.online_config.player_num == state.player_turn:
                    print("=== it's now your turn to roll ===\n\n    ", end="")
            
            # allows a user to update any variable
            case "varupdate":
                _, var, value, _ = online_input.split(":")
                state.__dict__.update({var: eval(value)})

            # when a player purchases a property
            case "propertyupdate":
                _, prop, owner, upgrades, _ = online_input.split(":")
                prop = int(prop)
                state.property_data[prop]["owner"] = int(owner)
                state.property_data[prop]["upgrade state"] = int(upgrades)

                repair_property_states()

            case "carddrawn":
                _, card, _ = online_input.split(":")
                if card == "cc": state.community_chest.draw_card()
                else: state.chance.draw_card()

            case "auctionstart":
                _, props, _ = online_input.split(":")
                props = eval(props)
                state.display_property(*props, bid=True)

            case "auction":
                _, bid, player = online_input.split(":")

                state.display_property.player_bids[int(player) - 1]["$$$"] = int(bid)
                state.display_property.bid_number += 1

                if state.display_property.bid_number > state.players_playing:
                    state.display_property.bid_number = state.players_playing

                state.display_property.countdown = 5

                state.display_property.player_bids.list = sorted(
                    state.display_property.player_bids.list,
                    key = lambda item: item["$$$"],
                    reverse = True
                )
                state.display_property(*state.display_property.property_queue)

            case "traderequest":

                _, player = online_input.split(":")
                p_name = state.online_config.joined_clients[int(player) - 1][0]

                # obviously, the player cannot accept while trading
                if state.trade_screen.is_trade:
                    send_data(f"whisper:{player}:decline trade")
                    return

                print(f"=== player {player} ({p_name}) would like to trade with you. ([A]ccept/ [D]ecline) ===\n\n    ", end ="")
                
                state.online_config.is_trade_request = True
                state.online_config.trade_requester = int(player)
               
            case "accept trade":
                state.online_config.is_trade_request = False
                state.online_config.trade_requester = None
                state.trade_screen.is_trade = True

                _, player = online_input.split(":")
                state.trade_screen.player_2["player"] = int(player)
                state.trade_screen.display_trade_window()

            case "decline trade": # used when quitting trades as well
                _, player = online_input.split(":")
                p_name = state.online_config.joined_clients[int(player) - 1][0]

                if state.trade_screen.is_trade:
                    state.refresh_board()
                    print(f"=== player {player} ({p_name}) cancelled the trade ===\n\n    ", end="")
                else:
                    state.refresh_board()
                    print(f"=== player {player} ({p_name}) didn't want to trade ===\n\n    ", end="")

                state.online_config.is_trade_request = False
                state.online_config.trade_requester = None
                state.trade_screen.__init__() # resets all variables

            case "trade":
                _, _type, value, player = online_input.split(":")
                player = int(player)

                # finds relevant trading player
                if player == state.trade_screen.player_1["player"]:
                    player = state.trade_screen.player_1
                else:
                    player = state.trade_screen.player_2
                
                # updates offer based on command
                if _type == "$": player["$$$"] = int(value)
                elif _type == "add p": player["props"].append(int(value))
                elif _type == "rmv p": player["props"].remove(int(value))
                elif _type == "accept": player["accepted?"] = bool(value)
                
                # ensures a person can not change a deal after the other agrees
                if not (_type == "accept" and bool(value)):
                    state.trade_screen.player_1["accepted?"] = False
                    state.trade_screen.player_2["accepted?"] = False

                if state.trade_screen.player_1["accepted?"] and state.trade_screen.player_2["accepted?"]:
                    state.trade_screen.trade_completed()
                else:
                    state.trade_screen.display_trade_window()

            case _:
                input(f"{online_input=}")
   
    loop = asyncio.get_running_loop()
    message_queue = []

    if state.online_config.socket_type == "host":
        while True:
            for item in state.online_config.joined_clients:
                
                # this is the host's fake socket
                if item[2] == 1: continue

                try:
                    if message_queue:
                        online_input = message_queue.pop(0)
                    else:
                        online_input = await loop.run_in_executor(None, item[3].recv, 1024)
                        online_input = online_input.decode()

                except (UnicodeDecodeError, BlockingIOError):
                    continue
                
                except (ConnectionError, ConnectionAbortedError, ConnectionResetError, ConnectionRefusedError):
                    state.online_config.handle_client_quit(item[2])
                    continue

                except OSError:
                    return

                # sometimes, multiple messages get merged into one
                # this splits them and handles each separately
                online_input = online_input.removesuffix("%")
                message_queue.extend(online_input.split("%"))
                online_input = unsanitise(message_queue.pop(0))

                if online_input.startswith("whisper"):
                    parts = online_input.split(":")

                    online_input = online_input.removeprefix(f"whisper:{parts[1]}:")
                    receiver = int(parts[1]) - 1

                    # the host processes message like normal if directed to them
                    if receiver == 0:
                        action(online_input.split(":")[0])
                    else:
                        state.online_config.joined_clients[receiver][3].sendall(f"{online_input.encode()}:{item[2]}%".encode())
                    continue

                # ensures all clients except sender receive message
                for sub_item in state.online_config.joined_clients:
                    if sub_item != item and sub_item[4]:
                        sub_item[3].sendall(f"{online_input}%".encode())

                # a blank message signals the client has lost connection
                if online_input == "":
                    state.online_config.handle_client_quit(item[2])
                    continue

                else:
                    action(online_input.split(":")[0])
      
            # reduces computational strain
            await asyncio.sleep(1)

    elif state.online_config.socket_type == "client":
        while True:
            try:
                if message_queue:
                    online_input = message_queue.pop(0)
                else:
                    online_input = await loop.run_in_executor(None, state.online_config.socket.recv, 1024)
                    online_input = online_input.decode()

            except (ConnectionAbortedError, ConnectionResetError, ConnectionError, ConnectionRefusedError):
                state.online_config.connection_lost()
                return

            # if user exits out, then message doesn't need to be shown
            except OSError:
                return

            # malformed messages are ignored
            except UnicodeDecodeError:
                continue

            # for debugging
            except Exception as e:
                input(f"{e=} {old_input=}")

            except:
                print('hmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm')

            # sometimes, multiple messages get merged into one
            # this splits them and handles each separately
            message_queue.extend(online_input.split("%")[:-1])
            old_input = online_input
            online_input = unsanitise(message_queue.pop(0))

            if online_input.startswith("booted"):
                state.online_config.kicked_notice()
                return

            elif online_input.startswith("users update"):

                _, client_list, ID = online_input.split(":")
                client_list = eval(client_list)

                state.online_config.joined_clients = client_list
                for item in state.online_config.joined_clients:
                    item[2] = int(item[2])

                # when a player leaves before the game starts,
                # host sends users update, and recalculates IDs
                # if a player is joining, IDs remain unchanged
                state.online_config.player_num = int(ID)

                state.online_config.client_wait_screen()

            elif online_input.startswith("clientquit:"):
                _, quitter = online_input.split(":")
                quitter = int(quitter)

                if state.online_config.game_strt_event.is_set():
                    state.player[quitter]["status"] = "disconnected"

                state.__dict__[state.current_screen].disconnect_management(quitter)

            elif online_input.startswith("hoststart"):
                initalise_game()

            elif online_input == "":
                state.online_config.connection_lost()
                return

            else:
                action(online_input.split(":")[0])
            
            await asyncio.sleep(1)


def initalise_game():
    """creates the players and starts game"""

    state.players_playing = len(state.online_config.joined_clients)

    # creates the players using the characters provided
    for i in range(state.players_playing):
        state.player[i + 1] = {
        "char": state.online_config.joined_clients[i][1],
        "$$$": 1500,
        "pos": 0,
        "last pos": 0,
        "jail passes": 0,
        "jail time": 0,
        "house total": 0,
        "hotel total": 0,
        "total properties": 0,
        "status": "playing",
    }

    state.player_turn = better_iter(range(1, state.players_playing + 1), True)
    state.start_time = time()
    state.online_config.game_strt_event.set()

    update_player_position(0)
    state.display_game_notice()


async def get_input():
    """gets user input (nonblocking) and executes appropriate logic"""
    loop = asyncio.get_running_loop()

    while True:
        u_input = await loop.run_in_executor(None, input)

        # the dice rolling creates separate asynchronous input checks
        # but since they are in a normal function, the cannot be awaited,
        # and are just added to the event loop
        if state.sub_async_input_override:

            # both handles coroutines and functions
            try: await state.input_override_logic(u_input)
            except TypeError: state.input_override_logic(u_input)
            
            continue

        try:
            state.__dict__[state.current_screen].input_management(u_input)
        except ReturnException:
            continue


class shell_socket():
    """fake socket to send data to"""
    def sendall(*args):
        pass

    def recv(*args):
        return b"host socket - ignore"


class online_config_class(utils.parent_class):
    """contains the menus and sockets for starting an online game

    .joined_clients = [[name, icon, ID, socket, active?],]
    .joied_clients  = [[name, icon, ID],] < client host ^
    
    .game_strt_event is set once the host starts the game.
    .player_num corresponds to a player key in `player`
    .running_tasks contains all asynchronous tasks created in self.shell()
    .ping count is an int as client, or list[int] as an host.
    .is_trade_request is checked before any input management
    """    
    def __init__(self):
        self.joined_clients = []
        self.action = None
        self.action_2 = None
        self.display_name = ""
        self.display_icon = ""
        self.socket_type = None
        self.is_trade_request = False
        self.trade_requester = None
        
        self.game_strt_event = asyncio.Event()
        self.running_tasks = []
        
        self.player_num = None # ID for specific player

        # creates a new socket for connection
        self.socket = socket(AF_INET, SOCK_STREAM)

    def __call__(self):
        state.current_screen = self.__name__

        self.action = "name 1"
        clear_screen()
        print()
        print("    === enter display name (this is different to icon shown on board) ===\n\n    ", end="")

    def mode_select(self):
        clear_screen()

        self.action = "mode select"

        print()
        for line in create_prompts(["Host", "Join", "Back"], spacing=[4, 3, 6]):
            print(line)
        print("\n    ", end = "")

    def connection_lost(self):
        """alerts user that connection to host was lost
        handles with closing the socket and exiting async"""

        state.current_screen = self.__name__
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

        state.current_screen = self.__name__
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
        state.current_screen = self.__name__
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
        state.current_screen = self.__name__
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
        print()
        print("    \x1b[s\x1b[0J")

        # buttons are adjusted once a user joins
        for line in create_prompts(
                ["Start game", "kick user", "Help", "back"],
                [len(self.joined_clients) > 0, len(self.joined_clients) > 0, True, True],
                [4, 3, 3, 6]
            ):
            print(line)

        print("\n\n    === joined users: ===\n")

        for item in self.joined_clients:
            print(f"    === {item[0]} joined ===")

        # restores cursor position
        print("\x1b[u\x1b[0K", end="", flush=True)

    def online_advice(self):
        clear_screen()
        state.current_screen = self.__name__
        self.action = "port forwarding advice"
        print()
        print("    ╔════════════════════════════════════════════════════════════════╗")
        print("    ║                                                                ║")
        print("    ║                     PEOPLE NOT CONNECTING?                     ║")
        print("    ║                                                                ║")
        print("    ║  People can only connect to this link if they're on the same   ║")
        print("    ║        network as you (if you are on a private network)        ║")
        print("    ║                                                                ║")
        print("    ║    = On a private network and want people online to join? =    ║")
        print("    ║                                                                ║")
        print("    ║      you'll need to enable port forwarding on your router      ║")
        print(f"    ║               (the port this game uses is {self.port})               ║")
        print("    ║                                                                ║")
        print("    ╚════════════════════════════════════════════════════════════════╝")
        print()
        for line in create_prompts(["How?", "Is it safe?", "This is LAN!", "Back"], spacing=[4, 3, 3, 6]):
            print(line)
        print("\n     ", end="")
        
    def client_wait_screen(self):
        state.current_screen = self.__name__
        self.action = "client wait screen"

        clear_screen()
        print()
        print("    ╔════════════════════════════════════════════════════════════════╗")
        print("    ║                                                                ║")
        print("    ║                            PLAYERS:                            ║")
        print("    ║                                                                ║")
        
        lock = False
        for item in self.joined_clients:
            name = item[0]

            # the first name is always the host
            if not lock:
                name += " (host)"
                lock = True

            if self.player_num == int(item[2]):
                name += " (you)"

            extra_space = ""
            extra_extra_space = ""
            for x in range(((40 - wcswidth(name)) // 2)):
                extra_space += " "

            if len(name) % 2 == 1: extra_extra_space = " "
            print(f"    ║            {extra_space}{name}{extra_space}{extra_extra_space}            ║")
        
        print("    ║                                                                ║")
        print("    ╚════════════════════════════════════════════════════════════════╝")
        print()
        for line in create_prompts(["back"]):
            print(line)
        print()
        print("    ", end="")
    
    def hard_mode(self):
        clear_screen()
        print("")
        print(r"       ___  ___        _____     _____ ____     _____      _____      _____     ____     ___  ___"    )
        print(r"      ╱   ╲╱   ╲      ╱     ╲    │    ╲│  │    ╱     ╲    │  _  \    ╱     ╲    │  │     ╲  \/  ╱ │ coded by:")
        print(r"     ╱  /╲  ╱\  ╲    │  (_)  │   │  ╲  ╲  │   │  (_)  │   │  ___/   │  (_)  │   │  │__    ╲_  _╱  │ James E.")
        print(r"    ╱__/  ╲╱  \__╲    ╲_____╱    |__│╲____|    ╲_____╱    |__|       ╲_____╱    |_____|    |__|   │ 2024, 2025")
        sleep(1500)
        print()
        print("\x1b[38;2;248;49;47m                    ██ ██  ▟███▙  ████▙  ████▙   ██▙▟██ ▟███▙ ████▙ ████\x1b[0m")
        print("\x1b[38;2;248;49;47m                    █████  ██▆██  ██▆█▛  ██ ██   ██▜▛██ ██ ██ ██ ██ ██▆▆\x1b[0m")
        print("\x1b[38;2;248;49;47m                    ██ ██  ██ ██  ██ ██  ████▛   ██  ██ ▜███▛ ████▛ ██▆▆\x1b[0m")
        sleep(1000)
        print()
        print("\x1b[38;2;255;200;100m                                              ~ COMING SOON ~\x1b[0m")

    @coro_protection
    async def get_users(self):
        """allows the host to receive users. Handles connection protocol"""
        if self.socket_type != "host": return
        loop = asyncio.get_running_loop()

        # check() cancels accepting new users once the game starts
        @coro_protection
        async def check():
            # users aren't accepted once game starts
            await self.game_strt_event.wait()
            accept_tsk.cancel()

        # accept needs to cancel check each time a user joins,
        # otherwise the gather hangs indefinitely from check
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

        while not self.game_strt_event.is_set():
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
            if client_version == state.game_version:
                client.sendall("True".encode())
            else:
                client.sendall("False".encode())
                continue

            # client sends name immediately after connection
            name, icon = client.recv(1024).decode().split(":")
           
            client.sendall(f"{len(self.joined_clients) + 1}:{state.chance.values}:{state.community_chest.values}".encode())

            client.setblocking(False)
            self.joined_clients.append([name, icon, len(self.joined_clients) + 1, client, True])

            # alerts all clients to update in players
            client_list = []
            client_list += [item[0:3] for item in self.joined_clients]

            sleep(150) # should stop messages bunching up for the last joined client
            for item in self.joined_clients:

                # ID is expected: see comment on client receiving side
                item[3].sendall(f"users update:{client_list}:{item[2]}%".encode())

            # ensures four players maximum isn't exceeded
            if len(self.joined_clients) == 3: return

            self.host_wait_screen()

    def input_management(self, user_input):
        
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

            if "%" in user_input or ":" in user_input:
                print("\n    === no using '%' or ':' - my bad code relies on them for control characters ===\n\n    ", end="")
                return

            if wcswidth(name) > 20:
                print("\n    === bro you do not need more than 20 characters try again ===\n\n    ", end="")

            # gets display name then player icon (see below)
            self.display_name = user_input

            if user_input.lower() == "frisk":
                self.hard_mode()

            print("\n    === enter player icon ===\n\n    ", end="")
            self.action = "name 2"

        elif self.action == "name 2":
            if "%" in user_input or ':' in user_input:
                print("\n    === no using '%' or ':' - my bad code relies on them for control characters ===\n\n    ", end="")

            # enforces 2 characters width for name
            name_width = wcswidth(user_input)
            
            if user_input in ["  ", r"\\"]:
                print("\n    === nice try. ===\n\n    ", end = "")
            elif name_width > 2:
                print("\n    === icon too large, try a different icon (eg: '😊' or 'JE') ===\n\n    ", end="")
            elif name_width < 2:
                print("\n    === icon too small, try a different icon (eg: '😊' or 'JE') ===\n\n    ", end="")
            elif name_width == -1:
                print("\n    === how have you even managed to get a string this wide?? try again. ===\n\n    ", end="")
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
                        item[3].sendall(b"booted:1%")
                        item[3].close()
                        self.joined_clients.remove(item)
                        break
                else:
                    print("\x1b[u\x1b[0K=== enter player name ([C]ancel): ", end="", flush=True)
                    return
                 
                print("\x1b[u\x1b[0K", end="", flush=True)
                self.action_2 = None
                self.host_wait_screen()

            elif self.action_2 == "accept notice":
                pass

            elif user_input in ["s", "S"]:
                if len(self.joined_clients) == 1:
                    print("\x1b[u\x1b[0K=== You need at least 2 players to start. [Enter] ===", end="", flush=True)
                    return

                send_data("hoststart")
                initalise_game()

            elif user_input in ["k", "K"]:
                 print("\x1b[u\x1b[0K=== enter player name ([C]ancel): ", end="", flush=True)
                 self.action_2 = "user to boot"

            elif user_input in ["h", "H"]:
                self.online_advice()

            elif user_input in ["b", "B"]:                
                self.quit_async()
            
            else:
                print("\x1b[u\x1b[0K", end="", flush=True)

        elif self.action == "port forwarding advice":
            if self.action_2 == "play prompt":
                if user_input in ["y", "Y"]:
                    self.action_2 = None
                    print("\n    === ok then stop whining ===\n\n    ", end="")

                elif user_input in ["n", "N"]:
                    self.quit_async()

                else:
                    print("\n    === you know these responses are prerecorded right? No clue what you just wrote ===\n\n    ", end="")


            if user_input in ["h", "H"]:
                print("\n    === step 1: open google ===")
                print("    === step 2: google \"how to do port forwarding\" ===\n\n    ", end="")

            elif user_input in ["i", "I"]:
                print("\n    === do you want to play or not. ===\n")
                for line in utils.create_prompts(["Yeah", "Not really"]):
                    print(line)
                print("\n    ", end="")
                self.action_2 = "play prompt"

            elif user_input in ["t", "T"]:
                print("\n    === Q: \"doesn't this technically count as LAN since it only works on the same network?\" ===")
                print("    === A: 01110011 01101000 01110101 01110100 00100000 01110101 01110000")
                print("           00101100 00100000 01101110 01100101 01110010 01100100 00100001 ===\n\n    ", end="")

            elif user_input in ["b", "B"]:
                self.action = None
                self.host_wait_screen()

            else:
                print("    ", end="")

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
                    if user_input in ["b", "B"]:
                        self.exit_async()

                    print("\n    === Error using join code. please try again ===\n\n    ", end="")
                    return

                # protocol is for joined clients to ensure same version
                self.socket.sendall(str(state.game_version).encode())

                same_ver = self.socket.recv(1024).decode()

                if same_ver != "True":
                    self.wrong_version_notice()
                    return

                # then names are exchanged
                self.socket.sendall(f"{self.display_name}:{self.display_icon}".encode())
                
                # ensures state.chance cards are consistent across games
                num, chance_order, cc_order = self.socket.recv(1024).decode().split(":")
                self.player_num = int(num)

                state.chance.values = eval(chance_order)
                state.community_chest.values = eval(cc_order)
                
                # receives list of playing clients
                _, client_list, _ = self.socket.recv(1024).decode().split(":")
                state.online_config.joined_clients = eval(client_list.removesuffix("%"))

                # ensures IDs are integers
                for item in state.online_config.joined_clients:
                    item[2] = int(item[2])

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

                # ensures other coroutine won't be permanently waiting for another connection
                self.socket.close()
                self.quit_async()

            else:
                print("\n    === command not recognised ===\n\n    ", end="")

        elif self.action == "mode select":
            if user_input in ["h", "H", "FORCELOCALHOST"] or user_input.startswith("port:"):
                self.socket_type = "host"
                self.player_num = 1

                if user_input == "FORCELOCALHOST":
                    self.U_IP_V4 = "127.0.0.1"
                elif user_input.startswith("port:"):
                    self.port = int(user_input.split(":")[1])
                else:
                    self.U_IP_V4 = gethostbyname(gethostname())

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

                self.joined_clients = [[self.display_name, self.display_icon, 1, shell_socket(), True]]
                self.host_wait_screen(f"{self.U_IP_V4}-{self.port}")

                try:
                    asyncio.run(self.shell())
                except:
                    pass
                print("    ", end = "")
                quit()
            
            elif user_input in ["j", "J"]:
                self.socket_type = "client"

                self.client_wait_screen()
                self.action_2 = "enter details"
                print("enter connection details: ", end = "")

            elif user_input in ["b", "B"]:
                self.game_strt_event.clear()
                state.homescreen()

            else:
                print("\n    === command not recognised ===\n\n    ", end="")

        else:
            print("\n    === command not recognised ===\n\n    ", end="")

    def disconnect_management(self, quitter):
        quitter = int(quitter)

        # removes the player from user's list of players
        state.online_config.joined_clients.pop(quitter - 1)

        if self.socket_type == "client":
            self.client_wait_screen()

        elif self.socket_type == "host":
            self.host_wait_screen()

    def quit_async(self):
        """quits all asynchronous tasks"""
        print("\x1b[0J")
        if name == "nt":
            system(f"taskkill /PID {getpid()} /F")
        elif name == "posix":
            system(f"kill -9 {getpid()}")

    def handle_client_quit(self, quitter: int):
        """as a host, determines how to handle a client quitting.
        sends appropriate updates to other clients"""
        if state.online_config.game_strt_event.is_set():

            # ensure the socket is not used again
            state.online_config.joined_clients[quitter - 1][4] = False

            # alerts other clients
            for item in state.online_config.joined_clients:
                if item[2] != quitter:
                    item[3].sendall(f"clientquit:{quitter}%".encode())

            state.__dict__[state.current_screen].disconnect_management(quitter)

        # otherwise, re-calculates player IDs if game hasn't started yet,
        # removes the quitter from existence
        else:
            # removes quitter
            self.joined_clients[quitter - 1].pop() # host doesn't appear, and IDs are 1-4, not 0-3
            
            # recalculates IDs
            ID = 2
            for client in self.joined_clients:
                client[2] = ID
                ID += 1

            # gathers changes
            client_list = [[self.display_name, self.display_icon, 1]]
            client_list += [item[0:3] for item in self.joined_clients]

            # alerts users of updates
            for item in self.joined_clients:
                if item[4]:
                    item[3].sendall(f"users update:{client_list}:{item[2]}%".encode())

            self.host_wait_screen()

    async def shell(self):
        """main entry point for asynchronous functions"""
        if state.dev_mode:
            asyncio.get_running_loop().set_debug(True)

        self.running_tasks = [asyncio.Task(get_input()), asyncio.Task(receive_data()), asyncio.Task(self.get_users())]
        self.gather = asyncio.gather(*self.running_tasks)

        await self.gather