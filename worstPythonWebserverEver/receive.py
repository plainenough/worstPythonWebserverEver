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


def getFiles(config, uri, statusCode):
    # TODO:  add templated files for return
    file_ext = uri.split('/')[-1].split('.')[-1]
    if file_ext not in config['defaults']['file_ext']:
        uri = deckFiles(config, uri)
    if uri:
        try:
            with open(uri, 'r') as newfile:
                statusCode = 200
                body = newfile.read()
        except IOError as e:
            statusCode = 403
        except Exception as e:
            statusCode = 500
    else:
        statusCode = 404
    if body == '':
        try:
            errorPath = config['defaults']['error_pages'][statusCode]
            with open(errorPath, 'r') as errorDoc:
                body = errorDoc.read()
        except Exception:
            body = 'EMPTY ERROR STRING'
    return body, statusCode


def checkFiles(config, uri):
    import os
    for i in config['default']['indexes']:
        if os.path.isfile("{0}{1}".format(uri, i)):
            uri = "{0}{1}".format(uri, i)
            return uri
    return False


if __name__ == '__main__':
    print("You are running this package incorrectly. RTFM")
    exit(1)
