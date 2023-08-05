import asyncio
import logging
import string

import docker

from controllers import InvocationDocker

logger = logging.getLogger(__name__)
printable_set = frozenset(string.printable + '\n')


class DockerExecution(object):
    async def on_log(self, x):
        if isinstance(x, bytes):
            x = x.decode('utf-8')
        filtered_string = ''.join([s for s in x if s in printable_set])
        if len(filtered_string) > 0:
            x = f"[{self.invocation_id[:5]}]\t{filtered_string}"
            logger.info(x)

        return x

    async def on_stats(self, x):

        await self.send_full_command('JOB_STATS', 1, **x)
        await self.sleep(10)

    @classmethod
    def create(cls, send, **kwargs):
        return cls(send, **kwargs)

    def __init__(self, send, active_config=None, **kwargs):
        from .api_commands import send_command

        self.send = send
        self.active_config = active_config
        self.invocation_id = kwargs['invocation_id']
        self.invocation = {}
        self.invocation.update(kwargs)
        self.container = InvocationDocker.create(**kwargs, active_config=self.active_config, log_callback=self.on_log, stats_call_back=self.on_stats)
        # hosted here for mocking
        self.sleep = asyncio.sleep
        self.send_command = send_command

    async def send_full_command(self, command_name, command_version, **kwargs):
        kwargs['invocation_id'] = self.invocation_id
        logging.debug('send_full_command(%s, %s, %s)', command_name, command_version, kwargs)
        return await self.send_command(self.send, command_name, command_version, **kwargs)

    async def run_manged(self):
        exit_code = None
        await self.send_full_command('JOB_START', 1, **self.invocation)
        try:
            exit_code = await self.container.do_run()
        except docker.errors.APIError as ex:
            logging.exception(ex)
            exit_code = ex.explanation

        finally:
            from .api_commands import send_command
            await self.send_full_command('JOB_END', 1, exit_code=exit_code)
