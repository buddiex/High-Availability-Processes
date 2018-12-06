from ha.commons.server import PrimaryServer, ServerRequestHandler,  ProxyRequestHandler
import ha.config as conf


def main(host, port):
    # server = PrimaryServer(ProxyRequestHandler,host, port)
    server = PrimaryServer(ServerRequestHandler,host, port)
    server.serve_forever()


if __name__ == '__main__':
    main(conf.PROXY_DEFAULT_HOST, conf.PROXY_DEFAULT_PORT)
