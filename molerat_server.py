import socket
import _thread
import time


service_address = ('', 65420)

class Command:
    def __init__(self):
        print("New command from player!")

class NoopCommand:
    pass

class Player:
    def __init__(self, nick):
        self.x_position = 0
        self.y_position = 0
        self.nick = nick
        self.current_command = NoopCommand()

    def move(self, x_vector, y_vector):
        self.x = self.x + x_vector
        self.y = self.y + y_vector

    def execute_command(self, game):
        print("Here happens changes due to the last " + str(self.nick) + " command")
        self.current_command = NoopCommand()

class Game:
    def __init__(self):
        self.running = False
        self.round = 0
        self.players = dict()

    def add_player(self, addr, player):
        self.players[addr] = player

    def render_for_player(self, addr):
        render = "Position: (" + str(self.players[addr].x_position) + "),(" + str(self.players[addr].y_position) + ")"
        render = render + "\n other info..."
        return render

def new_client(conn, addr, game):
    with conn as client_socket:
        nick = client_socket.recv(1024).decode()
        player = Player(nick)
        game.add_player(addr, player)
        client_socket.send(nick.encode())

        while True:
            msg = client_socket.recv(1024)

            if msg.decode() == "start":
                msg = "Game started by " + str(player.nick)
                game.running = True

            if game.running:
                msg = b'Game starts in seconds...'
                client_socket.send(msg)
                break

            msg = b'Server waits for command to start...'
            client_socket.send(msg)

        while True:
            msg = client_socket.recv(1024)
            player.command = Command()
            rendered_game = game.render_for_player(addr)
            client_socket.send(rendered_game.encode())

def game_loop(game):
    while True:
        if (game.running):
            for player in game.players.values():
                player.execute_command(game)
            print('Game updated!')
            game.round = game.round + 1
            time.sleep(5)
        else:
            print('Lobby:')
            for p in game.players.values():
                print(p.nick)
            time.sleep(10)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    print('Server started!')
    game = Game()
    _thread.start_new_thread(game_loop,(game,))
    print('Waiting for clients...')
    server_socket.bind(service_address)
    server_socket.listen(5)

    while True:
        conn, addr = server_socket.accept()
        print('New connection! ', addr)
        _thread.start_new_thread(new_client,(conn, addr,game))
