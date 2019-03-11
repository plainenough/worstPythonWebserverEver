#!/usr/bin/env python3


def main():
    import server as myServer
    import sys
    try:
        myServer.main()
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == '__main__':
    main()
