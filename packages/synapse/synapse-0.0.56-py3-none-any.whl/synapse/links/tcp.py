import synapse.common as s_common

import synapse.lib.socket as s_socket

from synapse.links.common import *

class TcpRelay(LinkRelay):
    '''
    Implements the TCP protocol for synapse.

    tcp://[user[:passwd]@]<host>[:port]/<path>

    '''
    proto = 'tcp'

    def _reqValidLink(self):
        host = self.link[1].get('host')
        port = self.link[1].get('port')

        if host is None:
            raise s_common.PropNotFound('host')

        if port is None:
            raise s_common.PropNotFound('port')

    def _listen(self):
        host = self.link[1].get('host')
        port = self.link[1].get('port')
        sock = s_socket.listen((host, port))
        self.link[1]['port'] = sock.getsockname()[1]
        return sock

    def _connect(self):
        try:

            host = self.link[1].get('host')
            port = self.link[1].get('port')
            return s_socket.connect((host, port))

        except s_common.sockerrs as e:
            raiseSockError(self.link, e)
