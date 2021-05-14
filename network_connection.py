import config
import socket
import threading
import logic_connection
import backend


class NetworkConnection:
    def __init__(self, ip_address):
        (self.connection, self.address) = (0, ip_address)

    def send(self, message):
        try:
            destination_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            destination_socket.connect((self.address, config.PORT))
            # destination_socket.send(message.encode('utf-8'))
            destination_socket.send(message)
            destination_socket.close()
        except:
            if self.connection == 0:
                print(f'Client {config.ADDRESS} not available')

    def close_connection(self):
        self.connection.close()


class ListenningThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        (self.connection, self.address) = (0, 0)

    def run(self):
        self.listen()

    def listen(self):
        listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listening_socket.bind(('', config.PORT))
        listening_socket.listen(5)
        while True:
            self.connection, self.address = listening_socket.accept()
            print(f'Connected with {self.address[0]}')
            received_msg = self.connection.recv(config.PACKAGE_SIZE)
            if not received_msg:
                break
            else:
                backend.handle_received_message(received_msg,self.address[0]) 
