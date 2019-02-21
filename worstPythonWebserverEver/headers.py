#!/usr/bin/env python3


def main(config, status):
    import time
    headers = []
    timeFormat = 'Date: %a, %d %b %Y %H:%M:%S GMT'
    headers.append("HTTP/1.1 {0} {1}".format(status.code, status.message))
    headers.append("Server: worstPythonServerEver")
    headers.append("Location: {0}".format(config['server']['name']))
    headers.append(time.strftime(timeFormat, time.gmtime()))
    return headers


if __name__ == '__main__':
    print("You are running this package incorrectly. RTFM")
    exit(1)
