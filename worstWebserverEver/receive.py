#!/usr/bin/env python3


def main(rawreq):
    # Request parsing
    req = str(rawreq, "utf-8").split(' ')
    method = req[0]
    (response, statusCode) = checkMethod(method)
    body = ''
    if not response:
        uri = req[1]
        body = getFiles(uri)
    header ="""HTTP/1.1 {0} OK \r
Server: worstWebserverEver\r""".format(statusCode)
    response = "{0}\n\n{1}".format(header, body)
    data = str.encode(response, 'utf-8')
    return data


def checkMethod(method):
    acceptedMethods = ["options", "head", "get"]
    if method.lower() in acceptedMethods:
        myMethod = method.upper()
        statusCode = 200
        if myMethod == 'OPTIONS':
            response = "Allow: OPTIONS, HEAD, GET"
        elif myMethod == 'HEAD':
            response = True
        elif myMethod == 'GET':
            response = False
    else:
        statusCode = 503
        response = "METHOD NOT AVAILABLE"
    return response, statusCode


def getFiles(uri):
    if uri.split('/')[-1].split('.')[-1] != 'html':
       uri = "{0}index.html".format(uri)
       print(uri)
    with open(".{0}".format(uri), 'r') as newfile:
        body = newfile.read()
    return body


if __name__ == '__main__':
    print("You are running this package incorrectly. RTFM")
    exit(1)
