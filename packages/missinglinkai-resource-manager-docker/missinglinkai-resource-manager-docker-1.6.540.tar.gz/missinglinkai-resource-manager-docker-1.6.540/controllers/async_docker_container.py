import asyncio

from .docker_controller import logger
from .docker_wrapper import DockerWrapper
from .log_generator import LogGenerator
from .stat_generator import StatGenerator


class AsyncDockerContainer(object):
    @classmethod
    def get_container_env(cls, active_config):
        if active_config is None:
            return {'ML': 'True'}
        return {
            'ML': 'True',
            'ML_CLUSTER_ID': active_config.general.cluster_id,
            'ML_CLUSTER_MANAGER': active_config.general.ws_server}

    @classmethod
    def create(cls, **kwargs):
        return cls(**kwargs)

    @classmethod
    async def create_and_run(cls, **kwargs):
        run_prefix = kwargs.pop('prefix', kwargs['image'])
        return await cls.create(**kwargs).run_with_callbacks(run_prefix)

    def __init__(self, **kwargs):
        active_config = kwargs.pop('active_config', None)
        internal_env = self.get_container_env(active_config)
        env = kwargs.pop('env', {})
        env.update(internal_env)
        labels = kwargs.pop('labels', {})
        labels.update(internal_env)
        self.image = kwargs.pop('image')
        self.command = kwargs.pop('command', None)
        self.env = env
        self.volumes = kwargs.pop('volumes', None)
        self.labels = labels
        self.container = None
        self.exit = None
        self.container_id = None
        self.logs = None
        self.kill_on_exit = kwargs.pop('kill_on_exit', False)
        self.work_dir = kwargs.pop('workdir', None)
        self.runtime = None
        self.docker = kwargs.pop('docker_client', DockerWrapper.get())
        if kwargs.pop('gpu', False):
            self.runtime = 'nvidia'
        self.log_cb = self.safe_get_callback(kwargs.pop('log_callback', None))
        self.stats_cb = self.safe_get_callback(kwargs.pop('stats_call_back', None), 5)
        self.logs_task = None
        self.stats_task = None
        self.stage_name = kwargs.pop('stage_name', None)

    def __aiter__(self):
        return self

    @classmethod
    def safe_get_callback(cls, cb, empty_sleep=0):
        async def empty_func(*args, **kwargs):
            await asyncio.sleep(empty_sleep)

        return cb or empty_func

    async def __aenter__(self):
        service_data = self.docker.be_summary()
        max_memory = int(service_data['cpu']['memory'] * 0.9)
        self.container = self.docker.create_container(
            image=self.image,
            command=self.command,
            stdin_open=False,
            detach=True,
            environment=self.env,
            labels=self.labels,
            volumes=self.volumes,
            working_dir=self.work_dir,
            mem_limit=max_memory,
            runtime=self.runtime
        )
        self.container_id = self.container.name
        self.container.start()
        self.logs = LogGenerator(self.container, self.stage_name)
        self.stats_generator = StatGenerator(self.container)

        return self

    def remove_and_cleanup_container(self):
        container_volumes = self.container.attrs.get('Mounts', [])
        self.container.remove()
        for cont_volume in container_volumes:
            if 'Name' not in cont_volume:
                logger.info('remove_and_cleanup_container: Skipping %s ', cont_volume)
                continue

            name = cont_volume['Name']
            if name not in self.volumes:
                volume_obj = self.docker.volume(name)
                if volume_obj is not None:
                    volume_obj.remove()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.container is None:
            logger.error(f'Failed to obtain container status for {self.container_id}, container not found')
            return
        is_cancelled = exc_type is not None and exc_type is asyncio.CancelledError
        if is_cancelled:
            exc_type = None

        logger.debug(f"{self.container_id}:  __aexit__ state {self.container_id}: {self.container.status}")
        self.exit_container(force_cancel=is_cancelled)

        if self.exit is not None:
            self.remove_and_cleanup_container()
        else:
            logger.warning(f"{self.container_id}:  __aexit__ container still {self.container_id}: {self.container.status}")
        await asyncio.sleep(0)
        return exc_type is None

    def exit_container(self, force_cancel=False):
        self.container.reload()
        if self.container.status == 'running' and (force_cancel or self.kill_on_exit):
            logger.debug('%s: DOCKER: execution cancelled', self.container.name)
            self.container.kill()
            self.container.reload()
        if self.container.status != 'running':
            self.exit = (self.container.status, self.container.wait())

        self._cancel_futures(self.logs_task, self.stats_task)

    @classmethod
    def _cancel_futures(cls, *args):
        for future in args:
            if future:
                future.cancel()

    async def run_with_callbacks(self, prefix):

        async with self as context:
            logger.debug('%s: DOCKER: run %s', self.container.name, prefix)

            async def _do_logs():
                async for line in context.logs:
                    await  asyncio.sleep(0)
                    await  context.log_cb(line[1], step_name=line[0])

            async def _do_stats():
                async for x in context.stats_generator:
                    await  asyncio.sleep(0)
                    await context.stats_cb(x)

            self.logs_task = asyncio.ensure_future(_do_logs())
            self.stats_task = asyncio.ensure_future(_do_stats())
            await  asyncio.wait([self.logs_task, self.stats_task])
            self.container.reload()
            logger.debug('%s: DOCKER: DONE %s', self.container.name, self.container.status)

        return self
