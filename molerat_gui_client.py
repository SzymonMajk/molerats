import socket
import _thread
import time
import json
import pygame

class GameCondition:
    def __init__(self):
        self.finished = False
        self.message = "noop"
        self.state = {}

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
                    game_condition.state = json.loads(data)
                except json.decoder.JSONDecodeError as e:
                    print(data)
                time.sleep(4)
            except (ConnectionResetError, ConnectionAbortedError):
                game_condition.finished = True
                break

print("Welcome in molerats!")

def draw_game(pygame, state):

    if "fields" in state.keys():
        for field in state["fields"]:
            if field[2] == 'F':
                pygame.draw.rect(screen, (0, 128, 255), pygame.Rect(field[0] * 30 + 15 * 30, field[1] * 20 + 15 * 30, 30, 30))
            else:
                pygame.draw.rect(screen, (128, 128, 128), pygame.Rect(field[0] * 30 + 15 * 30, field[1] * 20 + 15 * 30, 30, 30))
			

addr = ('localhost', 65420)
game_condition = GameCondition()

print("We will try to connect to server at host ", addr[0], " on port ", addr[1])
print("First send your nick, ,,start'' will finish the lobby and start the game on server")
print("After each iteration you will be informed about game status")
print("Move using wasd keys, 1,2 and 3 will allow you to make noise, use r to pick a food")
print("Remember! It is easy to get lost in molerats tunnels...")
print("Space to start, then w a s d 1 2 3 and r")

game_condition.message = input("I am ")
_thread.start_new_thread(communicate,(addr, game_condition))

pygame.init()
screen = pygame.display.set_mode((800, 800))
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            game_condition.message = "start"
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_w:
            game_condition.message = "north"
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_a:
            game_condition.message = "east"
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_s:
            game_condition.message = "south"
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_d:
            game_condition.message = "west"
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            game_condition.message = "collect"
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_1:
            game_condition.message = "snarl"
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_2:
            game_condition.message = "scrape"
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_3:
            game_condition.message = "squeak"

    screen.fill((0, 0, 0))
    draw_game(pygame, game_condition.state)
    pygame.event.pump()
    pygame.display.flip()
    clock.tick(60)
