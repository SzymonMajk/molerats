import socket


print("Welcome in molerats!")
addr = ('localhost', 65420)
print("We will try to connect to server at host ", addr[0], " on port ", addr[1])
print("First send your nick, ,,start'' will finish the lobby and start the game on server")
print("After each iteration you will be informed about game status")
print("Move using wasd keys, 1,2 and 3 will allow you to make noise, use r to pick a food")
print("Remember! It is easy to get lost in molerats tunnels...")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect(addr)
	
    msg = input("I am ")
    s.sendall(msg.encode())
    data = s.recv(1024)
    print('Welcome!', repr(data))
	
    while True:
        msg = input("To server << ")
        s.sendall(msg.encode())
        data = s.recv(1024)
        print('Received', repr(data))