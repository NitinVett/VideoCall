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
    users = dict.fromkeys(login_credentials, "Offline")

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
                    users[curruser] = "Online"
                    conn.send("LOGIN SUCCESSFUL".encode(FORMAT))
            else:
                conn.send("INVALID LOGIN".encode(FORMAT))
        elif msg[0] == "~SEARCH~":
            if msg[1] in users:
                conn.send("SUCCESS".encode(FORMAT))
            else:
                conn.send("INVALID".encode(FORMAT))
        elif msg[0] == "~EXIT~":
            if curruser != "$none$":
                users[curruser] = "Offline"
            conn.send("EXIT1".encode(FORMAT))
            break
        else:
            conn.send("NONE".encode(FORMAT))

def videoCall(conn1,conn2):
    connected = True
    while connected:
        msg1 = recvMessage(conn1)
        msg2 = recvMessage(conn2)



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
