"""functions to start/operate online games, and communicate between players"""

def sanitise(message: str, characters = {"%": "#", ":": "$"}):
    """replaces desired characters using dictionary (key becomes value)
    ensure multiple characters are not replaced with the same one"""

    message = message.replace("\\", "\\\\")

    # ensures forbidden characters are substituted
    for item in characters.items():
        message = message.replace(item[0], "\\" + item[1])

    return message

def unsanitise(message: str, characters = {"%": "#", ":": "$"}):
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

    data = sanitise(data)

    if online_config.socket_type == "host":
        if data.startswith("whisper"):
            parts = data.split(":")
            msg = data.removeprefix(f"whisper:{parts[1]}:").encode()
            online_config.joined_clients[int(parts[1])].sendall(f"{msg}:1%")
            return

        for item in online_config.joined_clients:
            item[1].sendall(f"{data}:{online_config.player_num}%".encode())

    elif online_config.socket_type == "client":
        online_config.socket.sendall(f"{data}:{online_config.player_num}%".encode())

async def get_data():
    """gets data sent from other players in an online game"""
    global player
    global player_turn
    global players_playing

    def action(arg: str):
        """online commands that don't differ between client and host"""

        global property_data

        match arg:
            case "turnfinished":
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
                elif online_config.player_num == player_turn:
                    print("\n    === it's now your turn to roll ===\n\n    ", end="")
            
            case "varupdate":
                _, var, value, _ = online_input.split(":")
                globals().update({var: eval(value)})

            case "propertyupdate":
                _, prop, owner, upgrades, _ = online_input.split(":")
                prop = int(prop)
                property_data[prop]["owner"] = int(owner)
                property_data[prop]["upgrade state"] = int(upgrades)
                colour_set = []

                # ensures colour set values are properly updated
                for check_prop in property_data:
                    if not ("colour set" in property_data[prop].keys() and "colour set" in check_prop.keys()):
                        continue

                    if property_data[prop]["colour set"] == check_prop["colour set"] and property_data[prop]["owner"] == check_prop["owner"]:
                        colour_set.append(prop)
                         
                # brown and dark blue (sets 0 and 7) only have two properties in their set
                if (len(colour_set) == 3 and property_data[prop]["colour set"] not in [0, 7]) \
                    or (len(colour_set) == 2 and property_data[prop]["colour set"] in [0, 7]):

                    for _prop in colour_set: property_data[_prop]["upgrade state"] = 2

            case "carddrawn":
                _, card, _ = online_input.split(":")
                if card == "cc": community_chest.draw_card()
                else: chance.draw_card()

            case "auctionstart":
                pass

            case _:
                input(f"{online_input=}")
   
    loop = asyncio.get_running_loop()
    message_queue = []

    if online_config.socket_type == "host":
        while not online_config.stop_event.is_set():
            for item in online_config.joined_clients:
                try:
                    if message_queue:
                        online_input = message_queue.pop(0)
                    else:
                        online_input = await loop.run_in_executor(None, item[1].recv, 1024)
                        online_input = online_input.decode()

                except (UnicodeDecodeError, BlockingIOError):
                    continue
                
                except (ConnectionError, ConnectionAbortedError, ConnectionResetError, ConnectionRefusedError):
                    online_config.handle_client_quit(item[3])
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
                    msg = online_input.removeprefix(f"whisper:{parts[1]}:").encode()
                    online_config.joined_clients[int(parts[1])].sendall(f"{msg}:{item[0]}%")
                    return

                # ensures all clients except sender receive message
                for sub_item in online_config.joined_clients:
                    if sub_item != item:
                        sub_item[1].sendall(f"{online_input}%".encode())

                # a blank message signals the client has lost connection
                if online_input == "":
                    online_config.handle_client_quit(item[3])
                    continue

                else:
                    action(online_input.split(":")[0])
      
            # reduces computational strain
            await asyncio.sleep(1)

    elif online_config.socket_type == "client":
        while not online_config.stop_event.is_set():
            try:
                if message_queue:
                    online_input = message_queue.pop(0)
                else:
                    online_input = await loop.run_in_executor(None, online_config.socket.recv, 1024)
                    online_input = online_input.decode()

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
                input(f"{e=} {old_input=}")

            # sometimes, multiple messages get merged into one
            # this splits them and handles each separately
            message_queue.extend(online_input.split("%")[:-1])
            old_input = online_input
            online_input = unsanitise(message_queue.pop(0))

            if online_input.startswith("booted"):
                online_config.kicked_notice()
                return

            elif online_input.startswith("users update"):

                _, client_list, ID = online_input.split(":")
                client_list = eval(client_list)

                online_config.joined_clients = client_list
                online_config.joined_clients[2] = [int(x) for x in online_config.joined_clients[2]] # insurance

                # when a player leaves before the game starts,
                # host sends users update, and recalculates IDs
                # if a player is joining, IDs remain unchanged
                online_config.player_num = int(ID)

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
                }

                player_turn = better_iter(range(1, players_playing + 1), True)
                update_player_position(0)
                online_config.game_strt_event.set()
                display_game_notice()

            elif online_input == "":
                online_config.connection_lost()
                return

            else:
                action(online_input.split(":")[0])
            
            await asyncio.sleep(1)

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

        # creates a new socket for connection
        self.socket = socket(AF_INET, SOCK_STREAM)

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
            name, icon = client.recv(1024).decode().split(":")
           
            client.sendall(f"{len(self.joined_clients) + 2}:{chance.values}:{community_chest.values}".encode())

            client.setblocking(False)
            self.joined_clients.append([name, client, icon, len(self.joined_clients) + 2])

            # alerts all clients to update in players
            client_list = [[self.display_name], [self.display_icon], [1]]
            for item in self.joined_clients:
                client_list[0].append(item[0])
                client_list[1].append(item[2])
                client_list[2].append(item[3])

            sleep(150) # should stop messages bunching up for the last joined client
            for item in self.joined_clients:

                # ID is expected: see comment on client receiving side
                item[1].sendall(f"users update:{client_list}:{item[3]}%".encode())

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

            if "%" in user_input or ":" in user_input:
                print("\n    === no using '%' or ':' - my bad code relies on them for control characters ===\n\n    ", end="")
                return

            if len(name) > 20:
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
                        item[1].sendall(b"booted:1%")
                        item[1].close()
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

                # protocol is for joined clients to ensure same version
                self.socket.sendall(str(game_version).encode())

                same_ver = self.socket.recv(1024).decode()

                if same_ver != "True":
                    self.wrong_version_notice()
                    return

                # then names are exchanged
                self.socket.sendall(f"{self.display_name}:{self.display_icon}".encode())

                """
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
                """
                
                # ensures chance cards are consistent across games
                num, chance_order, cc_order = self.socket.recv(1024).decode().split(":")
                self.player_num = int(num)

                chance.values = eval(chance_order)
                community_chest.values = eval(cc_order)
                
                # receives list of playing clients
                _, client_list, _ = self.socket.recv(1024).decode().split(":")
                online_config.joined_clients = eval(client_list.removesuffix("%"))
                online_config.joined_clients[2] = [int(x) for x in online_config.joined_clients[2]]

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
        quitter = int(quitter)
        if self.socket_type == "client":

            # removes the player from user's list of players
            # played ID is used as index to remove from all 3 sub-lists
            for _list in online_config.joined_clients:
                del _list[quitter - 1]

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

        """        self.stop_event.set()
        self.gather.cancel()
        if self.socket_type == "client":
            self.socket.close()
        else:
            for item in self.joined_clients:
                item[1].close()

        for task in online_config.running_tasks:
            task.cancel()"""

        if name == "nt":
            system(f"taskkill /PID {getpid()} /F")
        elif name == "posix":
            system(f"kill -9 {getpid()}")

    def handle_client_quit(self, quitter: int):
        """as a host, determines how to handle a client quitting.
        sends appropriate updates to other clients"""
        if online_config.game_strt_event.is_set():
            
            # alerts other clients, removes
            for item in online_config.joined_clients:
                if item[3] != quitter:
                    item[1].sendall(f"clientquit:{quitter}%".encode())

            globals()[current_screen].disconnect_management(quitter)
            bankruptcy(quitter, "disconnect")

        # otherwise, re-calculates player IDs if game hasn't started yet,
        # removes the quitter from existence
        else:
            # removes quitter
            del self.joined_clients[quitter - 2] # host doesn't appear, and IDs are 1-4, not 0-3
            
            # recalculates IDs
            ID = 2
            for client in self.joined_clients:
                client[3] = ID
                ID += 1

            # gathers changes
            client_list = [[self.display_name], [self.display_icon], [1]]
            for item in self.joined_clients:
                client_list[0].append(item[0])
                client_list[1].append(item[2])
                client_list[2].append(item[3])

            # alerts users of updates
            for item in self.joined_clients:
                item[1].sendall(f"users update:{client_list}:{item[3]}%".encode())

            self.host_wait_screen()

    async def shell(self):
        """main entry point for asynchronous functions"""
        if dev_mode:
            asyncio.get_running_loop().set_debug(True)

        self.running_tasks = [asyncio.Task(get_input()), asyncio.Task(get_data()), asyncio.Task(self.get_users())]
        self.gather = asyncio.gather(*self.running_tasks)

        await self.gather


online_config = online_config_class()