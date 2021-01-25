import socket
import _thread
import time
import sys
import random
import json


initial_reserves = 50
board_size = 100
vision_render = 3
audition_render = 8
smell_render = 15
food_probability = 0.002
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
            board.left_pheromones(player.nick, player.x_position, player.y_position)

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

class Pheromone:
    def __init__(self, nick, x_position, y_position):
        self.nick = nick
        self.time_to_live = 10
        self.x_position = x_position
        self.y_position = y_position

    def list_serialize(self):
        return [self.nick, self.x_position, self.y_position]

class Sound:
    def __init__(self, type, x_position, y_position):
        self.type = type
        self.time_to_live = 3
        self.x_position = x_position
        self.y_position = y_position

    def list_serialize(self):
        return [self.type, self.x_position, self.y_position]

class Food:
    def __init__(self, value, x_position, y_position):
        self.value = value
        self.x_position = x_position
        self.y_position = y_position

    def list_serialize(self):
        return [self.value, self.x_position, self.y_position]

class GameBoard:
    def __init__(self, size, probability):
        self.size = size
        self.probability = probability
        self.fields = {}
        self.foods = []
        self.sounds = []
        self.pheromones = []
        self.collected_food = 0
        self.generate_board()

    def generate_board(self):
        for row in range(0, self.size):
            self.fields[row] = {} 
            for col in range(0, self.size):
                if (self.inside_queen_chamber(row, col)):
                    self.fields[row][col] = 'F'
                else:
                    self.fields[row][col] = 'W'
        
        x_dig = self.size / 2
        y_dig = self.size / 2

        for i in range(0, self.size):
            random_value = random.random()
            if random_value < 0.25 and y_dig < self.size - 1:
                y_dig = y_dig + 1
            elif random_value >= 0.25 and random_value <= 0.75 and x_dig < self.size - 1:
                x_dig = x_dig + 1
            elif random_value > 0.75 and y_dig > 0:
                y_dig = y_dig - 1

            self.fields[x_dig][y_dig] = 'F'

        x_dig = self.size / 2
        y_dig = self.size / 2

        for i in range(0, self.size):
            random_value = random.random()
            if random_value < 0.25 and y_dig < self.size - 1:
                y_dig = y_dig + 1
            elif random_value >= 0.25 and random_value <= 0.75 and x_dig > 0:
                x_dig = x_dig - 1
            elif random_value > 0.75 and y_dig > 0:
                y_dig = y_dig - 1

            self.fields[x_dig][y_dig] = 'F'

        x_dig = self.size / 2
        y_dig = self.size / 2

        for i in range(0, self.size):
            random_value = random.random()
            if random_value < 0.25 and x_dig < self.size - 1:
                x_dig = x_dig + 1
            elif random_value >= 0.25 and random_value <= 0.75 and y_dig < self.size - 1:
                y_dig = y_dig + 1
            elif random_value > 0.75 and x_dig > 0:
                x_dig = x_dig - 1

            self.fields[x_dig][y_dig] = 'F'

        x_dig = self.size / 2
        y_dig = self.size / 2

        for i in range(0, self.size):
            random_value = random.random()
            if random_value < 0.25 and x_dig < self.size - 1:
                x_dig = x_dig + 1
            elif random_value >= 0.25 and random_value <= 0.75 and y_dig > 0:
                y_dig = y_dig - 1
            elif random_value > 0.75 and x_dig > 0:
                x_dig = x_dig - 1


            self.fields[x_dig][y_dig] = 'F'

    def generate_food(self):
        for row in range(0, self.size):
            for col in range(0, self.size):
                random_value = random.random()
                if random_value <= self.probability and not self.inside_queen_chamber(row, col) and self.fields[row][col] == 'F':
                    self.foods.append(Food(int((1 - random_value) * 50), row, col))

    def update_sounds(self):
        for sound in list(self.sounds):
            sound.time_to_live = sound.time_to_live - 1
            
            if sound.time_to_live <= 0:
                self.sounds.remove(sound)

    def update_pheromones(self):
        for pheromone in list(self.pheromones):
            pheromone.time_to_live = pheromone.time_to_live - 1
            
            if pheromone.time_to_live <= 0:
                self.pheromones.remove(pheromone)


    def can_move(self, x_position, y_position):
        if x_position in self.fields.keys():
            if y_position in self.fields[x_position].keys():
                return self.fields[x_position][y_position] == 'F'

    def add_sound(self, type, x_position, y_position):
        self.sounds.append(Sound(type, x_position, y_position))

    def left_pheromones(self, nick, x_position, y_position):
        self.pheromones.append(Pheromone(nick, x_position, y_position))

    def collect_food(self, x_position, y_position):
        for food in list(self.foods):
            if food.x_position == x_position and food.y_position == y_position:
                value = food.value
                print("Collected! " + str(value))
                self.foods.remove(food)
                return value
        return 0

    def inside_queen_chamber(self, x_position, y_position):
        return abs((self.size / 2) - x_position) <= 2 and abs((self.size / 2) - y_position) <= 2

    def left_reserves(self, food):
        print("More fooood! " + str(food))
        self.collected_food = food

    def use_reserves(self):
        used_reserves = self.collected_food
        self.collected_food = 0
        return used_reserves

    def fields_map_to_list_around(self, x_position, y_position):
        result = []
		
        for row in self.fields.keys():
            for col in self.fields[row]:
                if abs(row - x_position) <= vision_render and abs(col - y_position) <= vision_render:
                    result.append([row - x_position, col - y_position, self.fields[row][col]])

        return result

    def foods_to_list_around(self, x_position, y_position):
        result = []
		
        for food in self.foods:
            if abs(food.x_position - x_position) <= audition_render and abs(food.y_position - y_position) <= smell_render:
                result.append([food.x_position - x_position, food.y_position - y_position, food.value])

        return result

    def sounds_to_list_around(self, x_position, y_position):
        result = []
		
        for sound in self.sounds:
            if abs(sound.x_position - x_position) <= audition_render and abs(sound.y_position - y_position) <= audition_render:
                result.append([sound.x_position - x_position, sound.y_position - y_position, sound.type])

        return result

    def pheromones_to_list_around(self, x_position, y_position):
        result = []
		
        for pheromone in self.pheromones:
            if abs(pheromone.x_position - x_position) <= audition_render and abs(pheromone.y_position - y_position) <= smell_render:
                result.append([pheromone.x_position - x_position, pheromone.y_position - y_position, pheromone.nick])

        return result

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
            self.board.update_pheromones()
            for player in self.players.values():
                player.execute_command(self.board)
                player.current_command = NoopCommand()
            self.reserves = self.reserves + self.board.use_reserves()
            self.round = self.round + 1
            self.reserves = self.reserves - 1
        else:
            self.running = False
            self.score = "Game finished, score = " + str(self.round)



    def render_for_player(self, addr):
        x_position = self.players[addr].x_position
        y_position = self.players[addr].y_position
        rendered = dict()
        rendered["fields"] = self.board.fields_map_to_list_around(x_position, y_position)
        rendered["foods"] = self.board.foods_to_list_around(x_position, y_position)
        rendered["sounds"] = self.board.sounds_to_list_around(x_position, y_position)
        rendered["pheromones"] = self.board.pheromones_to_list_around(x_position, y_position)
        rendered["reserves"] = self.reserves
        if self.board.inside_queen_chamber(x_position, y_position):
            rendered["queen_chamber"] = True
        return json.dumps(rendered)

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
                    client_socket.sendall(bytes(rendered_game,encoding="utf-8"))
                else:
                    client_socket.recv(1024)
                    client_socket.sendall(bytes(game.score,encoding="utf-8"))
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
                time.sleep(0.5)
            elif game.finished():
                print('Game finished! ' + str(game.score))
                game.reset()
                time.sleep(0.5)
            else:
                print(game.render_lobby())
                time.sleep(2)
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