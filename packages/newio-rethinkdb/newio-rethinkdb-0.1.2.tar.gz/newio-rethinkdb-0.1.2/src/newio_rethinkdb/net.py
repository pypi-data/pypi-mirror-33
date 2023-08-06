"""
SocketWrapper:
    - read_until
    - read_bytes
    - sendall
    - connect
    - close
    - send_query
    - read_response
Connection:
    - connect
    - run
    - use
    - close
    - _start/_continue/_stop/...
Cursor:
    - __aiter__
    - next
    - to_list
"""
import struct
import logging

from newio import socket
from newio.queue import Queue
from rethinkdb import r
from rethinkdb.net import pQuery as QueryType
from rethinkdb.net import pResponse as ResponseType
from rethinkdb.handshake import HandshakeV1_0
from rethinkdb.errors import (
    ReqlAuthError, ReqlTimeoutError, ReqlDriverError,
    ReqlServerCompileError, ReqlRuntimeError,
)
from rethinkdb.ast import DB, ReQLDecoder, ReQLEncoder, expr
from rethinkdb.ast import Insert, Update, Replace, Delete

from .errors import ReqlProgrammingError


__all__ = ('Connection', 'Cursor')

LOG = logging.getLogger(__name__)


def _get_consts(t):
    return {v: k for k, v in t.__dict__.items() if k.isupper()}


_QUERY_TYPE_NAMES = _get_consts(QueryType)
_RESPONSE_TYPE_NAMES = _get_consts(ResponseType)


def _shorten(text, width):
    if len(text) <= width:
        return text
    suffix = '(...{} hidden chars)'.format(len(text) - width)
    return text[:width] + suffix


class Query:
    def __init__(self, type, token, term, options):
        self.type = type
        self.token = token
        self.term = term
        self.options = options

    def __repr__(self):
        type_name = _QUERY_TYPE_NAMES.get(self.type, self.type)
        term = _shorten(str(self.term), width=300)
        return f'<{type(self).__name__} {self.token} {type_name}: {term}>'

    def serialize(self, json_encoder):
        message = [self.type]
        if self.term is not None:
            message.append(self.term)
        if self.options is not None:
            message.append(expr(self.options))
        query_str = json_encoder.encode(message).encode('utf-8')
        query_header = struct.pack('<QL', self.token, len(query_str))
        return query_header + query_str

    def is_writing(self):
        return isinstance(self.term, (Insert, Update, Replace, Delete))


class Response:
    def __init__(self, token, data, json_decoder):
        self.token = token
        full_response = json_decoder.decode(data.decode('utf-8'))
        self.type = full_response['t']
        self.data = full_response['r']
        self.backtrace = full_response.get('b', None)
        self.profile = full_response.get('p', None)
        self.note_type = full_response.get('n', None)

    def __repr__(self):
        type_name = _RESPONSE_TYPE_NAMES.get(self.type, self.type)
        return f'<{type(self).__name__} {self.token} {type_name}>'


