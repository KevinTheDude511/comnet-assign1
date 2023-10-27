import socket
import os
import shutil

# Copy the absolute path
sourcePath = "C:/Users/Dell/Desktop/Files/BK năm ba/Computer Network (Lab)/Assignment_1/Code/"

def getAllFiles():
    localRepo = sourcePath + "Client1/LocalRepo"
    fileList = []
    for file in os.listdir(localRepo):
        filePath = os.path.join(localRepo, file)
        if os.path.isfile(filePath):
            fileList.append(file)
    return fileList

def searchFile(fileName):
    fileList = getAllFiles()
    if fileName in fileList:
        return True
    else:
        return False

def returnBroadcast(fileName, clientSocket):
    message = "respondBroadcast "
    if searchFile(fileName):
        message += "<MY_IP>"
    else:
        message += "empty"
    clientSocket.send(message.encode())

def connectFetchClient(ip):
    # connect client by ip?
    return True

def returnFetchClient():
    # send file over socket?
    return True

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
    message = "requestIP " + fileName
    clientSocket.send(message.encode())
    # 1.4/ Server sends IP back to client
    message = clientSocket.recv(1024).decode()
    message = message.split()
    if message[0] == respondIP and message[1] == "noFile":
        return None
    elif message[0] == respondIP:
        return message[1]
    else:
        raise ValueError("fetchIP: wrong message received")

def respondDiscover(clientSocket):
    message = "respondDiscover "
    fileList = getAllFiles()
    for file in fileList:
        message += file + ","
    message = message[:-1] # remove the final comma
    clientSocket.send(message.encode())

def respondPing(clientSocket):
    message = "respondPing" + "<MY_IP>"
    clientSocket.send(message.encode())

def sendMessage(messageSegments, clientSocket):
    messageSegments = messageSegments[1:]
    message = ""
    for messageSegment in messageSegments:
        message += messageSegment + " "
    message = message[:-1]
    clientSocket.send(message.encode())

def clientProgram():
    host = socket.gethostname()
    port = 5000

    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((host, port))

    while True:
        message = input("-> ")
        message = message.strip().split()
        if message[0].lower() == "exit":
            break
        elif message[0].lower() == "publish" and message[1] and message[2]:
            publish(message[1], message[2], clientSocket)
        elif message[0].lower() == "fetch" and message[1]:
            # 1/ Contact server
            ip = fetchIP(message[1], clientSocket)
            if not IP:
                print("No online client have " + message[1])
                continue
            # 2/ Contact client
            # 2.1/ Send request fetch to client (using port?)
                connectFetchClient(ip)
            # 2.2/ Client search for file in repo --> definitely use thread here
            # 2.3/ Send file back to requesting client
        elif message[0].lower() == "message":
            sendMessage(message, clientSocket)
        elif message[0].lower() == "files":
            fileList = getAllFiles()
            for file in fileList:
                print(file + " ")
        elif message[0].lower() == "search" and message[1]:
            if searchFile(message[1]):
                print("There is file")
            else:
                print("There is no file")
        else:
            print("Invalid command")
    clientSocket.close()

if __name__ == '__main__':
    clientProgram()