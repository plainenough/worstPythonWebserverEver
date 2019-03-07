#!/usr/bin/env python3


def main(args, config, rawreq):
    import method
    import headers
    req = str(rawreq, "utf-8").split(' ')
    myMethod = req[0]
    (response, statusCode) = method.main(config, myMethod)
    body = ''
    if response == 'GET':
        uri = req[1]
        (body, statusCode) = getFiles(config, uri, statusCode)
    myHeaders = headers.main(config, statusCode)
    header = '\r\n'.join(myHeaders)
    response = "{0}\r\n\r\n{1}".format(header, body)
    data = str.encode(response, 'utf-8')
    return data


def getFiles(config, uri, statusCode):
    path = config['webroot']
    file_ext = uri.split('/')[-1].split('.')[-1]
    request = '{0}{1}'.format(path, uri)
    body = ""
    if file_ext not in config['file_ext']:
        request = checkFiles(config, request)
    elif file_ext == '/':
        request = checkFiles(config, request)
    if request:
        try:
            with open(request, 'r') as newfile:
                statusCode = 200
                body = newfile.read()
        except FileNotFoundError:
            statusCode = 404
        except IOError:
            statusCode = 403
        except Exception:
            statusCode = 500
    else:
        statusCode = 404
    if statusCode != 200:
        try:
            errorPath = config['error_pages'][statusCode]
            if config['custom_error_pages'] == False:
                errorPath = "{0}/{1}".format(config['server_working_dir'],
                                             errorPath)
            with open(errorPath, 'r') as errorDoc:
                body = errorDoc.read()
        except Exception:
            body = 'EMPTY ERROR PAGE RESPONSE'
    return body, statusCode


def checkFiles(config, request):
    import os
    for i in config['default_indexes']:
        if os.path.isfile("{0}{1}".format(request, i)):
            uri = "{0}{1}".format(request, i)
            return uri
    return False


if __name__ == '__main__':
    print("You are running this package incorrectly. RTFM")
    exit(1)
