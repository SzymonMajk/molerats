import socket
import _thread
import time
import sys
import random


initial_reserves = 20
board_size = 10
food_probability = 0.05
service_address = ('', 65420)

class NoopCommand:
    def execute(self, player, board):
        pass

class MoveCommand:
    def __init__(self, direction):
        self.direction = direction

    def execute(self, player, board):
        new_x_position = player.x_position
        new_y_position = player.y_position

        if self.direction == "north":
            new_y_position = new_y_position + 1
        elif  self.direction == "east":
            new_x_position = new_x_position - 1
        elif  self.direction == "west":
            new_x_position = new_x_position + 1
        elif self.direction == "south":
            new_y_position = new_y_position - 1

        if board.can_move(new_x_position, new_y_position):
            player.move(new_x_position, new_y_position)

class SoundCommand:
    def __init__(self, sound):
        self.sound = sound

    def execute(self, player, board):
        board.add_sound(self.sound, player.x_position, player.y_position)

class CollectCommand:
    def execute(self, player, board):
        if player.inventory_reserves <= 0:
            player.inventory_reserves = board.collect_food(player.x_position, player.y_position)
        elif board.inside_queen_chamber(player.x_position, player.y_position):
            board.left_reserves(player.inventory_reserves)
            player.inventory_reserves = 0

class Player:
    def __init__(self, addr, nick):
        self.addr = addr
        self.x_position = board_size / 2
        self.y_position = board_size / 2
        self.inventory_reserves = 0
        self.nick = nick
        self.current_command = NoopCommand()

    def move(self, new_x_position, new_y_position):
        self.x_position = new_x_position
        self.y_position = new_y_position

    def execute_command(self, board):
        self.current_command.execute(self, board)

class Sound:
    def __init__(self, type, x_position, y_position):
        self.type = type
        self.time_to_live = 3
        self.x_position = x_position
        self.y_position = y_position

class Food:
    def __init__(self, value, x_position, y_position):
        self.value = value
        self.x_position = x_position
        self.y_position = y_position

class Floor:
    pass

class Wall:
    pass

class GameBoard:
    def __init__(self, size, probability):
        self.size = size
        self.probability = probability
        self.fields = {}
        self.foods = []
        self.sounds = []
        self.collected_food = 0
        self.generate_board()

    def generate_board(self):
        for row in range(0, self.size):
            self.fields[row] = {} 
            for col in range(0, self.size):
                self.fields[row][col] = Floor() #TODO add Wall generation

    def generate_food(self):
        for row in range(0, self.size):
            for col in range(0, self.size):
                random_value = random.random()
                if random_value <= self.probability and not self.inside_queen_chamber(row, col):
                    self.foods.append(Food(int((1 - random_value) * 50), row, col))

    def update_sounds(self):
        for sound in list(self.sounds):
            sound.time_to_live = sound.time_to_live - 1
            
            if sound.time_to_live <= 0:
                self.sounds.remove(sound)

    def can_move(self, x_position, y_position):
        if x_position in self.fields.keys():
            if y_position in self.fields[x_position].keys():
                return not isinstance(self.fields[x_position][y_position], Wall)

    def add_sound(self, type, x_position, y_position):
        self.sounds.append(Sound(type, x_position, y_position))

    def collect_food(self, x_position, y_position):
        for food in list(self.foods):
            if food.x_position == x_position and food.y_position == y_position:
                value = food.value
                print("Collected! " + str(value))
                self.foods.remove(food)
                return value
        return 0

    def inside_queen_chamber(self, x_position, y_position):
        return abs(self.size / 2 - x_position) <= 2 and abs(self.size / 2 - y_position) <= 2

    def left_reserves(self, food):
        self.collected_food = food

    def use_reserves(self):
        used_reserves = self.collected_food
        self.collected_food = 0
        return used_reserves

class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.board = GameBoard(board_size, food_probability)
        self.running = False
        self.round = 0
        self.score = 0
        self.players = dict()
        self.reserves = initial_reserves

    def add_player(self, addr, player):
        self.players[addr] = player

    def remove_player(self, addr):
        try:
            del self.players[addr]
        except KeyError:
            pass

    def render_lobby(self):
        lobby = "Lobby:"
        for p in game.players.values():
            lobby = lobby + " " + p.nick + " "
        return lobby

    def update_game(self):
        if self.reserves > 0:
            self.board.generate_food()
            self.board.update_sounds()
            for player in self.players.values():
                player.execute_command(self.board)
            self.reserves = self.reserves + self.board.use_reserves()
            self.round = self.round + 1
            self.reserves = self.reserves - 1
        else:
            self.running = False
            self.score = "Game finished, score = " + str(self.round)

    def render_for_player(self, addr): #TODO consolidate with GameBoard, probably by json
        render = "Position: (" + str(self.players[addr].x_position) + "),(" + str(self.players[addr].y_position) + ")" 
        render = render + " " + str(self.reserves) + " reserves left! "
        return render

    def finished(self):
        return not self.running and self.reserves <= 0 and not self.players

def parse_input(raw_input):
    if raw_input == "north":
        return MoveCommand("north")
    elif raw_input == "east":
        return MoveCommand("east")
    elif raw_input == "south":
        return MoveCommand("south")
    elif raw_input == "west":
        return MoveCommand("west")
    elif raw_input == "collect":
        return CollectCommand()
    elif raw_input == "snarl":
        return SoundCommand("snarl")
    elif raw_input == "scrape":
        return SoundCommand("scrape")
    elif raw_input == "squeak":
        return SoundCommand("squeak")
    else:
        return NoopCommand()

def handle_client(conn, addr, game):
    with conn as client_socket:
        nick = client_socket.recv(1024).decode()
        player = Player(addr, nick)
        game.add_player(addr, player)
        client_socket.send(nick.encode())

        while True:
            try:
                msg = client_socket.recv(1024)

                if msg.decode() == "start":
                    msg = "Game started by " + str(player.nick)
                    game.running = True

                if game.running:
                    msg = b'Game starts in seconds...'
                    client_socket.send(msg)
                    break

                msg = game.render_lobby().encode()
                client_socket.send(msg)
            except ConnectionResetError:
                game.remove_player(addr)

        while True:
            try:
                if game.running:
                    player.current_command = parse_input(client_socket.recv(1024).decode())
                    rendered_game = game.render_for_player(addr)
                    client_socket.send(rendered_game.encode())
                else:
                    client_socket.recv(1024)
                    client_socket.send(game.score.encode())
                    break
            except (ConnectionResetError, ConnectionAbortedError):
                game.remove_player(addr)
                break

def game_loop(game):
    while True:
        try:
            if game.running:
                game.update_game()
                print('Game updated! Round ' + str(game.round))
                time.sleep(5)
            elif game.finished():
                print('Game finished! ' + str(game.score))
                game.reset()
                time.sleep(5)
            else:
                print(game.render_lobby())
                time.sleep(10)
        except KeyboardInterrupt:
            break


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    print('Server started!')
    game = Game()
    _thread.start_new_thread(game_loop,(game,))
    print('Waiting for clients...')
    server_socket.bind(service_address)
    server_socket.settimeout(1.0)
    server_socket.listen(5)

    while True:
        try:
            conn, addr = server_socket.accept()
            print('New client! Address: ', addr)
            _thread.start_new_thread(handle_client,(conn, addr,game))
        except IOError:
            continue
        except KeyboardInterrupt:
            break