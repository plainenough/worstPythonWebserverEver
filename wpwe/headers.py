#!/usr/bin/env python3


def main(config, statusCode):
    import time
    headers = []
    if statusCode == 'UNSET':
        statusCode = 500
    statusMessage = {200: 'OK', 404: 'NotFound',
                     500: 'InternalServerError',
                     403: 'NotAuthorized',
                     405: 'MethodNotAllowed'}
    timeFormat = 'Date: %a, %d %b %Y %H:%M:%S GMT'
    headers.append("HTTP/1.1 {0} {1}".format(statusCode,
                   statusMessage[statusCode]))
    headers.append("Server: worstPythonWebserverEver")
    headers.append("Action: Jackson")
    headers.append("Location: {0}".format(config['server_name']))
    headers.append(time.strftime(timeFormat, time.gmtime()))
    return headers


if __name__ == '__main__':
    print("You are running this package incorrectly. RTFM")
    exit(1)
