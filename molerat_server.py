import socket
import _thread


service_address = ('', 65420)

def on_new_client(clientsocket,addr):
    print("du[a")
    with clientsocket as s:
        print("du[a")
        while True:
            msg = s.recv(1024)
            #do some checks and if msg == someWeirdSignal: break:
            print(addr, ' >> ', msg)
            msg = b'SERVER >> reponse'
        
            print("Game proceeding...")
        
            s.send(msg)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    print('Server started!')
    print('Waiting for clients...')
    s.bind(service_address)
    s.listen()
    while True:
        conn, addr = s.accept()
        print('Connected by', addr)
        _thread.start_new_thread(on_new_client,(conn,addr))
