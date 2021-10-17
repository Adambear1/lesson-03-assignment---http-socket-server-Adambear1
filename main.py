import socket
import sys
import traceback
import os
import mimetypes

class HttpServer():

    def __init__(self, port):
        self.port = port

    def serve(self):
        address = ('127.0.0.1', port)

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        print("Server hosted on http://{}:{}".format(*address))

        sock.bind(address)
        sock.listen(10)

        try:
            while True:
                print("Waiting for a connection...")
                conn, addr = sock.accept()
                try:
                    print("Connection Made: {}:{}".format(*addr))
                    request = ''
                    while True:
                        data = conn.recv(1024)
                        request += data.decode()
                        if "/r/n/r/n" in request:
                            break
                        path = self.get_path(request)
                        try:
                            body = self.get_content(path)
                            mimetype = self.get_mimetype(path)
                            response = self.make_response(
                                b"200",
                                b"OK",
                                body,
                                mimetype
                            )
                            conn.sendall(response.encode())
                        finally:
                            conn.close()
                            return
                except KeyboardInterrupt:
                    sys.exit(1)
                except Exception:
                    traceback.print_exc()
                finally:
                    conn.close()
                    return True
        except KeyboardInterrupt:
            sys.exit(1)
            return True
        except Exception:
            traceback.print_exc()
        finally:
            sock.close()

    def get_path(self, req):
        '''
        Method to receive header and parse values into list
        '''
        return req.split("\r\n")

    def get_filename(self, req):
        return req[0].split(" /")[1].split(" ")[0]

    def get_content(self, req):
        try:
            if type(req) is list:
                if os.path.isfile(self.get_filename(req)):
                    return "File '{}' found!".format(self.get_filename(req))
                raise FileNotFoundError 
            raise SystemError
        except FileNotFoundError:
            body = b"Couldn't find the file requested."
            mimetype = b"text/plain"
            response = self.make_response(
                b"404",
                b"OK",
                body,
                mimetpye
            )
            conn.sendall(response.encode())
        except SystemError:
            body = b"System error, please try again."
            mimetype = b"text/plain"
            response = self.make_response(
                b"500",
                b"OK",
                body,
                mimetype
            )
            conn.sendall(response.encode())


    def get_mimetype(self, req):
        if type(req) is list:
            return mimetypes.MimeTypes().guess_type(self.get_filename(req))[0]
        return SystemError

    def make_response(self, status, code, body, mimetype):
        response = ''
        response += "HTTP/1.1 {} {}\r\n".format(status, code)
        response += "Content-Type: {}\r\n".format(mimetype)
        response += "\r\n"
        response += "{}".format(body)
        return response

if __name__ == "__main__":
    try:
        port = int(sys.argv[1])
    except IndexError:
        port = 10000

    server = HttpServer(port)
    server.serve()
