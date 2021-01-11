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
        print(player.nick + " move " + self.direction) #TODO changes due to command execution

class SoundCommand:
    def __init__(self, sound):
        self.sound = sound

    def execute(self, player, board):
        print(player.nick + " sound " + self.sound) #TODO changes due to command execution

class CollectCommand:
    def execute(self, player, board):
        print(player.nick + " collect food!") #TODO changes due to command execution

class Player:
    def __init__(self, addr, nick):
        self.addr = addr
        self.x_position = 0
        self.y_position = 0
        self.nick = nick
        self.current_command = NoopCommand()

    def move(self, x_vector, y_vector):
        self.x = self.x + x_vector
        self.y = self.y + y_vector

    def execute_command(self, board):
        self.current_command.execute(self, board)

class Floor:
    pass

class Food:
    pass

class Wall:
    pass

class GameBoard:
    def __init__(self, size, probability):
        self.size = size
        self.food_probability = probability
        self.fields = {}
        self.generate_board()

    def generate_board(self):
        for row in range(0, self.size):
            self.fields[row] = {} 
            for col in range(0, self.size):
                self.fields[row][col] = Floor() #TODO add Wall generation

    def generate_food(self):
        for row in range(0, self.size):
            for col in range(0, self.size):
                if random.random() <= self.probability:
                    self.fields[row][col] = Food()

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
            for player in self.players.values():
                player.execute_command(self.board)
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