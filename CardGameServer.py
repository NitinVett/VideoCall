import pickle
import socket
import sys
import threading

HEADER = 64
PORT = 5051
SERVER = "148.113.183.233"
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

with open('loginData.pkl', "rb") as f2:
    login_credentials = pickle.load(f2)
    """1st entry in value is users status (OFFLINE or ONLINE),
        2nd entry is their connection to the server(None if OFFLINE),
        3rd entry is their availability (FREE,RINGING,BUSY) and if they are busy or ringing the 2nd entry in the tuple will
        be the connection that is calling or in call with that user"""
    users = {user: ["OFFLINE", None, ("FREE", None)] for user in login_credentials}


def sendMessage(msg, conn, encode=True):
    message = msg
    send_length = str(len(message))
    send_length = send_length.encode(FORMAT)
    if encode:
        message = message.encode(FORMAT)

    send_length += b' ' * (HEADER - len(send_length))
    conn.send(send_length)
    conn.send(message)


def recvMessage(conn, decode=True):
    msg_length = conn.recv(HEADER).decode(FORMAT)

    msg_length = int(msg_length)
    msg1 = conn.recv(msg_length)
    if decode:
        msg1 = msg1.decode(FORMAT)
        msg1 = msg1.split(" ")
    return msg1


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    curruser = "$none$"
    connected = True
    while connected:
        msg = recvMessage(conn)

        if msg[0] == "~CALL~":

            if users[curruser][2][0] == "RINGING":
                sendMessage("YES", conn)
                users[curruser][2] = ("BUSY", users[curruser][2][1])
                videoCall(curruser)

        if msg[0] == "~SIGNUP~":
            if msg[1] not in login_credentials:
                login_credentials[msg[1]] = msg[2]
                with open('loginData.pkl', "wb") as f:
                    pickle.dump(login_credentials, f)
                sendMessage("SUCCESSFUL SIGNUP", conn)
            else:
                sendMessage("USERNAME TAKEN", conn)

        elif msg[0] == "~LOGIN~":
            if msg[1] in login_credentials:
                if msg[2] == login_credentials[msg[1]]:
                    curruser = msg[1]
                    users[curruser][0] = "ONLINE"
                    users[curruser][1] = conn

                    sendMessage("LOGIN SUCCESSFUL", conn)
            else:
                sendMessage("INVALID LOGIN", conn)
        elif msg[0] == "~SEARCH~":
            if msg[1] in users:
                if users[msg[1]][0] == "ONLINE":
                    users[msg[1]][2] = ("RINGING", conn)
                    while users[msg[1]][2][0] != "BUSY":
                        continue
                    sendMessage("CALLING", conn)
                    users[curruser][2] = ("BUSY", users[msg[1]][1])

                    videoCall(curruser)


            else:
                sendMessage("INVALID", conn)
        elif msg[0] == "~EXIT~":
            if curruser != "$none$":
                users[curruser][0] = "OFFLINE"
                users[curruser][1] = None
                users[curruser][2] = ("FREE", None)

            sendMessage("EXIT1", conn)
            break
        else:
            sendMessage("NONE", conn)


def videoCall(user):
    while True:

        msg = recvMessage(users[user][1], decode=False)[0]
        print(msg + "   " + user)
        if msg == "LEAVE":
            sendMessage("END", users[user][2][1])
            return "add something here"

        sendMessage(msg, users[user][2][1],encode=False)


def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(users)
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")


print("[STARTING] server is starting...")
start()
