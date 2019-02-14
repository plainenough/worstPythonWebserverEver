#!/usr/bin/env python3


def main():
    serversocket = createSocket()
    #import socket
    #serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #serversocket.bind((socket.gethostname(), 80))
    #serversocket.bind(('', 80))
    #TODO: Wire up config here.
    #serversocket.listen(5)
    #TODO: add configuration import
    while True:
        (clientsocket, address) = serversocket.accept()
        clientsocket.run()


def createSocket():
    import socket
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #serversocket.bind((socket.gethostname(), 80))
    serversocket.bind(('', 80))
    #TODO: Wire up config here.
    serversocket.listen(5)
    return serversocket


if __name__ == '__main__':
    print("You are running this package incorrectly, rtfm.")
