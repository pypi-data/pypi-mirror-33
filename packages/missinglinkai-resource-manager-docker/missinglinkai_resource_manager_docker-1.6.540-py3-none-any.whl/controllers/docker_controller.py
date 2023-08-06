import logging

import docker as dckr

logger = logging.getLogger(__name__)


def docker_client():
    return dckr.from_env()


ADMIN_VOLUME = {'/var/run/docker.sock': {'bind': '/var/run/docker.sock'}}
MALI_IMG = 'missinglinkai/mali:latest'


def init_from_config(conf):
    import os
    docker_socket = list(ADMIN_VOLUME.keys())[0]
    if not os.path.exists(docker_socket) and not os.environ.get('CI'):
        from click import BadParameter
        raise BadParameter('Docker host: {} must be mounted'.format(docker_socket))
