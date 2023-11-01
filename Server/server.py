import socket
import threading

MAX_CLIENTS = 5

connectingClients = []

def serverSend():
    while True:
        message = input()
        message = message.strip().split(" ")
        if not connectingClients:
            print("There is no connecting client")
            continue
        for connectSocket in connectingClients:
            ip, _ = connectSocket.getpeername()
            if len(message) > 1:
                if message[0] == "ping":
                    if message[1] != ip:
                        print(f"{message[1]} is down!")
                        continue
                    else:
                        message = "requestPing"
                elif message[0] == "discover":
                    if message[1] != ip:
                        print("Error!")
                        continue
                    else:
                        message = "requestDiscover"
                connectSocket.send(message.encode())
            else:
                print("Command missing arguments!")
    connectSocket.close()

def serverReceive(connectSocket, address):
    while True:
        try:
            message = connectSocket.recv(1024).decode()
            if not message:
                break
            command = message.strip().split(" ")
            print(f"{address}: {message}")
            if (command[0] == "requestIP"):
                connectSocket.send(("respondIP " + socket.gethostbyname(socket.gethostname())).encode())
            elif command[0] == "respondPing":
                print(f"{command[1]} is up.")
            elif command[0] == "respondDiscover":
                for i in command[1:]:
                    print(i[:-1])
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
    serverProgram()    serverProgram()
