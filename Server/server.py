import socket
import threading

MAX_CLIENTS = 5

connectingClients = []

def serverSend():
    while True:
        message = input()
        if not connectingClients:
            print("There is no connecting client")
            continue
        for connectSocket in connectingClients:
            connectSocket.send(message.encode())

def serverReceive(connectSocket, address):
    while True:
        try:
            message = connectSocket.recv(1024).decode()
            if not message:
                break
            print(f"{address}: {message}")
        except ConnectionResetError:
            break
    connectSocket.close()
    connectingClients.remove(connectSocket)

def serverConnect(serverSocket):
    while True:
        connectSocket, address = serverSocket.accept()
        print(f"Connect from {address}")
        connectingClients.append(connectSocket)

        message = "clientAddress " + address[0] + ":" + str(address[1])
        connectSocket.send(message.encode())

        threadReceive = threading.Thread(target=serverReceive, args=(connectSocket, address))
        threadReceive.start()

        threadSend = threading.Thread(target=serverSend)
        threadSend.start()

def serverProgram():
    host = socket.gethostname()
    port = 12000

    serverSocket = socket.socket()
    serverSocket.bind((host, port))
    serverSocket.listen(MAX_CLIENTS)

    threadListen = threading.Thread(target=serverConnect, args=(serverSocket,))
    threadListen.start()

if __name__ == '__main__':
    serverProgram()