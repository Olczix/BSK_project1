import config
import socket
import threading


class Connection:
    def __init__(self):
        (self.connection, self.address) = (0, 0)

    def listen(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', config.PORT))
        s.listen(5)
        while True:
            self.connection, self.address = s.accept()
            print(f'Connected with {self.address[0]}')

    def send(self, message):
        try:
            self.connection.send(message.encode('utf-8'))
        except:
            if self.connection == 0:
                print(f'Client {config.CLIENT} not available')

    def receive(self):
        s = socket.socket().connect((config.CLIENT, config.PORT))
        print(s.recv(1024))

    def close_connection(self):
        self.connection.close()


class ListenningThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        Connection().listen()
