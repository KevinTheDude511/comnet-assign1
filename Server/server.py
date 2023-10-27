import socket

def serverProgram():
    host = socket.gethostname()
    port = 5000

    # serverSocket = socket.socket() # --> create TCP welcome socket
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind((host, port)) # bind host and port
    serverSocket.listen(2) # number of possible clients

    connectSocket, address = serverSocket.accept() # accept new connection
    print("Connection from: " + str(address))

    while True:
        message = connectSocket.recv(1024).decode()
        if not message:
            break
        else:
            print("From client: " + message)
        #data = input(" -> ")
        #connectSocket.send(data.encode()) # send data back to client
    connectSocket.close()

if __name__ == '__main__':
    serverProgram()