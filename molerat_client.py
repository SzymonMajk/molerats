import socket


addr = ('localhost', 65420)
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect(addr)
    while True:
        s.sendall(b'Hello, world')
        data = s.recv(1024)
        print('Received', repr(data))