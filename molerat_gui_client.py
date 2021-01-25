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
                    game_condition.state = json.loads('{"lobby" : "' + data + '"}')
                time.sleep(0.01)
            except (ConnectionResetError, ConnectionAbortedError):
                game_condition.finished = True
                break

print("Welcome in molerats!")

def draw_game(pygame, state):

    if "fields" in state.keys():
        for field in state["fields"]:
            if field[2] == 'F':
                pygame.draw.rect(screen, (0, 128, 255), pygame.Rect(field[0] * 20 + 15 * 20, field[1] * 20 + 15 * 20, 20, 20))
            else:
                pygame.draw.rect(screen, (128, 128, 128), pygame.Rect(field[0] * 20 + 15 * 20, field[1] * 20 + 15 * 20, 20, 20))
    if "pheromones" in state.keys():
        for pheromone in state["pheromones"]:
            pygame.draw.rect(screen, (128, 0, 0), pygame.Rect(pheromone[0] * 20 + 15 * 20, pheromone[1] * 20 + 15 * 20, 20, 20))

    if "sounds" in state.keys():
        for sound in state["sounds"]:
            if field[2] == 'snarl':
                pygame.draw.rect(screen, (0, 108, 0), pygame.Rect(sound[0] * 20 + 15 * 20, sound[1] * 20 + 15 * 20, 20, 20))
            elif field[2] == 'scrape':
                pygame.draw.rect(screen, (0, 128, 0), pygame.Rect(sound[0] * 20 + 15 * 20, sound[1] * 20 + 15 * 20, 20, 20))
            elif field[2] == 'squeak':
                pygame.draw.rect(screen, (0, 148, 0), pygame.Rect(sound[0] * 20 + 15 * 20, sound[1] * 20 + 15 * 20, 20, 20))
    if "foods" in state.keys():
        for food in state["foods"]:
            pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(food[0] * 20 + 15 * 20, food[1] * 20 + 15 * 20, 20, 20))
        pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(15 * 20, 15 * 20, 20, 20))

        text = "Reserves = " + str(state["reserves"])
        if "queen_chamber" in state.keys():
            text = text + ' in queen chamber'
        myfont = pygame.font.SysFont('Comic Sans MS', 30)
        textsurface = myfont.render(text, False, (50, 50, 50))
        screen.blit(textsurface,(20,20))
    else:
        myfont = pygame.font.SysFont('Comic Sans MS', 30)
        if 'score' in state['lobby']:
            textsurface = myfont.render(state['lobby'], False, (50, 50, 50))
            screen.blit(textsurface,(20,20))
        else:
            textsurface1 = myfont.render('Push space to start!', False, (50, 50, 50))
            textsurface2 = myfont.render('w a s d - move, r - pick food, 1,2,3 - noise', False, (50, 50, 50))
            textsurface3 = myfont.render('player is white rectangle, food is red', False, (50, 50, 50))
            textsurface4 = myfont.render('collected food left in quenn chamber', False, (50, 50, 50))
            textsurface5 = myfont.render(state['lobby'], False, (50, 50, 50))
            screen.blit(textsurface1,(20,140))
            screen.blit(textsurface2,(20,20))
            screen.blit(textsurface3,(20,60))
            screen.blit(textsurface4,(20,100))
            screen.blit(textsurface5,(20,180))

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
screen = pygame.display.set_mode((600, 600))
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            game_condition.message = "start"
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_w:
            game_condition.message = "south"
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_a:
            game_condition.message = "east"
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_s:
            game_condition.message = "north"
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
