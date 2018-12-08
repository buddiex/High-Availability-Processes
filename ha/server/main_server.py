from ha.commons.server import PrimaryServer, ServerRequestHandler
import config as conf


def main(host, port):
    server = PrimaryServer(ServerRequestHandler,host, port)
    server.serve_forever()


if __name__ == '__main__':
    main(conf.SERVER_DEFAULT_HOST, conf.SERVER_DEFAULT_PORT)
