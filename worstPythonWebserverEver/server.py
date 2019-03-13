#!/usr/bin/env python3


def main():
    import config
    import multiprocessing as mp
    (args, config, log) = config.main()
    serversocket = createSocket(config)
    while True:
        (clientsocket, address) = serversocket.accept()
        data = clientsocket.recv(1024)
        p = mp.Process(target=handleRequest, args=(args, config,
                                                   data, clientsocket))
        p.start()
        p.join()
    serversocket.close()


def createSocket(config):
    import socket
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # serversocket.bind((socket.gethostname(), 80))
    serversocket.bind((config['server_ipv4'], config['server_port']))
    # TODO: Wire up config here.
    serversocket.listen(5)
    return serversocket


def handleRequest(args, config, data, clientsocket):
    import receive
    clientsocket.setblocking(0)
    response = receive.main(args, config, data)
    clientsocket.send(response)
    clientsocket.close()
    return


if __name__ == '__main__':
    print("You are running this package incorrectly. RTFM.")
    exit(1)
