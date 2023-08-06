from rethinkdb import *  # noqa
from .net import Connection, ConnectionPool  # noqa


def set_loop_type():
    import rethinkdb.net
    rethinkdb.net.connection_type = Connection
