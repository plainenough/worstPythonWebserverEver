#!/usr/bin/env python3


def main():
    serversocket = createSocket()
    # TODO: add configuration import
    while True:
        (clientsocket, address) = serversocket.accept()
        # mySocket(clientsocket)
        rawreq = clientsocket.recv(1024)
        req = str(rawreq, "utf-8").split(' ')
        method = req[0]
        uri = req[1]
        addr = "{0}:{1}".format(address[0], address[1])
        print("Connection from: {0} - {1}  --  {2}".format(addr, method, uri))
        response = """\
HTTP/1.1 200 OK

Hello, World!
"""
        clientsocket.sendall(str.encode(response))
        clientsocket.close()


def createSocket():
    import socket
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # serversocket.bind((socket.gethostname(), 80))
    serversocket.bind(('', 80))
    # TODO: Wire up config here.
    serversocket.listen(5)
    return serversocket


if __name__ == '__main__':
    print("You are running this package incorrectly, rtfm.")
