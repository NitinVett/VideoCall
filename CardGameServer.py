import pickle
import socket
import sys
import threading

# CONSTANTS
HEADER = 64
PORT = 5051
SERVER = "148.113.183.233"
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind(ADDR)

# loading user information from our pickle file
with open('loginData.pkl', "rb") as f2:
    login_credentials = pickle.load(f2)
    """1st entry in value is users status (OFFLINE or ONLINE),
        2nd entry is their connection to the server(None if OFFLINE),
        3rd entry is their availability (FREE,RINGING,BUSY) and if they are busy or ringing the 2nd entry in the tuple will
        be the connection that is calling or in call with that user"""
    users = {user: ["OFFLINE", None, ("FREE", None)] for user in login_credentials}


# sends message to given socket
def sendMessage(msg, conn, encode=True):
    message = msg

    # gets the length of the message
    send_length = str(len(message))
    send_length = send_length.encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))

    # encodes message unless encode is set to false
    if encode:
        message = message.encode(FORMAT)

    # sends the length of the message and then the actual message
    conn.sendall(send_length)
    conn.sendall(message)


# function to receive messages larger than 4096 bytes
def recvLargeMessage(conn, msg_length):
    buffer_size = 4096
    total_length = int(msg_length)
    data = b''

    # receives the message in 4096 byte chunks until the message is fully received
    while len(data) < total_length:
        packet = conn.recv(buffer_size)
        if not packet:
            break
        data += packet
        if total_length - len(data) < 4096:
            buffer_size = total_length - len(data)
    return data


# function for receiving messages from a connection
def recvMessage(conn, decode=True):
    # looks to receive the size of the incoming message
    msg_length = conn.recv(HEADER).decode(FORMAT)
    msg_length = int(msg_length)

    # uses recvLargeMessage for messages greater than 4096 bytes in size
    if msg_length > 4096:
        msg1 = recvLargeMessage(conn, msg_length)
    else:
        msg1 = conn.recv(msg_length)

    # will decode unless decode is set to false
    if decode:
        msg1 = msg1.decode(FORMAT)
        msg1 = msg1.split(" ")
    return msg1


# main function to handle each individual connection
def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    curruser = "$none$"
    connected = True

    # receives and responds to commands
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


# will take camera information from users in calls and send it to their recipient
def videoCall(user):
    while True:

        msg = recvMessage(users[user][1], decode=False)
        if msg == "LEAVE":
            sendMessage("END", users[user][2][1])
            return "add something here"

        sendMessage(msg, users[user][2][1], encode=False)


# starts server and listens for connections
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
