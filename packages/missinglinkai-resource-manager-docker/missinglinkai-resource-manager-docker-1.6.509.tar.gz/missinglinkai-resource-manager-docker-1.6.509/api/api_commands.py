import asyncio
import functools
import json
import logging

from controllers import DockerWrapper

logger = logging.getLogger(__name__)


class CommandResponseError(Exception):
    def __init__(self, command, response):
        self.command = command
        self.response = response


async def send_command(send, command_name, command_version, **kwargs):
    await send(command=f"{command_name}:{command_version}", data=kwargs)


async def register_1(send, api_context, **kwargs):
    data = DockerWrapper.get().be_summary()
    data["gpu_present"] = DockerWrapper.get().has_nvidia()
    response = await send(command="REGISTER:1", jwt=api_context.general.jwt, data=data, rpc=True)

    if response.get('ok', False):
        logger.info("Connected")
        return True
    raise CommandResponseError("register_1", response)


running_tasks = {}


def remove_completed_task(t_id, task):
    res = running_tasks.pop(t_id, None)
    if res is not None:
        print(f'invocation Id {t_id} completed')


async def kill_1(send, api_context, **kwargs):
    invocation_id = kwargs['invocation_id']
    task = running_tasks.pop(invocation_id, None)
    logger.info(f'Killing {invocation_id}: {task}')
    if task is None:
        return

    task.cancel()


async def running_1(send, api_context, **kwargs):
    tasks = dict(running_tasks)
    return {'ok': tasks}


async def run_1(send, api_context, **kwargs):
    from .docker_execution import DockerExecution
    logger.info('RUN_1: %s', json.dumps(kwargs))
    kwargs['active_config'] = api_context
    invocation_id = kwargs['invocation_id']

    task = asyncio.ensure_future(DockerExecution.create(send, **kwargs).run_manged())
    task.add_done_callback(functools.partial(remove_completed_task, invocation_id))
    logger.info(f'{invocation_id} is now running')
    running_tasks[invocation_id] = task
    return {'ok': True, 'invocation_id': invocation_id}


async def echo_1(send, api_context, **kwargs):
    logger.info('echo_1: %s', json.dumps(kwargs))
    return kwargs


async def on_connect(send, api_context, **kwargs):
    logger.debug('on_connect %s %s', api_context, kwargs)
    await send(jwt=api_context.general.jwt)


API_MAPPING = {
    'REGISTER:1': register_1,
    'RUN:1': run_1,
    'KILL:1': kill_1,
    '_on_connect': on_connect
}