class SocketWrapper:

    def __init__(self, host, port,
                 user, password, ssl,
                 json_encoder, json_decoder,
                 timeout, buffer_size=16 * 1024,
                 ):
        self.host = host
        self.port = port
        self.ssl = ssl
        self._handshake = HandshakeV1_0(
            json_decoder=json_decoder,
            json_encoder=json_encoder,
            host=host,
            port=port,
            username=user,
            password=password,
        )
        self.json_encoder = json_encoder
        self.json_decoder = json_decoder
        self.timeout = timeout
        self.buffer_size = buffer_size
        self._socket = None
        self._read_buffer = b''

    async def recv(self, maxsize):
        ret = await self._socket.recv(maxsize)
        return ret

    async def sendall(self, data):
        return await self._socket.sendall(data)

    def _consume(self, loc):
        ret = self._read_buffer[:loc]
        self._read_buffer = self._read_buffer[loc:]
        return ret

    async def read_until(self, delimiter):
        while True:
            loc = self._read_buffer.find(delimiter)
            if loc >= 0:
                return self._consume(loc + len(delimiter))
            self._read_buffer += await self.recv(self.buffer_size)

    async def read_bytes(self, num_bytes):
        while True:
            if len(self._read_buffer) >= num_bytes:
                return self._consume(num_bytes)
            self._read_buffer += await self.recv(self.buffer_size)

    async def connect(self):
        # ssl_context = ssl.create_default_context()
        # ssl_context.verify_mode = ssl.CERT_REQUIRED
        # ssl_context.check_hostname = True  # redundant with match_hostname
        # self._socket = await open_connection(self.host, self.port, ssl=ssl)
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        await self._socket.connect((self.host, self.port))
        self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        try:
            self._handshake.reset()
            response = None
            while True:
                request = self._handshake.next_message(response)
                if request is None:
                    break
                # This may happen in the `V1_0` protocol where we send two requests as
                # an optimization, then need to read each separately
                if request:
                    await self.sendall(request)
                # The response from the server is a null-terminated string
                response = (await self.read_until(b'\0'))[:-1]
        except (ReqlAuthError, ReqlTimeoutError):
            await self.close()
            raise
        except ReqlDriverError as ex:
            await self.close()
            error = str(ex)\
                .replace('receiving from', 'during handshake with')\
                .replace('sending to', 'during handshake with')
            raise ReqlDriverError(error)
        except socket.timeout as ex:
            await self.close()
            raise ReqlTimeoutError(self.host, self.port)

    def is_open(self):
        return self._socket is not None

    async def send_query(self, query):
        data = query.serialize(json_encoder=self.json_encoder)
        return await self.sendall(data)

    async def read_response(self, query):
        headers = await self.read_bytes(12)
        res_token, res_len = struct.unpack('<qL', headers)
        if res_token != query.token:
            await self.close()
            raise ReqlDriverError('Unexpected response received.')
        res_buf = await self.read_bytes(res_len)
        return Response(res_token, res_buf, json_decoder=self.json_decoder)

    async def close(self):
        if self.is_open():
            try:
                await self._socket.shutdown(socket.SHUT_RDWR)
                await self._socket.close()
            finally:
                self._socket = None


def maybe_profile(value, res):
    if res.profile is not None:
        return {'value': value, 'profile': res.profile}
    return value


