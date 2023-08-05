import stat
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
import os
import logging
import asyncio
from .config import init_cluster
import click
from controllers.configuration import get_active_config
from controllers.transport import Backbone
from api import API_MAPPING
from pkg_resources import DistributionNotFound, get_distribution


class CliTools:
    @classmethod
    def load_config(cls, loop=None):
        conf_path = os.environ.get('MLADMIN_CONF_DIR', os.path.expanduser('~/.config'))
        debug = os.environ.get('MLADMIN_DEBUG') is not None
        loop = loop or asyncio.get_event_loop()
        loop.run_until_complete(init_cluster(config_folder=conf_path))
        return conf_path, debug, loop

    @classmethod
    def is_in_container(cls):
        return os.environ.get("ML_RM_MANAGER") == '1'

    @classmethod
    def get_keys_pem_from_ssh_key_data(cls, ssh_key_data):
        private_key = serialization.load_pem_private_key(ssh_key_data, password=None, backend=default_backend())
        pk_pem = private_key.private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.TraditionalOpenSSL, encryption_algorithm=serialization.NoEncryption())
        pub_pem = private_key.public_key().public_bytes(encoding=serialization.Encoding.OpenSSH, format=serialization.PublicFormat.OpenSSH)
        return pk_pem, pub_pem

    @classmethod
    def save_ssh_key(cls, ssh_key_data):
        if not CliTools.is_in_container():
            raise click.BadOptionUsage("SSH key configuration is only available inside docker environments")
        conf_path, debug, loop = CliTools.load_config()
        if not isinstance(ssh_key_data, bytes):
            ssh_key_data = ssh_key_data.encode('utf-8')
        # TODO: do stuff with passwords here...
        ssh_path = os.path.join(conf_path, '.ssh')
        os.makedirs(ssh_path, exist_ok=True)

        ssh_conf_path = os.path.join(conf_path, '.ssh', 'config')
        with open(ssh_conf_path, 'w') as f:
            f.writelines(['Host *\n', "   StrictHostKeyChecking=no\n", "   IdentityFile=/root/.ssh/id_rsa\n"])

        pk_pem, pub_pem = cls.get_keys_pem_from_ssh_key_data(ssh_key_data)
        private_key_path = os.path.join(ssh_path, 'id_rsa')
        public_key_path = os.path.join(ssh_path, 'id_rsa.pub')
        with open(private_key_path, 'wb') as f:
            f.write(pk_pem)
            logging.info("Private key is set up: %s", private_key_path)
        os.chmod(private_key_path, stat.S_IRUSR | stat.S_IWUSR)
        with open(public_key_path, 'wb') as f:
            f.write(pub_pem)
            logging.info("Public key is set up: %s", private_key_path)
        get_active_config().general.save()

    @classmethod
    def run_ws(cls, loop=None):
        conf_path, debug, loop = cls.load_config(loop)
        active_config = get_active_config()
        return Backbone.create_and_serve(API_MAPPING, debug, active_config, loop)

    @classmethod
    def get_version(cls, package='missinglinkai-resource-manager-docker'):
        try:
            dist = get_distribution(package)
        except DistributionNotFound:
            return None

        return str(dist.version)

    @classmethod
    def save_mali_config(cls, config_prefix, config_data):
        import base64
        conf_path, debug, loop = cls.load_config()

        mali_path = os.path.join(conf_path, '.MissingLinkAI')
        os.makedirs(mali_path, exist_ok=True)
        filename = 'missinglink.cfg'
        if config_prefix is not None and len(config_prefix) > 0:
            filename = f"{config_prefix}-{filename}"

        with open(os.path.join(mali_path, filename), 'wb') as f:
            f.write(base64.decodebytes(config_data))
            print(f"file: ")
