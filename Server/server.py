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

def fetchBroadcast(message, connectingClients):
    # Split the message into segments
    segments = message.split(" ")

    if len(segments) == 2:
        filename = segments[1]
        # Construct the requestBroadcast message
        broadcast_message = f"requestBroadcast {filename}"

        # Send the request to all connected clients
        for connectSocket in connectingClients:
            connectSocket.send(broadcast_message.encode())
    else:
        print("Invalid command. Usage: fetchBroadcast <filename>")

def returnIP(message, connectingClients):
    # Split the message into segments
    segments = message.split(" ")

    if len(segments) == 2:
        filename = segments[1]
        matching_clients = []

        # Find clients that have the file
        for connectSocket in connectingClients:
            connectSocket.send(f"requestIP {filename}".encode())
            response = connectSocket.recv(1024).decode()
            if response.startswith("respondIP"):
                ips = response.split(" ")[1:]
                matching_clients.extend(ips)

        if matching_clients:
            # Construct the respondIP message with IP addresses
            response_message = "respondIP " + " ".join(matching_clients)
        else:
            response_message = "respondIP noFile"

        # Send the response to the original client
        connectingClients[0].send(response_message.encode())
    else:
        print("Invalid command. Usage: returnIP <filename>")

def serverReceive(connectSocket, address):
    while True:
        try:
            message = connectSocket.recv(1024).decode()
            if not message:
                break
            command = message.strip().split(" ")
            print(f"{address}: {message}")
            #Prototype for finding correct file from clients connect to server
            #and return all IP of clients which have the file .
            if (command[0] == "requestIP"):
                connectSocket.send(("respondIP " + socket.gethostbyname(socket.gethostname())).encode())
            #   connectSocket.send(("respondIP " + socket.gethostbyname(socket.gethostname()) + " " + socket.gethostbyname(socket.gethostname()) + " " + socket.gethostbyname(socket.gethostname())).encode())
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
    serverProgram()
