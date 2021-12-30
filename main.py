import socket
import sys
import traceback
import os
from obj import mimetypes


def response_ok(body, mimetype, status=b"OK", code=b"200"):
    """
    returns a basic HTTP response
    """
    response = ''
    response += 'HTTP/1.1 {} {}\r\n'.format(status, code)
    response += 'Content-Type:{}\r\n'.format(mimetype)
    response += '\r\n'
    if body:
        name, isDir = body
        if isDir:
            response += '{}\r\n'.format('\n'.join(
                [file for file in os.listdir(name) if file != os.path.basename(__file__)]))
            return response
        else:
            file = open(name, "rb").read()
            response += '{}\r\n'.format(file)
            return response
    response += '{}\r\n'.format('\n'.join(
        [file for file in os.listdir(".") if file != os.path.basename(__file__)]))
    return response


def response_method_not_allowed(mimetype=b"text/plain", status=b"OK", code=b"405"):
    """Returns a 405 Method Not Allowed response"""
    response = ''
    response += 'HTTP/1.1 {} {}\r\n'.format(status, code)
    response += 'Content-Type:{}\r\n'.format(mimetype)
    response += '\r\n'
    response += '405 Error Not Allowed\r\n'
    return response


def response_not_found(body, mimetype=b"text/plain", status=b"OK", code=b"405"):
    """Returns a 404 Not Found response"""
    response = ''
    response += 'HTTP/1.1 {} {}\r\n'.format(status, code)
    response += 'Content-Type:{}\r\n'.format(mimetype)
    response += '\r\n'
    response += '{} was not found. Please try again\r\n'.format(
        body)
    return response


def parse_request(request):
    """
    Given the content of an HTTP request, returns the path of that request.
    This server only handles GET requests, so this method shall raise a
    NotImplementedError if the method of the request is not GET.
    """
    filename = request.split("GET")[1].split("HTTP")[0].strip()
    if filename == "/" or filename == "/favicon.ico" or ".ico" in filename:
        return None
    else:
        return filename[1:], os.path.isdir(filename[1:])


def response_path(filename):
    """
    This method should return appropriate content and a mime type.
    If the requested path is a directory, then the content should be a
    plain-text listing of the contents with mimetype `text/plain`.
    If the path is a file, it should return the contents of that file
    and its correct mimetype.
    If the path does not map to a real location, it should raise an
    exception that the server can catch to return a 404 response.
    Ex:
        response_path('/a_web_page.html') -> (b"North Carolina...",
                                            b"text/html")
        response_path('/images/sample_1.png')
                        -> (b"A12BCF...",  # contents of sample_1.png
                            b"image/png")
        response_path('/') -> (b"images/, a_web_page.html, make_type.py,...",
                             b"text/plain")
        response_path('/a_page_that_doesnt_exist.html') -> Raises a NameError
    """
    print(filename)
    if filename is None or "." not in filename:
        return "txt", "text/plain"
    content = filename.split(".")[1]
    return content, mimetypes[content] if mimetypes[content] else "text/plain"


def server(log_buffer=sys.stderr):
    address = ('127.0.0.1', 10000)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print("making a server on {0}:{1}".format(*address), file=log_buffer)
    sock.bind(address)
    sock.listen(1)
    try:
        while True:
            print('waiting for a connection', file=log_buffer)
            conn, addr = sock.accept()
            try:
                print('connection - {0}:{1}'.format(*addr), file=log_buffer)
                request = ''
                while True:
                    data = conn.recv(1024)
                    request += data.decode('utf8')
                    if '\r\n\r\n' in request:
                        break
                print("Request received:\n{}\n\n".format(request))
                body = parse_request(request)
                content, mimetype = response_path(body)
                response = response_ok(
                    body,
                    mimetype
                )
                conn.sendall(response.encode())
            except:
                traceback.print_exc()
            finally:
                conn.close()
    except KeyboardInterrupt:
        sock.close()
        return
    except:
        traceback.print_exc()


if __name__ == '__main__':
    server()
    sys.exit(0)
