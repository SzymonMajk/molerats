import socket
import _thread
import time
import json

class GameCondition:
    def __init__(self):
        self.finished = False
        self.message = "noop"

    def reset(self):
        self.message = "noop"

def recvall(socket):
    BUFF_SIZE = 1024
    data = b''
    while True:
        part = socket.recv(BUFF_SIZE)
        data += part
        if len(part) < BUFF_SIZE:
            break
    return data

def communicate(addr, game_condition):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(addr)
	
        s.sendall(game_condition.message.encode())
        data = recvall(s).decode("utf-8")
        print(repr(data))
	
        while True:
            try:
                s.sendall(game_condition.message.encode())
                data = recvall(s).decode("utf-8")
                try:
                    print(json.loads(data))
                except json.decoder.JSONDecodeError as e:
                    print(data)
                time.sleep(1)
            except (ConnectionResetError, ConnectionAbortedError):
                game_condition.finished = True
                break

print("Welcome in molerats!")

addr = ('localhost', 65420)
game_condition = GameCondition()

print("We will try to connect to server at host ", addr[0], " on port ", addr[1])
print("First send your nick, ,,start'' will finish the lobby and start the game on server")
print("After each iteration you will be informed about game status")
print("Move using wasd keys, 1,2 and 3 will allow you to make noise, use r to pick a food")
print("Remember! It is easy to get lost in molerats tunnels...")

game_condition.message = input("I am ")
_thread.start_new_thread(communicate,(addr, game_condition))

while True:
    if game_condition.finished:
        break

    raw_input = input("To server start to start, other options w a s d r 1 2 3 << ")

    if raw_input == "start":
        game_condition.message = "start"
    elif raw_input == "w":
        game_condition.message = "north"
    elif raw_input == "a":
        game_condition.message = "east"
    elif raw_input == "s":
        game_condition.message = "south"
    elif raw_input == "d":
        game_condition.message = "west"
    elif raw_input == "r":
        game_condition.message = "collect"
    elif raw_input == "1":
        game_condition.message = "snarl"
    elif raw_input == "2":
        game_condition.message = "scrape"
    elif raw_input == "3":
        game_condition.message = "squeak"
    else:
        time.sleep(0.1)
