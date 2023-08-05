import tornado.ioloop
import tornado.web
import json
import webbrowser
import socket

from .config import set_token, DEFAULT_CONFIG

token = None


class TokenHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "*")
        self.set_header('Access-Control-Allow-Methods', 'POST, OPTIONS')

    def post(self):
        global token
        data = json.loads(self.request.body)
        token = data['token']
        self.write('OK')
        tornado.ioloop.IOLoop.current().stop()

    def options(self):
        self.set_status(204)
        self.finish()


def token_server():
    global token
    app = tornado.web.Application([(r"/token", TokenHandler)])
    port = choose_port()
    server = app.listen(port)
    webbrowser.open_new('https://vlab.jumper.io/cli_login/{}'.format(port))
    tornado.ioloop.IOLoop.current().start()
    server.stop()
    return token


def choose_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    addr, port = s.getsockname()
    s.close()
    return port


def login():
    token = token_server()
    set_token(token)
    print("Token has been saved to {}".format(DEFAULT_CONFIG))
    print("Login successful")
    return token


if __name__ == "__main__":
    print(token_server())
