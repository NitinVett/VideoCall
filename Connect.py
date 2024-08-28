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

    def recvLargeMessage(self, msg_length):
        buffer_size = 4096
        total_length = int(msg_length)
        data = b''  # to store the full message in bytes

        while len(data) < total_length:
            packet = self.client.recv(buffer_size)  # receive data in chunks
            if not packet:
                break  # if the connection is closed, break
            data += packet
            if total_length - len(data) < 4096:
                buffer_size = total_length - len(data)
        return data

    def send(self, msg, encode=True,receive = True):
        message = msg

        send_length = str(len(message))

        send_length = send_length.encode(self.FORMAT)
        if encode:
            message = message.encode(self.FORMAT)

        send_length += b' ' * (self.HEADER - len(send_length))
        self.client.sendall(send_length)

        self.client.sendall(message)
        if receive:
            response = self.receive()
            if encode:
                response = response.decode(self.FORMAT)
            return response


    def receive(self):
        msg_length = self.client.recv(self.HEADER).decode(self.FORMAT)

        msg_length = int(msg_length)

        if msg_length > 4096:
            response = self.recvLargeMessage(msg_length)
        else:
            response = self.client.recv(msg_length)

        return response