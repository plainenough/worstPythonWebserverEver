#!/usr/bin/env python3


def main(args, config, rawreq):
    import method
    import headers
    # Request parsing
    # TODO: rework how headers are generated.
    # this primitive header handling suits my current needs
    req = str(rawreq, "utf-8").split(' ')
    myMethod = req[0]
    (response, statusCode) = method.main(myMethod)
    body = ''
    if response == 'GET':
        uri = req[1]
        (body, statusCode) = getFiles(uri, statusCode)
    myHeaders = headers.main(config, status)
    header = '\r'.join(myHeaders)
    response = "{0}\n\n{1}".format(header, body)
    data = str.encode(response, 'utf-8')
    return data


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
