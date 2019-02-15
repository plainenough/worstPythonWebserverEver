#!/usr/bin/env python3


def main(rawreq):
    # Request parsing
    # TODO: rework how headers are generated.
    # this primitive header handling suits my current needs
    req = str(rawreq, "utf-8").split(' ')
    method = req[0]
    (response, statusCode) = checkMethod(method)
    body = ''
    if not response:
        uri = req[1]
        (body, statusCode) = getFiles(uri, statusCode)
    header = """HTTP/1.1 {0} OK \r
Server: worstWebserverEver\r""".format(statusCode)
    response = "{0}\n\n{1}".format(header, body)
    data = str.encode(response, 'utf-8')
    return data


def checkMethod(method):
    # TODO: Add config for enabled method.
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
        statusCode = 405
        response = "METHOD NOT ALLOWED"
    return response, statusCode


def getFiles(uri, statusCode):
    # TODO:  add templated files for return
    if uri.split('/')[-1].split('.')[-1] != 'html':
        uri = "{0}index.html".format(uri)
    try:
        with open(".{0}".format(uri), 'r') as newfile:
            body = newfile.read()
    except FileNotFoundError as e:
        statusCode = 404
        body = "<html><body><p>404 - File not Found \
                </p></body></html>"
    except IOError as e:
        statusCode = 403
        body = "<html><body><p>403 - Not Authorized \
                </p></body></html>"
    except Exception as e:
        statusCode = 500
        body = "<html><body><p>500 - internal server error \
                </p></body></html>"
    return body, statusCode


if __name__ == '__main__':
    print("You are running this package incorrectly. RTFM")
    exit(1)
