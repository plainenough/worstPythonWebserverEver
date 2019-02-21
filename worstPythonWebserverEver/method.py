#!/usr/bin/env python3


def main(config, method):
    if config['server']['methods']:
        methodsEnabled = config['server']['methods']
    else:
        methodsEnabled = ["OPTIONS", "HEAD", "GET"]
    if method.upper() in [x.upper() for x in methodsEnabled]:
        (response, statusCode) = checkMethod(method)
    else:
        statusCode = 405
        response = "METHOD NOT ALLOWED"
    return response, statusCode


def checkMethod(method):
    statuscode = 'UNSET'
    if myMethod == 'OPTIONS':
        statusecode = 200
        response = "Allow: {0}".format(' '.join(methodsEnabled).upper())
    elif myMethod == 'HEAD':
        statuscode = 200
        response = False
    elif myMethod == 'GET':
        response = 'GET'
    elif myMethod = 'POST':
        response = 'POST'
    elif myMethod == 'PUT':
        response = 'PUT'
    elif myMethod = 'DELETE':
        response = 'DELETE'
    else:
        response = 'INTERNAL SERVER ERROR'
        statuscode = 500
    return response, statuscode


if __name__ == '__main__':
    print("You are running this package incorrectly. RTFM.")
    exit(1)
