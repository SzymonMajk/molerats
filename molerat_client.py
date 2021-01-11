import socket
import _thread
import time


class Message:
    def __init__(self):
        self.content = "NOOP"

    def reset(self):
        self.content = "NOOP"

def communicate(addr, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(addr)
	
        s.sendall(message.content.encode())
        data = s.recv(1024)
        print(repr(data))
	
        while True:
            try:
                s.sendall(message.content.encode())
                data = s.recv(1024)
                message.reset()
                print('Received: ', repr(data.decode()))
                time.sleep(4)
            except (ConnectionResetError, ConnectionAbortedError):
                break

print("Welcome in molerats!")

addr = ('localhost', 65420)
message = Message()

print("We will try to connect to server at host ", addr[0], " on port ", addr[1])
print("First send your nick, ,,start'' will finish the lobby and start the game on server")
print("After each iteration you will be informed about game status")
print("Move using wasd keys, 1,2 and 3 will allow you to make noise, use r to pick a food")
print("Remember! It is easy to get lost in molerats tunnels...")

message.content = input("I am ")
_thread.start_new_thread(communicate,(addr, message))

while True:
    raw_input = input("To server s to start, other options w a s d r 1 2 3 << ")
	
    if raw_input == "start":
        message.content = "start"
    elif raw_input == "w":
        message.content = "north"
    elif raw_input == "a":
        message.content = "east"
    elif raw_input == "s":
        message.content = "south"
    elif raw_input == "d":
        message.content = "west"
    elif raw_input == "r":
        message.content = "collect"
    elif raw_input == "1":
        message.content = "snarl"
    elif raw_input == "2":
        message.content = "scrape"
    elif raw_input == "3":
        message.content = "squeak"
    else:
        time.sleep(0.5)
