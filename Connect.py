import socket


class Connect:

    def __init__(self):
        self.user = "$None$"
        self.HEADER = 64
        self.PORT = 5051
        self.FORMAT = 'utf-8'
        self.DISCONNECT_MESSAGE = "!DISCONNECT"
        self.SERVER = "148.113.183.233"
        self.ADDR = (self.SERVER, self.PORT)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.client.connect(self.ADDR)

    def send(self, msg,encode = True):
        message = msg
        print(message)
        send_length = str(len(message))
        print(send_length)
        send_length = send_length.encode(self.FORMAT)
        if encode:
            message = message.encode(self.FORMAT)


        send_length += b' ' * (self.HEADER - len(send_length))
        self.client.send(send_length)
        self.client.send(message)

        msg_length = self.client.recv(self.HEADER).decode(self.FORMAT)
        msg_length = int(msg_length)
        response = self.client.recv(msg_length)
        if encode:
            response = response.decode(self.FORMAT)
        return response