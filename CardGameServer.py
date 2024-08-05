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
    users = dict.fromkeys(login_credentials, ["OFFLINE", None,("FREE",None)])



def recvMessage(conn):
    msg_length = conn.recv(HEADER).decode(FORMAT)

    msg_length = int(msg_length)
    msg1 = conn.recv(msg_length).decode(FORMAT)
    msg1 = msg1.split(" ")
    return msg1


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    curruser = "$none$"
    connected = True
    while connected:
        msg = recvMessage(conn)
        if msg[0] == "~CALL~":
            if users[curruser][0] == "RINGING":
                videoCall(conn,users[curruser][2][1])


        if msg[0] == "~SIGNUP~":
            if msg[1] not in login_credentials:
                login_credentials[msg[1]] = msg[2]
                with open('loginData.pkl', "wb") as f:
                    pickle.dump(login_credentials, f)
                conn.send("SUCCESSFUL SIGNUP".encode(FORMAT))
            else:
                conn.send("USERNAME TAKEN".encode(FORMAT))

        elif msg[0] == "~LOGIN~":
            if msg[1] in login_credentials:
                if msg[2] == login_credentials[msg[1]]:
                    curruser = msg[1]
                    users[curruser] = ["ONLINE", conn]
                    conn.send("LOGIN SUCCESSFUL".encode(FORMAT))
            else:
                conn.send("INVALID LOGIN".encode(FORMAT))
        elif msg[0] == "~SEARCH~":
            if msg[1] in users:
                if users[msg[1]][0] == "ONLINE":
                    conn.send("CALLING".encode(FORMAT))
                    users[msg[1]][2][1] = "RINGING"
                    users[msg[1]][2][0] = conn


            else:
                conn.send("INVALID".encode(FORMAT))
        elif msg[0] == "~EXIT~":
            if curruser != "$none$":
                users[curruser] = ["Offline", None]
            conn.send("EXIT1".encode(FORMAT))
            break
        else:
            conn.send("NONE".encode(FORMAT))


def videoCall(conn1, conn2):
    while True:
        messages = []
        for conn in [conn1, conn2]:
            msg = recvMessage(conn)
            if (msg == "LEAVE"):
                return "add something here"
            messages.append(msg)

        conn1.send(msg[1])
        conn2.send(msg[0])


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
