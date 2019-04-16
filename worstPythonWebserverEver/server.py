#!/usr/bin/env python3


def main():
    import config
    import multiprocessing as mp
    (args, config, log) = config.main()
    serversocket = createSocket(config)
    while True:
        (csock, addr) = serversocket.accept()
        #data = csock.recv(1024)
        p = mp.Process(target=handleRequest, args=(args, config,
                                                   csock, addr))
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


def handleRequest(args, config, csock, addr):
    import receive
    print("Connection from {0}".format(addr))
    data = csock.recv(1024)
    csock.setblocking(False)
    response = receive.main(args, config, data)
    csock.sendall(response)
    csock.close()
    return False


if __name__ == '__main__':
    print("You are running this package incorrectly. RTFM.")
    exit(1)