class Connection:

    def __init__(self, host, port, db, auth_key, user, password,
                 timeout, ssl, _handshake_version, **kwargs):
        self.host = host
        try:
            self.port = int(port)
        except ValueError:
            raise ReqlDriverError('Could not convert port %r to an integer.' % port)
        self.db = db
        if 'json_encoder' in kwargs:
            self.json_encoder = kwargs.pop('json_encoder')
        else:
            self.json_encoder = ReQLEncoder()
        if 'json_decoder' in kwargs:
            self.json_decoder = kwargs.pop('json_decoder')
        else:
            self.json_decoder = ReQLDecoder()
        if password is None:
            password = ''
        if auth_key is not None:
            raise ReqlDriverError('`auth_key` is not supported')
        if _handshake_version != 10:
            raise ReqlDriverError('only support handshake version 1.0')
        self._socket = SocketWrapper(
            host=self.host, port=self.port, ssl=ssl, timeout=timeout,
            user=user, password=password,
            json_encoder=self.json_encoder, json_decoder=self.json_decoder,
        )
        self._next_token = 0

    def use(self, db):
        self.db = db

    def is_open(self):
        return self._socket is not None and self._socket.is_open()

    def check_open(self):
        if self._socket is None or not self._socket.is_open():
            raise ReqlDriverError('Connection is closed.')

    async def close(self):
        await self._socket.close()

    async def reconnect(self, timeout=None):
        await self.close()
        await self._socket.connect()
        return self

    def _new_token(self):
        res = self._next_token
        self._next_token += 1
        return res

    async def _run_query(self, query, noreply, raise_for_errors=True):
        query_noreply = 'noreply ' if noreply else ''
        LOG.debug(f'Send {query_noreply}query {query}')
        await self._socket.send_query(query)
        if noreply:
            return None
        res = await self._socket.read_response(query)
        LOG.debug(f'Receive response {res}')
        if res.type == ResponseType.SUCCESS_ATOM:
            data = res.data[0]
            if raise_for_errors and query.is_writing():
                if data.get('errors'):
                    raise ReqlProgrammingError(data, query.term)
            return maybe_profile(data, res)
        elif res.type in {ResponseType.SUCCESS_PARTIAL, ResponseType.SUCCESS_SEQUENCE}:
            if query.type == QueryType.CONTINUE:
                return res
            else:
                return Cursor(self, query, res)
        elif res.type == ResponseType.WAIT_COMPLETE:
            return None
        elif res.type == ResponseType.SERVER_INFO:
            return res.data[0]
        else:
            error = (res.data[0], query.term, res.backtrace)
            if res.type == ResponseType.CLIENT_ERROR:
                raise ReqlDriverError(*error)
            elif res.type == ResponseType.COMPILE_ERROR:
                raise ReqlServerCompileError(*error)
            elif res.type == ResponseType.RUNTIME_ERROR:
                raise ReqlRuntimeError(*error)
            else:
                raise ReqlDriverError(f'Unknown Response type {res.type} encountered.')

    async def _start(self, term, **options):
        self.check_open()
        if 'db' in options or self.db is not None:
            options['db'] = DB(options.get('db', self.db))
        q = Query(QueryType.START, self._new_token(), term, options)
        return await self._run_query(
            q, noreply=options.get('noreply', False),
            raise_for_errors=options.get('raise_for_errors', True))

    async def _continue(self, query):
        self.check_open()
        q = Query(QueryType.CONTINUE, query.token, None, None)
        return await self._run_query(q, False)

    async def _stop(self, query):
        self.check_open()
        q = Query(QueryType.STOP, query.token, None, None)
        return await self._run_query(q, True)

    async def noreply_wait(self):
        self.check_open()
        q = Query(QueryType.NOREPLY_WAIT, self._new_token(), None, None)
        return await self._run_query(q, False)

    async def server(self):
        self.check_open()
        q = Query(QueryType.SERVER_INFO, self._new_token(), None, None)
        return await self._run_query(q, False)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()


class Cursor:

    def __init__(self, conn, query, res):
        self._conn = conn
        self._query = query
        self._closed = False
        self._end = False
        self._has_profile = res.profile is not None
        self._feed(res)
        self._it = self._aiter()

    def _feed(self, res):
        self._items = res.data
        self._profile = res.profile
        if res.type == ResponseType.SUCCESS_SEQUENCE:
            self._end = True

    async def _aiter(self):
        while True:
            for item in self._items:
                if self._closed:
                    return
                if self._has_profile:
                    yield {'value': item, 'profile': self._profile}
                else:
                    yield item
            if self._end or self._closed:
                break
            res = await self._conn._continue(self._query)
            self._feed(res)

    async def __aiter__(self):
        async for item in self._it:
            yield item

    async def next(self):
        return await self._it.__anext__()

    async def close(self):
        await self._conn._stop(self._query)
        self._closed = True

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()

    async def to_list(self):
        ret = []
        async for x in self:
            ret.append(x)
        return ret


class ConnectionPool:
    def __init__(self, pool_size=32, *args, **kwargs):
        self.pool_size = pool_size
        self._args = args
        self._kwargs = kwargs
        self._queue = Queue(self.pool_size)
        self._current_size = 0

    async def get(self):
        if self._queue.empty() and self._current_size < self.pool_size:
            self._current_size += 1
            conn = await r.connect(*self._args, **self._kwargs)
            return conn
        else:
            return await self._queue.get()

    async def put(self, conn):
        if conn.is_open():
            await self._queue.put(conn)
        else:
            self._current_size -= 1
