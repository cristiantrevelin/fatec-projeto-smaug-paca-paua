import socket


class Connection:
    def __init__(self, port):

        self.host = socket.gethostname()
        self.port = port
        self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = (self.host, self.port)
        self.buff = 1024
        self.connected = None

        self.connect()

    def connect(self):

        try:
            self.client_sock.connect(self.server)
            self.connected = True
            return self.client_sock.recv(self.buff).decode()

        except Exception as e:
            print(e)
            self.connected = False

    def send(self, data):

        try:
            self.client_sock.send(str(data).encode())

        except Exception as e:
            print(e)

    def receive(self):
        return self.client_sock.recv(self.buff).decode()
