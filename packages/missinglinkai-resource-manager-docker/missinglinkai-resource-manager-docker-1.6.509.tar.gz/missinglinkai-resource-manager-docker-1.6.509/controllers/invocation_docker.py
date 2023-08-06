import asyncio
import logging
import os
import re
import uuid

from docker.errors import APIError

from controllers.async_docker_container import AsyncDockerContainer
from controllers.docker_controller import MALI_IMG, logger, ADMIN_VOLUME
from controllers.docker_wrapper import DockerWrapper
from controllers.errors import PrepareDockerEnvironmentException
from .transport.ecr import Ecr


class InvocationDocker:
    git_clone_image = 'missinglinkai/git-lfs:latest'

    def get_or_create_volume(self, name, labels=None):
        cur_volume = self.docker_wrapper.volume(name)
        if cur_volume:
            return cur_volume
        labels = labels or {}
        labels.update(AsyncDockerContainer.get_container_env(self.active_config))

        return self.docker_wrapper.create_volume(name, labels=labels)

    async def run_with_callbacks_and_validate_result(self, name, **kwargs):
        execution_kwargs = dict(self.init_kwargs)
        execution_kwargs.update(kwargs)
        try:
            container = await  AsyncDockerContainer.create_and_run(**execution_kwargs)
            return await self.validate_exit_state(name, container.exit)
        except APIError as ex:
            logging.exception(ex)
            return ex.explanation, -500

    async def validate_exit_state(self, step_name, exit_state):
        logger.debug('validate_exit_state: %s = %s', step_name, exit_state)
        exit_result = exit_state[1]
        if isinstance(exit_result, dict) and 'StatusCode' in exit_result:
            exit_state = [exit_state[0], exit_result['StatusCode'], exit_result.get('Error')]
        elif not isinstance(exit_result, int):
            raise ValueError(f'Unknown exit_state: {exit_state} in {step_name}')
        if exit_state[1] != 0:
            self.errors.append((step_name, exit_state))
            raise PrepareDockerEnvironmentException('Failed in step %s: %s' % (step_name, exit_state))
        else:
            await self.log_cb(f'{step_name} ... Done {exit_state}')
            return exit_state

    ecr_repo_re = r"(.*)\.dkr\.ecr\.(.*)\.amazonaws\.com/(.*)"

    async def try_ecr_image_auth_if_needed(self, image, volumes):
        aws_repo = re.match(self.ecr_repo_re, image)

        if not aws_repo:
            return

        account, region, actual_image = aws_repo.groups()
        user, password, endpoint = Ecr.login(account, region, actual_image)

        if user is password is None:
            return

        await self.run_with_callbacks_and_validate_result(
            name=f'docker Login to: `{endpoint}`',
            image="docker",
            command=f"docker login -u {user} -p {password} {endpoint}",
            volumes=volumes,
        )
        return

    async def pull_image(self, image, force=False):
        if not force and self.docker_wrapper.image(image):
            await self.log_cb(f'Skipping pull of {image}, already present')
            return

        volumes = dict(ADMIN_VOLUME)
        volumes[os.environ['ML_CONFIG_VOLUME']] = {'bind': "/root"}

        await self.try_ecr_image_auth_if_needed(image, volumes)
        await self.log_cb(f'Pulling Image {image} ... ')

        return await self.run_with_callbacks_and_validate_result(
            name=f'Pull Image: `{image}`',
            image="docker",
            command=f"docker pull {image}",
            volumes=volumes,
        )

    def _skip_data_clone(self):
        if self.data_query is None or self.data_volume is None:
            return True

        if self.data_use_iterator:
            return True

        return False

    async def clone_data(self):
        if self._skip_data_clone():
            await self.log_cb(f'Skipping data clone')
            return None

        mount_path, volume_id = self.build_artifact_volume('/data', {'volume': self.data_volume, 'query': self.data_query})
        data_mount = {volume_id: {'bind': '/data'}}
        return await self.run_mali_command(data_mount, 'data', 'clone', str(self.data_volume), '--query', self.data_query, '--destFolder', self.data_dest_folder)

    async def run_mali_command(self, mounts, *args, update_mali=True):
        args = [str(x) for x in args]
        logger.info(f"Run mali command {args}")
        await self.pull_image(MALI_IMG, update_mali)

        mounts[os.environ['ML_CONFIG_VOLUME']] = {'bind': "/root"}
        exec_args = ['python', 'mali.py']

        if self.active_config.general.mali_prefix is not None:
            exec_args.append('-cp')
            exec_args.append(self.active_config.general.mali_prefix)

        logger.info(f"Run mali command {args}: %s", mounts)
        return await  self.run_with_callbacks_and_validate_result(
            f'mali_command: {args}',
            image=MALI_IMG,
            command=exec_args + list(args),
            volumes=mounts,
        )

    @classmethod
    def create(cls, **kwargs):
        return cls(**kwargs)

    def __init__(self, **kwargs):
        # Required params
        self.invocation_id = kwargs.pop('invocation_id')
        self.docker_wrapper = kwargs.pop('docker_wrapper', DockerWrapper.get())
        self.active_config = kwargs.pop('active_config')
        self.project_id = str(kwargs.pop('project_id', self.invocation_id))
        # CACHE
        self.cache_volume_name = f"{os.environ['ML_CONFIG_VOLUME']}_cache"
        self.get_or_create_volume(self.cache_volume_name)

        self.env = kwargs.pop('env', {})
        self.env.update(self._get_env())
        if self.active_config.general.mali_prefix is not None:
            self.env['ML_CONFIG_PREFIX'] = self.active_config.general.mali_prefix

        self.git_repo = kwargs.pop('git_repo', None)
        self.git_tag = kwargs.pop('git_tag', 'master')
        self.data_volume = kwargs.pop('data_volume', None)
        self.data_query = kwargs.pop('data_query', None)
        self.data_use_iterator = kwargs.pop('data_use_iterator', False)
        self.data_dest_folder = kwargs.pop('data_dest_folder', '/data')
        self.log_cb = kwargs.pop('log_callback')
        self.labels = kwargs.pop('labels', {})
        self.volumes = kwargs.pop('volumes', {})
        if self.data_volume is not None:
            self.env['ML_DATA_VOLUME'] = self.data_volume
            self.env['ML_DATA_QUERY'] = self.data_query
            self.env['ML_DATA_USE_ITERATOR'] = self.data_use_iterator
            self.env['ML_DATA_DEST'] = self.data_dest_folder

        self.persistent_paths = {}
        for container_path, host_path in kwargs.pop('persistent_paths', {}).items():
            bind_name, src_path = self._bind_volume(src_path=host_path, bind_path=container_path)
            self.persistent_paths[src_path] = bind_name

        self.output_paths = self.build_artifact_volumes(kwargs.pop('output_paths', []))
        self.output_data_volume = kwargs.pop('output_data_volume', None)

        if self.output_data_volume is not None:
            self.env['ML_OUTPUT_DATA_VOLUME'] = self.output_data_volume
        # result placeholders
        self.errors = []
        self.stages_results = {}
        self.init_kwargs = kwargs

        # params for containers
        self.init_kwargs['log_callback'] = self.log_cb
        self.init_kwargs['active_config'] = self.active_config

    def build_artifact_volume(self, volume, volume_labels=None):
        volume = volume if not volume.startswith('/') else volume[1:]
        volume_name = self._get_artifact_name(volume)
        volume_labels = volume_labels or {}
        volume_labels['path'] = volume
        volume_obj = self.get_or_create_volume(volume_name, volume_labels)
        return self._bind_volume(src_path=volume_obj.id, bind_path=volume)

    def build_artifact_volumes(self, volumes):
        return [self.build_artifact_volume(volume) for volume in volumes]

    def _bind_volume(self, src_path, bind_path):
        bind_path = bind_path if bind_path[0] == '/' else '/%s' % bind_path
        bind_name = bind_path[1:]
        logger.debug("Path %s will be handled by %s", bind_path, src_path)

        self.env[f"ML_MOUNT_{bind_name}"] = src_path
        self.labels[f"ML_MOUNT_{bind_name}"] = src_path

        self.volumes.update({src_path: {'bind': bind_path}})
        return bind_name, src_path

    def _get_artifact_name(self, path):
        import re
        attempt_id = uuid.uuid4().hex[:3]
        return f"{self.invocation_id[:5]}_{attempt_id}___{re.sub(r'[^a-zA-Z0-9_.-]', '_', path)}"

    def _get_env(self):
        return {'ML_INVOCATION_ID': self.invocation_id, 'ML_PROJECT_ID': self.project_id}

    async def pull_code(self):
        if self.git_repo is None:
            await self.log_cb('No git data provided. Skipping creation /code folder')
            return None

        await self.pull_image(self.git_clone_image)

        code_mount = self.build_artifact_volume('/code')
        mounts = {
            code_mount[1]: {'bind': "/code"},
            os.environ['ML_CONFIG_VOLUME']: {'bind': "/root"}
        }

        return await  self.run_with_callbacks_and_validate_result(
            name='Pulling Code',
            image=self.git_clone_image,
            command=f"clone {self.git_repo} -b {self.git_tag or 'master'} -v --depth=1 /code --recurse-submodules -j8",
            volumes=mounts)

    async def _clean_up_output_paths(self):
        for name, volume in self.output_paths:
            volume_obj = self.docker_wrapper.volume(volume)
            if volume_obj is not None:
                await self.log_cb(f'Removing  volume {name}')
                volume_obj.remove()

    async def export_output_paths(self):
        if len(self.output_paths) == 0:
            return 'No export paths present', 0
        if self.output_data_volume is None:
            logger.error("Can't export output_path %s - there is not output data volume configured for your organization", [x[0] for x in self.output_paths])
            return 'No export Data Volume configured for this org', 0

        export_root_path = f"/export/{self.project_id}/{self.invocation_id}"
        mounts = {}
        for name, volume in self.output_paths:
            mounts[volume] = {'bind': f'{export_root_path}{name}'}
        await self.run_mali_command(
            mounts, 'data', 'setMetadata', '--dataPath', '/export',
            '--metadata-string', 'project_id', self.project_id,
            '--metadata-string', 'invocation_id', self.invocation_id)
        sync_res = await self.run_mali_command(
            mounts, 'data', 'sync', self.output_data_volume,
            '--no_progressbar', '--dataPath', '/export', '--isolated',
            '--commit', f'Project ID: {self.project_id} Invocation: {self.invocation_id}',
            update_mali=False)
        await self._clean_up_output_paths()
        return sync_res

    async def cleanup_volumes(self):
        if not self.volumes:
            return

        for name, _ in self.volumes.items():
            if name in self.persistent_paths:
                await self.log_cb(f'cleanup_volumes: skipping persistent volume `{name}`. ')
                continue

            volume_obj = self.docker_wrapper.volume(name)
            if volume_obj is not None:
                await self.log_cb(f'Removing  volume {name}')
                volume_obj.remove()
        return 'Done', 0

    async def run_container(self):
        await self.log_cb(f'Running submitted code')
        mounts = dict(self.volumes)
        mounts[os.environ['ML_CONFIG_VOLUME']] = {'bind': "/root"}
        mounts[self.cache_volume_name] = {'bind': "/cache"}
        self.env['ML_CACHE_FOLDER'] = '/cache'
        logger.debug('volumes: %s', mounts)

        return await self.run_with_callbacks_and_validate_result(
            'Run Code',
            volumes=mounts,
            labels=self.labels,
            workdir='/code',
            env=self.env

        )

    async def await_stage_tasks(self, stage_name, *args):
        await self.log_cb(f'{stage_name}: Running')
        res = []
        errors = []
        try:
            tasks = [asyncio.ensure_future(x) for x in args]
            done_tasks, pending_tasks = await asyncio.wait(tasks)
            for result in done_tasks:
                if result.exception() is not None:
                    errors.append(str(result.exception()))
                else:
                    execution_result = result.result() or ('Skipped', 0)
                    exit_state = execution_result[0]
                    exit_code = execution_result[1]
                    if exit_code == 0:
                        res.append(exit_state)
                    else:
                        errors.append(exit_state)
        except asyncio.CancelledError:
            await  self.log_cb(f'Execution cancelled at {stage_name}')
            if tasks:
                for task in tasks:
                    task.cancel()
            return f'Execution cancelled at {stage_name}', 137
        if errors:
            return_res = '\n'.join([f'{stage_name} failed:'] + errors), -100
        else:
            return_res = '\n'.join([f'{stage_name} completed:'] + res), 0
        await self.log_cb(f'{stage_name} completed: {return_res}')
        return return_res

    async def prepare_env(self):
        pull_code_task = self.pull_code()
        pull_image_task = self.pull_image(self.init_kwargs['image'], force=False)
        mali_clone_data_task = self.clone_data()
        return await self.await_stage_tasks('Preparing Environment', pull_code_task, pull_image_task, mali_clone_data_task)

    async def finalize_env(self):
        await self.await_stage_tasks('Finalizing Environment', self.export_output_paths())

    async def clean_up_env(self):
        return await self.await_stage_tasks('Cleanup Environment', self.cleanup_volumes())

    async def _try_stage(self, stage_name, stage):
        try:
            stage_res = await stage()
            return stage_res
        except PrepareDockerEnvironmentException as ex:
            await  self.log_cb(f'Failed to {stage_name}: {str(ex)}')
            stage_res = 'Failed: \n' + '\n'.join([x[0] for x in self.errors]), -200

        self.stages_results[stage_name] = stage_res
        return stage_res

    async def do_run(self):
        prepare_env_task = self._try_stage('prepare_env', self.prepare_env)
        finalize_env_task = self._try_stage('finalize_env', self.finalize_env)
        clean_up_env = self._try_stage('clean_up_env', self.clean_up_env)

        result = await  prepare_env_task
        if result[1] == 0:
            result = await self._try_stage('execute_code', self.run_container)

        await finalize_env_task
        await clean_up_env

        exit_code = 0 if result[1] == 0 else result[0]
        await self.log_cb(f'Invocation {self.invocation_id} completed with state: {result}.')
        return exit_code
