import asyncio
import functools
import json
import logging
import uuid
from collections import defaultdict
from queue import Queue
from traceback import format_exc

import jwt
import websockets
from websockets import exceptions

logger = logging.getLogger(__name__)


def wrap_socket_command(fn):
    @functools.wraps(fn)
    async def wrapped(self, *args, **kwargs):
        fn_name = fn.__name__
        hint = '%s: %s %s' % (fn_name, args, kwargs)

        if 'allow_in_connecting' in kwargs:
            allow_in_connecting = kwargs['allow_in_connecting']
            del (kwargs['allow_in_connecting'])
        else:
            allow_in_connecting = False

        logger.debug(hint)

        while True:
            await self.await_connect(hint=hint, allow_connecting=allow_in_connecting)
            try:
                return await fn(self, *args, **kwargs)
            except exceptions.InvalidState:
                logger.exception('FAILED %s ', hint)
                self.connected = False
                self.connecting = False
                self.disconnect_future.set_result(True)
                logger.info('Sleeping for 10 seconds before reconnect')
                await  asyncio.sleep(10, loop=self.loop)
            except Exception:
                logger.error('ERROR %s : %s', hint, format_exc())

    return wrapped


class Backbone(object):
    def __init__(self, api_mapping, server_address, jwt_str, api_context=None, **kwargs):
        self.api_mapping = api_mapping
        self.server_address = server_address
        self.jwt_token_str = jwt_str
        self.socket_connection = None
        self.jwt = jwt.decode(self.jwt_token_str, verify=False)
        self.sid = self.jwt.get("uid")
        self.endpoint = f'{server_address}/{self.sid}'
        self.loop = kwargs.get('loop', asyncio.get_event_loop())
        self.reconnect_sleep = kwargs.get('reconnect_sleep', 5)
        self.recv_timeout = kwargs.get('recv_timeout', 60)
        self.ping_timeout = kwargs.get('ping_timeout', 10)
        self.api_context = api_context or {}
        self.connected = False
        self.connecting = False
        self.reconnection_queue = Queue()
        self.rpc_dict = defaultdict(asyncio.Future)
        self.disconnect_future = asyncio.Future(loop=self.loop)

    async def await_connect(self, allow_connecting=False, hint=None):
        hint = hint or uuid.uuid4()
        if self.connected and self.reconnection_queue.empty():
            return
        if self.connecting and allow_connecting:
            return
        logger.debug('await_connect: %s enqueue', hint)
        reconnect_future = asyncio.Future(loop=self.loop)
        self.reconnection_queue.put(reconnect_future)
        await asyncio.sleep(0)
        await reconnect_future
        logger.debug('await_connect: %s resumed', hint)

    async def disconnection_monitor(self):
        logger.debug(f'disconnection_monitor start')
        while True:
            if self.disconnect_future is not None:
                logger.debug(f'wait for disconnect')
                await  self.disconnect_future
            logger.debug('disconnection_monitor: Connecting...')
            self.connected = False
            self.connecting = False
            self.socket_connection = await  self._connect()
            logger.debug('disconnection_monitor: _connected...')
            self.connecting = True
            self.disconnect_future = asyncio.Future(loop=self.loop)
            await self.do_task(dict(command='_on_connect'), admin=True)
            self.connected = True
            logger.debug('disconnection_monitor: _connected... queue empty? %s', self.reconnection_queue.empty())

            while not self.reconnection_queue.empty():
                future = self.reconnection_queue.get_nowait()
                future.set_result(True)

    async def _connect(self):
        logger.debug('_connect')
        while True:
            try:
                logger.info('Connect to %s', self.endpoint)
                x = await websockets.connect(self.endpoint)
                return x
            except Exception:
                logger.exception('Failed to connect to %s, will retry in %s', self.server_address, self.reconnect_sleep)
                await asyncio.sleep(self.reconnect_sleep, loop=self.loop)

    @wrap_socket_command
    async def send(self, rpc=False, **kwargs):
        call_rpc = None
        call_id = uuid.uuid4().hex
        if rpc:
            kwargs['__RPC_CALL_ID'] = call_id
            call_rpc = self._rpc_register(call_id)
        msg = json.dumps(kwargs)
        logger.debug("     > %s", msg)
        await self.socket_connection.send(msg)
        if rpc:
            return await call_rpc
        return

    def _rpc_register(self, call_id):
        return self.rpc_dict[call_id]

    @wrap_socket_command
    async def recv(self):
        msg_ = await self.socket_connection.recv()
        logger.debug("     < %s", msg_)
        return json.loads(msg_)

    def handle_rpc(self, msg):
        rpc_id = msg['__RPC_CALL_ID']
        del (msg['__RPC_CALL_ID'])
        if rpc_id in self.rpc_dict:
            future = self.rpc_dict[rpc_id]
            del (self.rpc_dict[rpc_id])
            future.set_result(msg)
        else:
            logger.warning('Got response for RPC_CALL_ID: %s but no future is present :( %s', rpc_id, msg)

    async def _read_msgs(self):
        logger.debug('_read_msgs')
        while True:
            msg = await self.recv()
            if msg.get('__RPC_CALL_ID') is not None:
                self.handle_rpc(msg)
            else:
                yield msg

    async def do_task(self, msg, admin=False):
        command = self.api_mapping.get(msg.get("command"))
        if command is None:
            logger.warning("Command not found %s", command)
            return
        data = msg.get('data')

        async def send_command(**kwargs):
            if 'allow_in_connecting' in kwargs:
                del (kwargs['allow_in_connecting'])
            return await self.send(allow_in_connecting=admin, **kwargs)

        if isinstance(data, dict):
            return await command(send_command, self.api_context, **data)
        else:
            if data is not None:
                logger.warning('No valid data in %s', json.dumps(data))
            return await command(send_command, self.api_context, **{})

    @classmethod
    def task_result(cls, msg):
        def response(future):
            try:
                resp = future.result()
                resp = resp if resp is not None else True
                if resp:
                    logger.debug('JOB: %s => %s', resp, msg)
                else:
                    logger.warning('JOB:F %s => %s', resp, msg)
            except Exception:
                logger.warning('JOB:E %s => %s', format_exc(), msg)

        return response

    async def listen_for_messages(self):
        logger.debug('listen_for_messages')
        async for msg in self._read_msgs():
            # TODO: handle tasks better... much better
            task = self.loop.create_task(self.do_task(msg))
            task.add_done_callback(self.task_result(msg))

    async def serve(self):
        logger.debug('serve')
        self.disconnect_future.set_result(True)
        logger.debug('serve: connected')
        return await asyncio.wait([self.listen_for_messages(), self.disconnection_monitor()], loop=self.loop)

    @classmethod
    def create_and_serve(cls, api_mapping, debug, api_context, loop):
        # TODO: check code climate
        ws_path = api_context.general.ws_server
        jwt_str = api_context.general.jwt
        loop.set_debug(debug)
        logging.info("Server starting")
        backbone = cls(api_mapping, ws_path, jwt_str=jwt_str, api_context=api_context, loop=loop)
        loop.run_until_complete(backbone.serve())
        return backbone
