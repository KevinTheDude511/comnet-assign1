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
                        return
                    else:
                        message = "requestPing"
                elif message[0] == "discover":
                    if message[1] != ip:
                        print(f"{message[1]} is down!")
                        return
                    else:
                        message = "requestDiscover"
                connectSocket.send(message.encode())
            else:
                print("Command missing arguments!")
    connectSocket.close()

def fetchBroadcast(message, conClients):
    # Split the message into segments
    global connectingClients
    segments = message.split(" ")

    if len(segments) == 2:
        filename = segments[1]
        matching_clients = []
        # Construct the requestBroadcast message
        broadcast_message = f"requestBroadcast {filename}"

        # Send the request to all connected clients
        # broadcastSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # broadcastSocket.bind((socket.gethostname(), 10000))
        # broadcastSocket.listen(len(connectingClients))
        # for connectSocket in connectingClients:
        #     if (connectSocket != conClients ):
        #         connectSocket.send(broadcast_message.encode())
        # for i in range(len(connectingClients)):
        #     if (connectingClients[i] != conClients ):
        #         broadcastPeer, peerAddr = broadcastSocket.accept()
        #         response = broadcastPeer.recv(1024).decode()
        #         command = response.split(" ")
        #         if (command[0] == "respondBroadcast" and command[1] != "empty"):
        #             matching_clients.append(command[1])
        # broadcastSocket.close()
        broadcastSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        broadcastSocket.bind((socket.gethostname(), 10000))
        broadcastSocket.listen(len(connectingClients))
        for i in range(len(connectingClients)):
            if (connectingClients[i] != conClients ):
                connectingClients[i].send(broadcast_message.encode())
                broadcastPeer, peerAddr = broadcastSocket.accept()
                response = broadcastPeer.recv(1024).decode()
                command = response.split(" ")
                if (command[0] == "respondBroadcast" and command[1] != "empty"):
                    matching_clients.append(command[1])
        broadcastSocket.close()
        
        response_message = ""
        if matching_clients:
            # Construct the respondIP message with IP addresses
            response_message = "respondIP " + " ".join(matching_clients)
        else:
            response_message = "respondIP noFile"
        conClients.send(response_message.encode())
    else:
        print("Invalid command. Usage: fetchBroadcast <filename>")

def returnIP(message, connectingClients):
    pass

def serverReceive(connectSocket, address):
    while True:
        try:
            message = connectSocket.recv(1024).decode()
            if not message:
                break
            command = message.strip().split(" ")
            if (command[0] == "requestIP"):
                fetchBroadcast(message, connectSocket)
            elif command[0] == "respondPing":
                print(f"{command[1]} is up.")
            elif command[0] == "respondDiscover":
                if command[2] == "noFile":
                    print(f"{command[1]} local files: no file")
                else:
                    print(f"{command[1]} local files: {command[2]}")
            elif command[0] == "publish":
                print(f"{command[1]} publishes: {command[2]}")
        except ConnectionResetError:
            break
    connectingClients.remove(connectSocket)
    connectSocket.close()

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
    #host = socket.gethostname()
    host = '192.168.56.1'
    port = 12000

    serverSocket = socket.socket()
    serverSocket.bind((host, port))
    serverSocket.listen(MAX_CLIENTS)

    threadListen = threading.Thread(target=serverConnect, args=(serverSocket,))
    threadListen.start()

if __name__ == '__main__':
    serverProgram()
