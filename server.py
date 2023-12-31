import socket
from config import SIZE, HOST, server_name
from select import select
from colorama import Fore, Style


class Server:
    # Server initializing
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(HOST)
        self.server_socket.listen()
        self.sockets = [self.server_socket]
        self.clients = {}

    # Accepting a connection
    def accept_connection(self):
        client, addr = self.server_socket.accept()
        client.send(f"You connected to - {server_name}\r\n".encode())
        client.send(b"Enter your name: ")
        print("Connection with -", addr, end=": ")

        # Entering a name
        name = b""
        try:
            while True:
                chunk = client.recv(SIZE)
                if not chunk:
                    break
                name += chunk

                if b"\r\n" in chunk:
                    break
        except socket.error as ex:
            print(ex)
            client.send(f"{Fore.RED}{ex}{Style.RESET_ALL}".encode())

        # Adding a new client
        self.clients[client] = name.decode("UTF-8")
        self.sockets.append(client)

        # Sending message when a new user joins a chat
        if len(self.sockets) > 2:
            for _socket in self.sockets:
                if _socket is not self.server_socket and _socket is not client:
                    message = f" {Fore.GREEN} Connected - ".encode() + name + Style.RESET_ALL.encode()
                    _socket.send(message)
        # If the first user connects
        else:
            self.sockets[1].send(b"You're the first user in this chat\r\n")

        print(self.clients[client])

    # Receiving a message
    def receive_message(self, _socket):
        msg = b""
        try:
            while True:
                chunk = _socket.recv(SIZE)
                if not chunk:
                    break
                msg += chunk

                # If the "Enter" key is pressed
                if b"\r\n" in chunk:
                    break
        except socket.error as ex:
            print(ex)
            _socket.send(f"{Fore.RED}{ex}{Style.RESET_ALL}".encode())

        if not msg:
            self.sockets.remove(_socket)
            return

        # If the message is empty
        if msg.strip() != b"":
            for client in self.sockets:
                if client is not _socket and client is not self.server_socket:
                    client.send(f"{Fore.GREEN + self.clients[_socket].strip() + Style.RESET_ALL}: ".encode() + msg)

    # An endless loop of processing connections and sending messages
    def event_loop(self):
        while True:
            try:
                rs, _, xs = select(self.sockets, [], self.sockets)

                # Reading sockets
                for _socket in rs:
                    # If a new user connects
                    if _socket is self.server_socket:
                        self.accept_connection()
                    # If the user sends a message
                    else:
                        self.receive_message(_socket)

                # Sockets with errors
                for _socket in xs:
                    self.sockets.remove(_socket)
                    del self.clients[_socket]

            except socket.error as ex:
                print(ex)

    def start(self):
        print("Server listening!")
        self.event_loop()
