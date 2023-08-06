import asyncio
import datetime
import functools
import logging
import string

import aiohttp


class CloudLogger:
    printable_set = frozenset(string.printable + '\n')

    @classmethod
    def get_printable(cls, x):
        if isinstance(x, bytes):
            x = x.decode('utf-8')
        return ''.join([s for s in x if s in cls.printable_set])

    def __init__(self, endpoint, loop=None):
        self.endpoint = endpoint
        self.loop = loop or asyncio.get_event_loop()
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.tasks = {}

    def __enter__(self):
        raise TypeError("Use async with instead")

    def __exit__(self, exc_type, exc_val, exc_tb):
        # __exit__ should exist in pair with __enter__ but never executed
        pass  # pragma: no cover

    async def __aenter__(self):
        return self

    async def close(self, grace_seconds=5):
        if self.tasks:
            logging.warning('Remote logger is closing but still has %s tasks, will allow %s seconds of grace', len(self.tasks), grace_seconds)
            await asyncio.sleep(grace_seconds)
            logging.warning('Remote logger is closing and %s tasks, are still alive after the grace period', len(self.tasks))
        for task in self.tasks:
            task.cancel()

        await self.session.close()
        await  asyncio.sleep(0.25)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    def _on_done(self, log_line: str, done_task: asyncio.Task):
        try:
            result = done_task.result()
            logging.debug('%s: sent: %s', self.endpoint, log_line)
        except asyncio.CancelledError:
            logging.warning('Line %s was not sent to server, the send task was cancelled', log_line)
        except asyncio.InvalidStateError:
            logging.warning("Line %s was not sent to server, the send task hasn't started", log_line)
        except aiohttp.client_exceptions.ClientConnectorError as ex:
            logging.warning('Failed to send "%s" to ML: %s', log_line, str(ex))
        except Exception:
            logging.exception('Failed to post log line %s', log_line)
        del (self.tasks[done_task])

    async def on_log(self, line):
        printable = self.get_printable(line)
        if not printable:
            return
        task = asyncio.ensure_future(self.session.post(url=self.endpoint, json={'level': 'INFO', 'message': printable, 'category': 'CloudLogger', 'ts': datetime.datetime.utcnow().isoformat()}), loop=self.loop)
        task.add_done_callback(functools.partial(self._on_done, line))
        self.tasks[task] = True
