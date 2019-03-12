#!/usr/bin/env python3


def main(config, method):
    methodsEnabled = config['methods']
    if method.upper() in [x.upper() for x in methodsEnabled]:
        (response, statusCode) = checkMethod(method.upper(), methodsEnabled)
    else:
        statusCode = 405
        response = "METHOD NOT ALLOWED"
    return response, statusCode


def checkMethod(method, methodsEnabled):
    statuscode = 'UNSET'
    if method == 'OPTIONS':
        statuscode = 200
        response = "Allow: {0}".format(' '.join(methodsEnabled).upper())
    elif method == 'HEAD':
        statuscode = 200
        response = ''
    elif method == 'GET':
        response = 'GET'
    elif method == 'POST':
        response = 'POST'
    elif method == 'PUT':
        response = 'PUT'
    elif method == 'DELETE':
        response = 'DELETE'
    else:
        response = 'INTERNAL SERVER ERROR'
        statuscode = 500
    return response, statuscode


if __name__ == '__main__':
    print("You are running this package incorrectly. RTFM.")
    exit(1)
