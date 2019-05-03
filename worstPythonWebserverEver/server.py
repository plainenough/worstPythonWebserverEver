#!/usr/bin/env python3
import socket

def main():
    import config
    import multiprocessing as mp
    (args, config, log) = config.main()
    serversocket = createSocket(config)
    while True:
        (clientsocket, address) = serversocket.accept()
        p = mp.Process(target=handleRequest, args=(args, config, clientsocket))
        p.start()
        p.join()
        print(mp.active_children())
    serversocket.close()
    return


def createSocket(config):
    import socket
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind((config['server_ipv4'], config['server_port']))
    serversocket.listen(1)
    return serversocket


def handleRequest(args, config, clientsocket):
    import receive
    clientsocket.setblocking(0)
    data = clientsocket.recv(1024)
    response = receive.main(args, config, data)
    clientsocket.send(response)
    clientsocket.shutdown(socket.SHUT_RDWR)
    clientsocket.close()
    del clientsocket
    return


if __name__ == '__main__':
    print("You are running this package incorrectly. RTFM.")
    exit(1)
