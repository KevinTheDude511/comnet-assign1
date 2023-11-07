import socket
import os
import shutil
import threading
import random

# Copy the absolute path
sourcePath = "C:/Users/Dell/Desktop/Files/BK năm ba/Computer Network (Lab)/Assignment_1/Code/"

connectStatus = False
clientAddress = None
filename = ""

broadcast_port = 10000

def getAllFiles():
    localRepo = "./LocalRepo"
    fileList = []
    for file in os.listdir(localRepo):
        filePath = os.path.join(localRepo, file)
        if os.path.isfile(filePath):
            fileList.append(file)
    return fileList
   
def getFile():
    fileList = getAllFiles()
    if fileName in fileList:
        return "LocalRepo/" + fileName
    else:
        return "Fail"

def searchFile(fileName):
    fileList = getAllFiles()
    if fileName in fileList:
        return True
    else:
        return False

def returnBroadcast(fileName, clientSocket):
    global clientAddress
    message = "respondBroadcast "
    if searchFile(fileName):
        message += clientAddress
    else:
        message += "empty"
    try:
        returnbroadSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        returnbroadSocket.connect((clientSocket.getpeername()[0],10000))
        returnbroadSocket.send(message.encode())
    except ConnectionAbortedError:
        pass
    returnbroadSocket.close()

def connectFetchClient(addr):
    global filename
    # connect client by ip?
    inp = random.randint(0, len(addr) - 1)
    address = addr[inp].split(":")
    
    fetchsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    fetchsocket.connect((address[0], int(address[1])))
    fetchsocket.send(("requestFile " + filename).encode())
    newfile = open("LocalRepo/" + filename, "wb")
    try:
        print("Receiving file, please wait")
        r = fetchsocket.recv(1024)
        while (r):
            newfile.write(r)
            r = fetchsocket.recv(1024)
        newfile.close()
        print("Receive file!")
        fetchsocket.close()
        return True
    except ConnectionAbortedError:
        print("Fail to receive file due to abrupt disconnection from other client.")
        os.remove("LocalRepo/" + filename)
        fetchsocket.close()
        return False
    
def returnFetchClient(reqclient):
    # send file over socket?
    # real code
    message = reqclient.recv(1024).decode()
    message = message.split(" ")
    f = open("LocalRepo/" + message[1], "rb")
    # testing code
    #f = open(command[1], "rb")
    try:
        print("Sending file, please wait")
        reqclient.sendall(f.read())  
        f.close()
        print("File send!")
        reqclient.close()
        return True
    except ConnectionAbortedError:
        print("Fail to send file due to abrupt disconnection from other client.")
        reqclient.close()
        return False

def publish(fileLocation, newFileName, clientSocket):
    oldPath = sourcePath + fileLocation
    newPath = sourcePath + "Client1/LocalRepo/" + newFileName + ".txt"
    try:
        shutil.copy(oldPath, newPath)
    except FileNotFoundError:
        print("File not found.")
    message = "publish " + newFileName + ".txt"
    clientSocket.send(message.encode())

def fetchIP(fileName, clientSocket):
    # 1.1/ Send request fetch to server
    clientSocket.send(("requestIP " + fileName).encode())
    # 1.4/ Server sends IP back to client
    # message = clientSocket.recv(1024).decode()
    # message = message.split()
    # print(message)
    
def respondDiscover(clientSocket):
    message = "respondDiscover "
    fileList = getAllFiles()
    for file in fileList:
        message += file + ","
    message = message[:-1] # remove the final comma
    clientSocket.send(message.encode())

def respondPing(clientSocket):
    message = "respondPing " + clientAddress
    clientSocket.send(message.encode())

def sendMessage(messageSegments, clientSocket):
    messageSegments = messageSegments[1:]
    message = ""
    for messageSegment in messageSegments:
        message += messageSegment + " "
    message = message[:-1]
    clientSocket.send(message.encode())

def clientReceive(clientSocket):
    global connectStatus, clientAddress
    while connectStatus:
        """
        message = clientSocket.recv(1024).decode()
        if not message:
            break
        print("From server: " + message)
        """
        try:
            message = clientSocket.recv(1024).decode()
            # use for debugging purpose
            # print("From server: " + message)
            message = message.split()
            if message[0] == "clientAddress":
                clientAddress = message[1]
            elif message[0] == "requestBroadcast":
                returnBroadcast(message[1], clientSocket)
            elif message[0] == "respondIP":
                if message[1] == "noFile":
                    print("No online client have " + filename)
                else:
                    connectFetch_thread = threading.Thread(target=connectFetchClient, args=(message[1:],))
                    connectFetch_thread.start()
            elif message[0] == "requestDiscover":
                respondDiscover(clientSocket)
            elif message[0] == "requestPing":
                respondPing(clientSocket)
        except ConnectionAbortedError:
            connectStatus = False
            break
        except ConnectionResetError:
            connectStatus = False
            break
    clientSocket.close()

def clientSend(clientSocket):
    global connectStatus, clientAddress, filename
    while connectStatus:
        message = input()
        if (not(connectStatus)):
            break
        message = message.strip().split()
        if (len(message) > 0):
            if message[0] == "exit" and len(message) == 1:
                connectStatus = False
                break
            elif message[0] == "publish" and len(message) == 3:
                publish(message[1], message[2], clientSocket)
            elif message[0] == "fetch" and len(message) == 2:
                # 1/ Contact server
                # ip = fetchIP(message[1], clientSocket)
                filename = message[1]
                fetchIP(message[1], clientSocket)
                # if not IP:
                    # print("No online client have " + message[1])
                    # continue
                # 2/ Contact client
                # 2.1/ Send request fetch to client (using port?)
                # print("F")
                # connectFetchClient(ip, clientSocket, message[1])
                # 2.2/ Client search for file in repo
                # 2.3/ Send file back to requesting client
            elif message[0] == "message":
                sendMessage(message, clientSocket)
            elif message[0] == "files":
                fileList = getAllFiles()
                for file in fileList:
                    print(file + " ")
            elif message[0] == "search" and message[1]:
                if searchFile(message[1]):
                    print("There is file")
                else:
                    print("There is no file")
            elif message[0] == "clientAddress":
                print(clientAddress)
            else:
                print("Invalid command")
        else:
            print("Invalid command")
    endSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    endSocket.connect(clientSocket.getsockname())
    endSocket.close()
    clientSocket.close()

def clientListen(listenSocket):
    while connectStatus:
        listenSocket.listen(5)
        reqclient, reqclient_addr = listenSocket.accept()
        if (not(connectStatus)):
            break
        returnthread = threading.Thread(target = returnFetchClient, args = (reqclient,))
        returnthread.start()
        
def clientProgram():
    global connectStatus
    host = socket.gethostname()
    port = 12000
    random.seed()
       
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((host, port))
    connectStatus = True

    threadSend = threading.Thread(target=clientSend, args=(clientSocket,))
    threadSend.start()

    threadReceive = threading.Thread(target=clientReceive, args=(clientSocket,))
    threadReceive.start()
    
    listenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listenSocket.bind(clientSocket.getsockname())
    threadListen = threading.Thread(target = clientListen, args=(listenSocket,))
    threadListen.start()

if __name__ == '__main__':
    clientProgram()
